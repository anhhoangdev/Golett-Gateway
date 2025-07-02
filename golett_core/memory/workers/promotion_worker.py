from __future__ import annotations

"""Background worker that promotes valuable short-term memories into the long-term ring.

Design rationale:
- **ShortTermStore** contains session-bound summaries that may be ephemeral.
- Items deemed important and stable over time should be copied to **LongTermStore**
  so that the knowledge is available across future sessions.

Promotion criteria (configurable):
1. ``importance`` score ≥ ``importance_threshold``.
2. Item age ≥ ``age_threshold`` seconds (gives summariser time to refine).

The worker scans the ShortTermStore periodically (or can be triggered manually)
and upserts qualifying items into LongTermStore.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List

from golett_core.schemas.memory import MemoryItem, MemoryType, MemoryRing
from golett_core.memory.rings.short_term import ShortTermStore
from golett_core.memory.rings.long_term import LongTermStore
from golett_core.data_access.memory_dao import MemoryDAO

__all__ = ["PromotionWorker"]


class PromotionWorker:
    """Periodic short→long term promotion service."""

    def __init__(
        self,
        short_term_store: ShortTermStore,
        long_term_store: LongTermStore,
        memory_dao: MemoryDAO,
        importance_threshold: float = 0.6,
        age_threshold_seconds: int = 60 * 5,
    ) -> None:
        self._short = short_term_store
        self._long = long_term_store
        self._dao = memory_dao
        self.importance_threshold = importance_threshold
        self.age_threshold = timedelta(seconds=age_threshold_seconds)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def promote_once(self) -> int:  # noqa: D401
        """Run one promotion pass. Returns number of items promoted."""
        now = datetime.utcnow()
        cutoff_time = now - self.age_threshold

        # Naively fetch all summary items via DAO – in production we'd filter in SQL.
        # Here we load a manageable subset for demo purposes.
        items: List[MemoryItem] = [
            itm
            for itm in self._dao.store._memory.values()  # type: ignore[attr-defined]
            if itm.type == MemoryType.SUMMARY
        ] if hasattr(self._dao.store, "_memory") else []

        promoted = 0
        for itm in items:
            if itm.importance < self.importance_threshold:
                continue
            if itm.created_at > cutoff_time:
                continue
            # Set ring and upsert into long-term store
            itm.ring = MemoryRing.LONG_TERM
            await self._long.store_memory_item(itm)
            promoted += 1
        return promoted

    async def run_forever(self, interval_seconds: int = 300) -> None:  # noqa: D401
        """Run promotion loop until cancelled."""
        while True:
            try:
                count = await self.promote_once()
                if count:
                    print(f"[PromotionWorker] promoted {count} items to long-term store")
            except Exception as exc:  # pragma: no cover
                print(f"[PromotionWorker] error: {exc}")
            await asyncio.sleep(interval_seconds) 