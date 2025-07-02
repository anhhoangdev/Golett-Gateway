"""Long-term memory ring – cross-session knowledge.

Handles FACT, PROCEDURE, ENTITY, and global SUMMARY items.  Persisted to
Postgres (relational) and Qdrant (vector) for semantic search.
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from golett_core.interfaces import MemoryStorageInterface
from golett_core.schemas.memory import ChatMessage, MemoryItem, MemoryType, MemoryRing
from golett_core.data_access.memory_dao import MemoryDAO
from golett_core.data_access.vector_dao import VectorDAO
from golett_core.utils.embeddings import get_embedding_model, EmbeddingModel

_ACCEPTED_TYPES = {
    MemoryType.FACT,
    MemoryType.PROCEDURE,
    MemoryType.ENTITY,
    MemoryType.SUMMARY,
}


class LongTermStore(MemoryStorageInterface):
    """Global knowledge base across all sessions."""

    def __init__(self, memory_dao: MemoryDAO, vector_dao: VectorDAO):
        self.dao = memory_dao
        self.vector = vector_dao
        self.embedder: EmbeddingModel = get_embedding_model()

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    async def store_memory_item(self, item: MemoryItem) -> None:  # noqa: D401
        if item.type not in _ACCEPTED_TYPES:
            return
        item.ring = MemoryRing.LONG_TERM
        await self.dao.create_memory_item(item)
        if item.content.strip():
            vector = self.embedder.embed_query(item.content)
            await self.vector.upsert(item, vector)

    async def store_message(self, message: ChatMessage):  # noqa: D401
        # Raw chat messages are not stored in long-term ring
        return

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    async def get_recent_messages(self, session_id: UUID, limit: int):  # noqa: D401
        return []

    async def search_memories(
        self,
        session_id: UUID,  # ignored, global scope
        query: str,
        memory_types: List[MemoryType] | None = None,
        limit: int = 10,
    ) -> List[MemoryItem]:
        vector = self.embedder.embed_query(query)
        results: List[MemoryItem] = await self.vector.search_vectors(
            "messages_vectors",
            vector,
            limit,
        )
        if memory_types:
            results = [m for m in results if m.type in memory_types]
        return results 