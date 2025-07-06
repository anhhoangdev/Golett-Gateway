from __future__ import annotations

"""SchedulerService – cooperative task runner for background maintenance.

The service *does not* allocate its own event loop.  Instead it should be
started from whatever async runtime the application already uses::

    scheduler = SchedulerService()
    scheduler.register_worker(summariser.run_forever, interval=300)
    scheduler.register_worker(promotion.run_forever, interval=600)
    scheduler.register_worker(pruner.run_forever, interval=900)
    await scheduler.start()

Workers are expected to be **async callables** that either run forever
(e.g. ``run_forever``) **or** perform a single pass and return – the scheduler
will wrap them in a loop based on the provided ``interval``.
"""

import asyncio
from collections.abc import Callable, Awaitable
from typing import List, Optional

# Interface
from golett_core.interfaces import SchedulerInterface


class _WorkerHandle:
    """Internal book-keeping for a scheduled coroutine."""

    def __init__(self, coro: Callable[[], Awaitable[None]]):
        self.task: Optional[asyncio.Task] = None
        self._coro_factory = coro

    def start(self) -> None:
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self._coro_factory())

    def cancel(self) -> None:
        if self.task and not self.task.done():
            self.task.cancel()


# pylint: disable=too-few-public-methods
class SchedulerService(SchedulerInterface):
    """Simple supervisor that restarts crashed background workers."""

    def __init__(self) -> None:
        self._handles: List[_WorkerHandle] = []
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_worker(
        self,
        worker_fn: Callable[[int], Awaitable[None]] | Callable[[], Awaitable[None]],
        *,
        interval: int | None = None,
    ) -> None:
        """Register *worker_fn*; optionally wrap it in an interval loop."""

        async def _runner() -> None:
            # If interval is None we assume the worker itself blocks forever.
            if interval is None:
                await worker_fn()  # type: ignore[arg-type]
                return

            # Otherwise we run it repeatedly with a sleep in-between.
            while True:
                try:
                    if interval == 0:
                        await worker_fn()  # type: ignore[arg-type]
                    else:
                        await worker_fn(interval)  # type: ignore[arg-type]
                except Exception as exc:  # pragma: no cover
                    print(f"[SchedulerService] worker error: {exc}")
                await asyncio.sleep(interval)

        self._handles.append(_WorkerHandle(_runner))

    async def start(self) -> None:  # noqa: D401
        """Spawn all registered workers and supervise them until cancelled."""
        if self._running:
            raise RuntimeError("SchedulerService already running")
        self._running = True

        for handle in self._handles:
            handle.start()

        # Keep the supervisor alive – if any worker crashes we restart it.
        while True:
            await asyncio.sleep(5)
            for handle in self._handles:
                if handle.task is None or handle.task.done():
                    handle.start() 