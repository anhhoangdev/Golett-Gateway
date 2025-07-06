from __future__ import annotations

from typing import Protocol

from golett_core.events import BaseEvent, EventBus

__all__ = ["WorkerInterface"]


class WorkerInterface(Protocol):
    """Reactive background worker that responds to EventBus notifications."""

    def interested_in(self, event: BaseEvent) -> bool:  # noqa: D401
        """Return True if *event* should trigger this worker."""
        ...

    async def run(self, event: BaseEvent, bus: EventBus) -> None:  # noqa: D401
        """Perform work in reaction to *event*.

        The worker may publish new events to *bus*.
        """
        ... 