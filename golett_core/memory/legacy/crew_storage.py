"""Legacy storage adapter for CrewAI integration."""
from __future__ import annotations

import asyncio

from golett_core.interfaces import (
    MemoryStoreInterface,
    VectorStoreInterface,
    GraphStoreInterface,
)
from golett_core.schemas.memory import ChatMessage, MemoryItem, Node


class GolettStorage:  # pragma: no cover – legacy
    """Implements Stage-1 multi-modal fetch for CrewAI legacy path."""

    def __init__(
        self,
        memory_dao: MemoryStoreInterface,
        vector_dao: VectorStoreInterface,
        graph_dao: GraphStoreInterface,
    ):
        self.mem = memory_dao
        self.vec = vector_dao
        self.graph = graph_dao

    async def fetch_candidates(
        self, message: ChatMessage, entity_ids: list[str]
    ) -> tuple[list[MemoryItem], list[MemoryItem], list[Node]]:
        fetch_tasks = [
            self.mem.get_recent_messages(message.session_id, 10),
            self.vec.search_vectors("messages_vectors", message.embedding, 15),
            self.graph.get_graph_neighborhood(entity_ids, 2),
        ]
        recent_msgs, semantic_matches, relational_nodes = await asyncio.gather(*fetch_tasks)

        recent_items = [MemoryItem.from_chat_message(msg) for msg in recent_msgs]
        semantic_items = [m.payload for m in semantic_matches if m.payload]
        return recent_items, semantic_items, relational_nodes

    async def save_message(self, message: ChatMessage):
        if message.embedding:
            memory_item = MemoryItem.from_chat_message(message)
            await self.vec.upsert_memory_item("messages_vectors", memory_item, message.embedding)  # type: ignore[arg-type]
        await self.mem.create_message(message)
