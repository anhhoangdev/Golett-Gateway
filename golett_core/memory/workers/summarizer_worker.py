"""
Content-aware background worker that summarizes memory buffers when triggered
by importance/topic rather than just time intervals.

Works with the new GolettMemoryCore to process accumulated memory items
when they reach significance thresholds.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

import openai

from golett_core.schemas.memory import MemoryItem, MemoryType, MemoryRing
from golett_core.interfaces import MemoryStorageInterface


class SummarizerWorker:
    """
    Content-driven summarization worker.
    
    Instead of running on fixed time intervals, this worker is triggered
    by the MemoryProcessor when buffers reach significance thresholds.
    """

    def __init__(
        self,
        storage: MemoryStorageInterface,
        model: str = "gpt-3.5-turbo-0125",
    ) -> None:
        self.storage = storage
        self.model = model

    async def summarize_items(self, items: List[MemoryItem]) -> MemoryItem:
        """
        Summarize a buffer of related memory items into a single summary.
        
        This is called by GolettMemoryCore when a topic buffer reaches
        the summarization threshold.
        """
        if not items:
            raise ValueError("Cannot summarize empty item list")

        # Get session info from first item
        session_id = items[0].session_id
        topic = items[0].metadata.get("topic", "general")
        
        # Build context from all items
        context_parts = []
        for item in items:
            role = "user" if item.metadata.get("role") == "user" else "assistant"
            context_parts.append(f"{role}: {item.content}")
        
        context = "\n".join(context_parts)
        
        # Generate summary
        summary_text = await self._generate_summary(context, topic)
        
        # Create summary memory item
        summary_item = MemoryItem(
            id=uuid4(),
            session_id=session_id,
            type=MemoryType.SUMMARY,
            content=summary_text,
            created_at=datetime.utcnow(),
            importance=max(item.importance for item in items),  # Use highest importance
            ring=MemoryRing.SHORT_TERM,
            metadata={
                "topic": topic,
                "source": "SummarizerWorker", 
                "item_count": len(items),
                "time_span": f"{items[0].created_at.isoformat()} to {items[-1].created_at.isoformat()}"
            }
        )
        
        # Store the summary
        await self.storage.store_memory_item(summary_item)
        
        return summary_item
    
    async def _generate_summary(self, context: str, topic: str) -> str:
        """Generate a concise summary using OpenAI."""
        prompt = f"""Summarize this conversation about {topic} in ≤150 words. Focus on:
- Key facts and decisions
- Important preferences or goals
- Actionable outcomes

Conversation:
{context}

Summary:"""

        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1,
        )
        
        return response.choices[0].message.content.strip()

    # Legacy method for backwards compatibility
    async def run_forever(
        self, 
        session_id: UUID, 
        interval_seconds: int = 300
    ) -> None:
        """
        DEPRECATED: Time-based summarization loop.
        
        This is kept for backwards compatibility but the new approach
        uses content-driven triggers via GolettMemoryCore.
        """
        while True:
            try:
                await self._summarise_session_legacy(session_id)
            except Exception as e:
                print(f"Summarization error for session {session_id}: {e}")
            
            await asyncio.sleep(interval_seconds)
    
    async def _summarise_session_legacy(self, session_id: UUID) -> None:
        """Legacy implementation - kept for backwards compatibility."""
        # This would need access to the old DAOs to work
        # For now, it's a no-op since we're moving to the new architecture
        pass 