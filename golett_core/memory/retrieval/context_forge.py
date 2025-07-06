"""ContextForge – new retrieval pipeline built on MultiRingStorage.

Stages:
1. Fetch recent messages (episodic) & semantic matches (short+long term).
2. Re-rank with hybrid scorer.
3. Token-budget prune.
4. Assemble ContextBundle.
"""
from __future__ import annotations

import asyncio
from itertools import chain
from typing import List, Optional

from golett_core.memory.rings.multi_ring import MultiRingStorage
from golett_core.memory.retrieval.reranker import ReRanker
from golett_core.memory.retrieval.token_budget import TokenBudgeter
from golett_core.memory.retrieval.graph_retriever import GraphMemoryRetriever
from golett_core.schemas.memory import ChatMessage, ContextBundle, MemoryItem, Node
from golett_core.utils.embeddings import get_embedding_model


class ContextForge:
    """Central orchestrator that builds `ContextBundle` for a chat turn."""

    def __init__(
        self,
        storage: MultiRingStorage,
        reranker: ReRanker | None = None,
        budgeter: TokenBudgeter | None = None,
        graph_retriever: GraphMemoryRetriever | None = None,
    ) -> None:
        self.storage = storage
        self.reranker = reranker or ReRanker()
        self.budgeter = budgeter or TokenBudgeter()
        self._embedder = get_embedding_model()
        self.graph_retriever = graph_retriever

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def build_bundle(
        self,
        message: ChatMessage,
        intent: str = "analytical",
    ) -> ContextBundle:
        """Return a fully assembled ContextBundle for the AgentRunner."""
        session_id = message.session_id
        # Pre-compute embedding once for scoring
        query_embedding = self._embedder.embed_query(message.content)

        # ------------------ Stage-1: parallel fetch ------------------
        fetch_tasks = [
            self.storage.get_recent_messages(session_id, 10),
            self.storage.search_memories(session_id, message.content, limit=20),
        ]
        recent_msgs, sem_items = await asyncio.gather(*fetch_tasks)

        # Convert recent ChatMessages ➜ MemoryItems for uniformity
        recent_items: List[MemoryItem] = [
            MemoryItem.from_chat_message(m) for m in recent_msgs
        ]

        candidate_items: List[MemoryItem] = list(chain(recent_items, sem_items))

        # ------------------ Stage-2: graph neighbourhood (optional) -------------
        relational_nodes: List[Node] = []
        if self.graph_retriever is not None and intent == "relational":
            relational_nodes = await self.graph_retriever.fetch_related_nodes(
                message.content, depth=1
            )

        # ------------------ Stage-3: re-ranking ------------------
        self.reranker.update_weights(intent)

        scored = [
            (
                self.reranker.score(itm, query_embedding, intent, relational_nodes),
                itm,
            )
            for itm in candidate_items
        ]
        scored.sort(key=lambda t: t[0], reverse=True)

        # ------------------ Stage-4: token budget prune ------------------
        pruned_items = self.budgeter.prune([itm for _, itm in scored], 3000)

        # ------------------ Stage-5: bundle assemble ------------------
        return ContextBundle(
            session_id=session_id,
            current_turn=message,
            recent_history=recent_msgs,
            retrieved_memories=pruned_items,
            related_graph_entities=relational_nodes,
        ) 