from __future__ import annotations

"""Periodic TTL pruning of in-session and short-term memory rings.

The pruner removes or archives items whose age exceeds ring-specific TTLs.
For demonstration purposes it only operates on *InMemory* stores where items
are kept in Python dicts.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List

from golett_core.memory.rings.in_session import InSessionStore
from golett_core.memory.rings.short_term import ShortTermStore
from golett_core.data_access.memory_dao import MemoryDAO
from golett_core.schemas.memory import MemoryItem, MemoryType

__all__ = ["TTLPruner"]


class TTLPruner:
    """Drops expired memory items based on creation timestamp."""

    def __init__(
        self,
        in_session_store: InSessionStore,
        short_term_store: ShortTermStore,
        memory_dao: MemoryDAO,
        in_session_ttl_seconds: int = 60 * 60,  # 1h
        short_term_ttl_seconds: int = 60 * 60 * 24 * 7,  # 1 week
    ) -> None:
        self._in_session = in_session_store
        self._short = short_term_store
        self._dao = memory_dao
        self._sess_cutoff = timedelta(seconds=in_session_ttl_seconds)
        self._short_cutoff = timedelta(seconds=short_term_ttl_seconds)

    async def prune_once(self) -> int:  # noqa: D401
        now = datetime.utcnow()
        sess_cutoff_time = now - self._sess_cutoff
        short_cutoff_time = now - self._short_cutoff

        # Again, only works with InMemoryMemoryStore for demo
        removed = 0
        if hasattr(self._dao.store, "_memory"):
            to_delete = []
            for mid, itm in list(self._dao.store._memory.items()):  # type: ignore[attr-defined]
                if itm.type == MemoryType.MESSAGE and itm.created_at < sess_cutoff_time:
                    to_delete.append(mid)
                elif itm.type == MemoryType.SUMMARY and itm.created_at < short_cutoff_time:
                    to_delete.append(mid)
            for mid in to_delete:
                del self._dao.store._memory[mid]  # type: ignore[attr-defined]
                removed += 1
        return removed

    async def run_forever(self, interval_seconds: int = 600):  # noqa: D401
        while True:
            try:
                count = await self.prune_once()
                if count:
                    print(f"[TTLPruner] removed {count} expired memory items")
            except Exception as exc:
                print(f"[TTLPruner] error: {exc}")
            await asyncio.sleep(interval_seconds) 