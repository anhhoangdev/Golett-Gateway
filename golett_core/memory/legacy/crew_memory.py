"""Legacy CrewAI integration – kept for backwards compatibility.

NOTE: This file is **not** part of the new three-ring architecture.
It is moved under `memory.legacy` so consumers can still import
`golett_core.memory.legacy.crew_memory.GolettMemory` during migration.
"""
from __future__ import annotations

from typing import Any, Optional
import asyncio

from crewai.memory.memory import Memory

from golett_core.memory.retrieval import ReRanker, TokenBudgeter, extract_entities
from golett_core.memory.legacy.crew_storage import GolettStorage
from golett_core.schemas.memory import ChatMessage, ContextBundle


class GolettMemory(Memory):
    """CrewAI Memory adapter – legacy implementation."""

    def __init__(
        self,
        storage: GolettStorage,
        reranker: ReRanker,
        budgeter: TokenBudgeter,
        entity_labels: Optional[list[str]] = None,
        **data: Any,
    ):
        super().__init__(storage=storage, **data)
        self.reranker = reranker
        self.budgeter = budgeter
        self.entity_labels = entity_labels

    def save(self, message: ChatMessage) -> None:
        asyncio.create_task(self.storage.save_message(message))

    async def search(self, message: ChatMessage, intent: str = "analytical") -> ContextBundle:  # type: ignore
        entity_ids = extract_entities(message.content, labels=self.entity_labels)

        recent_items, semantic_items, relational_nodes = await self.storage.fetch_candidates(
            message, entity_ids
        )

        candidate_items = recent_items + semantic_items

        self.reranker.update_weights(intent)
        scored = [
            (self.reranker.score(itm, message.embedding, intent, relational_nodes), itm)
            for itm in candidate_items
        ]
        scored.sort(reverse=True, key=lambda t: t[0])

        pruned_items = self.budgeter.prune([itm for _, itm in scored])

        return ContextBundle(
            session_id=message.session_id,
            current_turn=message,
            recent_history=[msg.to_chat_message() for msg in recent_items],
            retrieved_memories=pruned_items,
            related_graph_entities=relational_nodes,
        ) 