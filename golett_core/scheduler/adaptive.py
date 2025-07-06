from __future__ import annotations

import asyncio
from typing import List

from golett_core.events import BaseEvent, EventBus
from golett_core.interfaces.worker import WorkerInterface

__all__ = ["AdaptiveScheduler"]


class AdaptiveScheduler:
    """Hybrid event-driven scheduler that wakes workers *immediately* when their
    predicates match an incoming EventBus event.
    """

    def __init__(self, *, bus: EventBus, workers: List[WorkerInterface]):
        self._bus = bus
        self._workers = workers
        self._running = False

    async def start(self) -> None:  # noqa: D401
        if self._running:
            raise RuntimeError("AdaptiveScheduler already running")
        self._running = True

        while True:
            event: BaseEvent = await self._bus.get()

            # Fan-out in fire-and-forget tasks so one slow worker doesn't block.
            for worker in self._workers:
                try:
                    if worker.interested_in(event):
                        asyncio.create_task(worker.run(event, self._bus))
                except Exception as exc:  # pragma: no cover
                    print(f"[AdaptiveScheduler] worker dispatch error: {exc}") 