"""Data Access Object for relational memory store.

All DB/ORM specifics are intended to be handled by the injected `store`,
so that higher-level services remain database-agnostic.
"""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from golett_core.schemas import (
    Document,
    Session,
    ChatMessage,
)
from golett_core.schemas.memory import MemoryItem, MemoryRing
from golett_core.interfaces import MemoryStoreInterface, TaggerInterface
from golett_core.memory.processing.tagger import AutoTagger


class MemoryDAO:
    """Thin wrapper around a MemoryStoreInterface implementation."""

    def __init__(
        self,
        store: MemoryStoreInterface,
        tagger: Optional[TaggerInterface] = None,
    ):
        self.store = store
        # Default to AutoTagger (LLM if available, else heuristic)
        self.tagger = tagger or AutoTagger()

    async def get_recent_messages(self, session_id: UUID, limit: int = 10) -> List[ChatMessage]:
        return await self.store.get_messages(session_id, limit)

    async def create_message(self, message: ChatMessage) -> None:
        # Tag content for importance & topic
        try:
            tags = await self.tagger.tag(message) if self.tagger else {"type": "CHITCHAT"}
        except Exception:
            tags = {"type": "CHITCHAT", "importance": 0.0, "topic": "general"}

        item = MemoryItem.from_chat_message(message)
        item.ring = MemoryRing.IN_SESSION
        # Merge tags into metadata
        item.metadata.update(tags)
        item.importance = float(tags.get("importance", item.importance))
        await self.store.create_memory_item(item)

    async def create_memory_item(self, item: MemoryItem) -> None:
        """Persist any MemoryItem directly (e.g. summaries from background workers)."""
        await self.store.create_memory_item(item) 