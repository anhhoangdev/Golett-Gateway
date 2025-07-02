from __future__ import annotations

from typing import List
from uuid import UUID

from golett_core.schemas.memory import MemoryItem, VectorMatch
from golett_core.interfaces import VectorStoreInterface


class VectorDAO:
    """Thin adapter over a vector store implementation."""

    def __init__(self, store: VectorStoreInterface):
        self.store = store

    async def search(
        self, collection: str, query_vector: List[float], top_k: int
    ) -> List[VectorMatch]:
        return await self.store.search(collection, query_vector, top_k)

    async def search_vectors(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 10,
    ) -> List[MemoryItem]:  # convenience for rings expecting MemoryItem list
        """Wrapper that unwraps VectorMatch → MemoryItem for compatibility."""
        matches = await self.search(collection, query_vector, top_k)
        return [m.payload for m in matches if m.payload]

    async def upsert(
        self,
        item: MemoryItem,
        vector: List[float],
        collection: str = "default_collection",
    ):
        """Upserts a memory item's vector and payload into the store."""
        await self.store.upsert_vector(
            collection=collection,
            point_id=item.id,
            vector=vector,
            payload=item.dict(),
        ) 