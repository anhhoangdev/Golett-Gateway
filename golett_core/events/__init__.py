# Event system for reactive scheduler

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Tuple
from uuid import UUID

__all__ = [
    "BaseEvent",
    "NewTurn",
    "AgentProduced",
    "MemoryWritten",
    "TokensExceeded",
    "PeriodicTick",
    "EventBus",
]

# ---------------------------------------------------------------------------
#                       Data classes for events
# ---------------------------------------------------------------------------


@dataclass
class BaseEvent:
    """Root type for all events passed through EventBus."""

    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NewTurn(BaseEvent):
    session_id: UUID
    user_id: str
    turn_id: str
    text: str


@dataclass
class AgentProduced(BaseEvent):
    session_id: UUID
    agent_id: str
    turn_id: str
    content: str
    metadata: Dict[str, Any] | None = None


@dataclass
class MemoryWritten(BaseEvent):
    session_id: UUID
    memory_id: str
    type: str


@dataclass
class TokensExceeded(BaseEvent):
    session_id: UUID
    turn_id: str
    current_tokens: int


@dataclass
class PeriodicTick(BaseEvent):
    name: str = "default"


# ---------------------------------------------------------------------------
#                           Event bus implementation
# ---------------------------------------------------------------------------

Predicate = Callable[[BaseEvent], bool]
Handler = Callable[[BaseEvent], Awaitable[None]]


class EventBus:
    """A very small in-process pub-sub fabric based on asyncio.Queue."""

    def __init__(self) -> None:
        self._queue: "asyncio.Queue[BaseEvent]" = asyncio.Queue()
        self._subscriptions: List[Tuple[Predicate, Handler]] = []

    # ----------------------------- Producer API -----------------------------

    async def publish(self, event: BaseEvent) -> None:  # noqa: D401
        """Publish *event* to the queue and fan-out to subscribers."""
        await self._queue.put(event)
        # Fire async subscribers (best-effort)
        for predicate, handler in list(self._subscriptions):
            try:
                if predicate(event):
                    asyncio.create_task(handler(event))
            except Exception as exc:  # pragma: no cover – subscriber bug
                print(f"[EventBus] subscriber error: {exc}")

    # ----------------------------- Consumer API -----------------------------

    async def get(self) -> BaseEvent:  # noqa: D401
        """Await the next event from the queue (scheduler helper)."""
        return await self._queue.get()

    # ----------------------------- Subscriptions ----------------------------

    def subscribe(self, predicate: Predicate, handler: Handler) -> None:  # noqa: D401
        """Register *handler* for events where *predicate(event) is True*.

        The handler is executed in a fire-and-forget task so it MUST handle
        its own errors.
        """
        self._subscriptions.append((predicate, handler)) 