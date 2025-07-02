"""In-session (episodic) memory ring.

Stores raw chat turns for the active session.  Backed by Postgres (via
MemoryDAO) and optionally cached in Redis for hot-path reads.
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from golett_core.schemas.memory import (
    MemoryItem,
    ChatMessage,
    MemoryType,
    MemoryRing,
)
from golett_core.interfaces import MemoryStorageInterface
from golett_core.data_access.memory_dao import MemoryDAO


class InSessionStore(MemoryStorageInterface):
    """Raw chat messages with short TTL.  Not exposed to semantic search."""

    def __init__(self, memory_dao: MemoryDAO, ttl_seconds: int = 60 * 60):
        self.dao = memory_dao
        self.ttl_seconds = ttl_seconds

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    async def store_message(self, message: ChatMessage) -> None:  # noqa: D401
        await self.dao.create_message(message)

    async def store_memory_item(self, item: MemoryItem) -> None:  # noqa: D401
        if item.type == MemoryType.MESSAGE:
            item.ring = MemoryRing.IN_SESSION
            await self.dao.create_memory_item(item)

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    async def get_recent_messages(self, session_id: UUID, limit: int = 10) -> List[ChatMessage]:
        return await self.dao.get_recent_messages(session_id, limit)

    async def search_memories(self, *args, **kwargs):  # noqa: D401
        # No semantic search over raw turns – return empty list
        return [] 