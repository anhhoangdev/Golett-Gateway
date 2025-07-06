"""Hybrid ReRanker used by the new ContextForge implementation.

This is effectively extracted from the legacy engine.py so it can be used
independently of legacy code.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from golett_core.schemas.memory import MemoryItem, Node


class ReRanker:
    """Combines semantic, recency, relational, and importance signals."""

    def __init__(
        self,
        w_sem: float = 0.5,
        w_rec: float = 0.2,
        w_rel: float = 0.2,
        w_imp: float = 0.1,
    ):
        self.w_sem = w_sem
        self.w_rec = w_rec
        self.w_rel = w_rel
        self.w_imp = w_imp

    # ------------------------------------------------------------------
    # Dynamic weighting helpers
    # ------------------------------------------------------------------

    def update_weights(self, intent: str) -> None:
        """Dynamically adapt weight distribution based on *intent*."""
        if intent == "relational":
            self.w_rel, self.w_sem, self.w_rec, self.w_imp = 0.4, 0.3, 0.2, 0.1
        elif intent == "follow_up":
            self.w_rec, self.w_sem, self.w_rel, self.w_imp = 0.4, 0.3, 0.1, 0.2
        else:  # analytical / default
            self.w_sem, self.w_rec, self.w_rel, self.w_imp = 0.5, 0.2, 0.2, 0.1

    # ------------------------------------------------------------------
    # Scoring components
    # ------------------------------------------------------------------

    @staticmethod
    def _semantic_score(item: MemoryItem, query_embedding: Optional[List[float]]) -> float:
        if query_embedding is None or getattr(item, "embedding", None) is None:
            return 0.0
        a = query_embedding
        b = item.embedding  # type: ignore[attr-defined]
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x * x for x in a) ** 0.5
        mag_b = sum(x * x for x in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    @staticmethod
    def _recency_score(item: MemoryItem) -> float:
        delta = datetime.utcnow() - item.created_at
        return max(0.0, 1.0 - (delta.days / 30))

    @staticmethod
    def _relational_score(item: MemoryItem, rel_nodes: List[Node]) -> float:
        if not rel_nodes or item.source_id is None:
            return 0.0
        rel_ids = {n.id for n in rel_nodes}
        return 1.0 if item.source_id in rel_ids else 0.0

    @staticmethod
    def _importance_score(item: MemoryItem) -> float:
        # Normalise importance (0..1) already ensured by tagger/processor
        return item.importance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score(
        self,
        item: MemoryItem,
        query_embedding: Optional[List[float]],
        intent: str,
        relational_nodes: List[Node],
    ) -> float:
        sem = self._semantic_score(item, query_embedding)
        rec = self._recency_score(item)
        rel = self._relational_score(item, relational_nodes)
        imp = self._importance_score(item)
        return (
            (self.w_sem * sem)
            + (self.w_rec * rec)
            + (self.w_rel * rel)
            + (self.w_imp * imp)
        ) 