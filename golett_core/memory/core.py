"""
Unified Memory Core for Golett.

This module consolidates all memory functionality into a clean, layered architecture:
- Storage layer: handles persistence (relational + vector)
- Processing layer: handles tagging, summarization, retrieval  
- Interface layer: provides unified API for memory operations

Replaces the scattered engine.py, interfaces.py, and crew_integration approach.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from golett_core.schemas.memory import (
    MemoryItem,
    ChatMessage,
    ChatRole,
    ContextBundle,
    MemoryType,
)
from golett_core.interfaces import TaggerInterface, MemoryStorageInterface
from golett_core.memory.processing.tagger import AutoTagger


class MemoryProcessor:
    """Handles tagging, importance scoring, and summarization triggers."""
    
    def __init__(self, tagger: TaggerInterface = None):
        self.tagger = tagger or AutoTagger()
        self._buffers: Dict[tuple[UUID, str], List[MemoryItem]] = {}
        self.importance_threshold = 0.35
        self.buffer_size_limit = 20
    
    async def process_message(self, message: ChatMessage) -> MemoryItem:
        """Tag and score a message, return MemoryItem ready for storage."""
        tags = await self.tagger.tag(message)
        item = MemoryItem.from_chat_message(message)
        item.metadata.update(tags)
        item.importance = float(tags.get("importance", 0.3))
        return item
    
    async def should_summarize(self, session_id: UUID, topic: str) -> bool:
        """Check if accumulated items warrant summarization."""
        buffer_key = (session_id, topic)
        buffer = self._buffers.get(buffer_key, [])
        
        # Trigger conditions
        if len(buffer) >= self.buffer_size_limit:
            return True
        
        high_importance_count = sum(1 for item in buffer 
                                  if item.importance >= self.importance_threshold)
        return high_importance_count >= 5
    
    def add_to_buffer(self, item: MemoryItem) -> None:
        """Add item to summarization buffer."""
        if item.session_id is None:
            return
            
        topic = item.metadata.get("topic", "general")
        buffer_key = (item.session_id, topic)
        
        if buffer_key not in self._buffers:
            self._buffers[buffer_key] = []
        
        self._buffers[buffer_key].append(item)
    
    def get_buffer(self, session_id: UUID, topic: str) -> List[MemoryItem]:
        """Get and clear buffer for summarization."""
        buffer_key = (session_id, topic)
        buffer = self._buffers.get(buffer_key, [])
        if buffer:
            del self._buffers[buffer_key]
        return buffer


# -----------------------------------------------------------------------------
# Unified Memory Manager (main public API)
# -----------------------------------------------------------------------------

class GolettMemoryCore:
    """
    Main memory interface that replaces GolettMemory, ContextForge, etc.
    
    Provides a clean API for:
    - Storing messages with automatic processing
    - Triggering summarization when needed
    - Building context for agent queries
    """
    
    def __init__(
        self,
        storage: MemoryStorageInterface,
        processor: MemoryProcessor | None = None,
        summarizer=None,  # SummarizerWorker
        graph_worker=None,  # GraphWorker
        context_forge=None,  # Optional advanced retriever
        *,
        bus=None,  # EventBus, kept optional to avoid breaking callers
    ):
        self.storage = storage
        self.processor = processor or MemoryProcessor()
        self.summarizer = summarizer
        self.graph_worker = graph_worker
        self.context_forge = context_forge  # may be None for legacy search
        self.bus = bus
    
    async def save_message(self, message: ChatMessage) -> None:
        """Store a message with automatic tagging and summarization triggering."""
        # 1. Process and tag the message
        item = await self.processor.process_message(message)
        
        # 2. Store it
        await self.storage.store_memory_item(item)
        
        # 2b. Publish MemoryWritten event so reactive workers fire immediately
        if self.bus is not None:
            try:
                from golett_core.events import MemoryWritten

                await self.bus.publish(
                    MemoryWritten(
                        session_id=message.session_id,
                        memory_id=str(item.id),
                        type=item.type.value,
                    )
                )
            except Exception as exc:  # pragma: no cover – event bus optional
                print(f"[MemoryCore] failed to publish MemoryWritten: {exc}")
        
        # 3a. Persist graph entities / relations (fire-and-forget)
        if self.graph_worker and (
            item.metadata.get("entities") or item.metadata.get("relations")
        ):
            # Run without blocking the main path – graph writes are non-critical
            asyncio.create_task(self.graph_worker.process_item(item))

        # 3b. Add to summarization buffer
        self.processor.add_to_buffer(item)
        
        # 4. Check if we should summarize
        topic = item.metadata.get("topic", "general")
        if await self.processor.should_summarize(message.session_id, topic):
            await self._trigger_summarization(message.session_id, topic)
    
    async def search(
        self, 
        session_id: UUID, 
        query: str,
        intent: str = "analytical",
        include_recent: bool = True
    ) -> ContextBundle:
        """Build complete context for agent response."""
        # Fast path: if a modern ContextForge instance is available, delegate.
        if self.context_forge is not None:
            msg = ChatMessage(session_id=session_id, role=ChatRole.USER, content=query)
            return await self.context_forge.build_bundle(msg, intent=intent)

        # --------------------------------------------------------------
        # Legacy simple retrieval fallback (no graph / re-ranker)
        # --------------------------------------------------------------

        tasks = []
        
        # Get recent messages
        if include_recent:
            tasks.append(self.storage.get_recent_messages(session_id, 10))
        
        # Semantic search across all memory types
        tasks.append(self.storage.search_memories(session_id, query, limit=15))
        
        if include_recent:
            recent_msgs, semantic_items = await asyncio.gather(*tasks)
        else:
            recent_msgs = []
            semantic_items = await tasks[0]
        
        return ContextBundle(
            session_id=session_id,
            current_turn=ChatMessage(session_id=session_id, content=query),
            recent_history=recent_msgs,
            retrieved_memories=semantic_items,
            related_graph_entities=[],  # TODO: implement if needed
        )
    
    async def _trigger_summarization(self, session_id: UUID, topic: str) -> None:
        """Trigger background summarization for a topic."""
        if not self.summarizer:
            return
            
        buffer = self.processor.get_buffer(session_id, topic)
        if buffer:
            # Delegate to summarizer worker
            await self.summarizer.summarize_items(buffer) 