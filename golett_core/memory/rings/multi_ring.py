"""Fan-out facade that delegates memory operations to the appropriate rings."""
from __future__ import annotations

import asyncio
from typing import List
from uuid import UUID

from golett_core.schemas.memory import ChatMessage, MemoryItem, MemoryType
from golett_core.interfaces import MemoryStorageInterface


class MultiRingStorage(MemoryStorageInterface):
    """Combines in-session, short-term, and long-term rings under one API."""

    def __init__(
        self,
        in_session: MemoryStorageInterface,
        short_term: MemoryStorageInterface,
        long_term: MemoryStorageInterface,
    ) -> None:
        self.in_session = in_session
        self.short_term = short_term
        self.long_term = long_term

    # ------------------------------------------------------------------
    # Write path helpers
    # ------------------------------------------------------------------

    async def store_message(self, message: ChatMessage) -> None:  # noqa: D401
        await self.in_session.store_message(message)

    async def store_memory_item(self, item: MemoryItem) -> None:  # noqa: D401
        # Delegate to all rings that may accept the item
        await asyncio.gather(
            self.in_session.store_memory_item(item),
            self.short_term.store_memory_item(item),
            self.long_term.store_memory_item(item),
        )

    # ------------------------------------------------------------------
    # Read path helpers
    # ------------------------------------------------------------------

    async def get_recent_messages(self, session_id: UUID, limit: int = 10):  # noqa: D401
        return await self.in_session.get_recent_messages(session_id, limit)

    async def search_memories(
        self,
        session_id: UUID,
        query: str,
        memory_types: List[MemoryType] | None = None,
        limit: int = 15,
    ):  # noqa: D401
        st_items, lt_items = await asyncio.gather(
            self.short_term.search_memories(session_id, query, memory_types, limit),
            self.long_term.search_memories(session_id, query, memory_types, limit),
        )
        return st_items + lt_items 