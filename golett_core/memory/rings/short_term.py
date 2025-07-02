"""Short-term memory ring – session-bound summaries.

These summaries are created by SummarizerWorker and remain relevant only
within the session.  They live in Postgres + Qdrant so they can be
queried semantically.
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from golett_core.interfaces import MemoryStorageInterface
from golett_core.schemas.memory import ChatMessage, MemoryItem, MemoryType, MemoryRing
from golett_core.data_access.memory_dao import MemoryDAO
from golett_core.data_access.vector_dao import VectorDAO
from golett_core.utils.embeddings import get_embedding_model, EmbeddingModel


class ShortTermStore(MemoryStorageInterface):
    """Session-scoped summaries and key facts."""

    def __init__(self, memory_dao: MemoryDAO, vector_dao: VectorDAO):
        self.dao = memory_dao
        self.vector = vector_dao
        self.embedder: EmbeddingModel = get_embedding_model()

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    async def store_memory_item(self, item: MemoryItem) -> None:  # noqa: D401
        if item.type != MemoryType.SUMMARY:
            return  # only handle summaries here
        # Mark ring before persisting
        item.ring = MemoryRing.SHORT_TERM
        # Persist to relational
        await self.dao.create_memory_item(item)
        # Persist to vector store for semantic retrieval
        vector = self.embedder.embed_query(item.content)
        await self.vector.upsert(item, vector)

    async def store_message(self, message: ChatMessage):  # noqa: D401
        # Raw messages are not handled here
        return

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    async def get_recent_messages(self, session_id: UUID, limit: int):  # noqa: D401
        # Short-term store does not serve raw messages
        return []

    async def search_memories(
        self,
        session_id: UUID,
        query: str,
        memory_types: List[MemoryType] | None = None,
        limit: int = 10,
    ) -> List[MemoryItem]:
        # Only semantic search inside this session
        vector = self.embedder.embed_query(query)
        results: List[MemoryItem] = await self.vector.search_vectors(
            "messages_vectors",
            vector,
            limit,
        )
        # Filter by type if requested
        if memory_types:
            results = [m for m in results if m.type in memory_types]
        return results 