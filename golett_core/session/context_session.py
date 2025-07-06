from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from golett_core.events import MemoryWritten, EventBus
from golett_core.memory.retrieval.context_forge import ContextForge
from golett_core.schemas.memory import ChatMessage, ContextBundle

__all__ = ["SessionContext"]


class SessionContext:
    """Ephemeral helper that lets agents *pull* fresh context on demand.

    It invalidates its internal cache whenever a MemoryWritten event for the
    same session id is observed on the EventBus.
    """

    def __init__(
        self,
        *,
        session_id: UUID,
        context_forge: ContextForge,
        bus: EventBus,
        intent: str = "analytical",
    ) -> None:
        self.session_id = session_id
        self.intent = intent
        self._forge = context_forge
        self._bus = bus
        self._cached_bundle: Optional[ContextBundle] = None

        # Subscribe to memory-write events to drop cache.
        self._bus.subscribe(self._is_own_memory_write, self._invalidate)

    # ------------------------------------------------------------------
    # Public API used by agents
    # ------------------------------------------------------------------

    async def fetch(self, message: ChatMessage) -> ContextBundle:  # noqa: D401
        """Return (possibly cached) retrieval bundle for *message*."""
        if self._cached_bundle is None:
            self._cached_bundle = await self._forge.build_bundle(
                message=message, intent=self.intent
            )
        return self._cached_bundle

    def last_result(self) -> Optional[ContextBundle]:  # noqa: D401
        return self._cached_bundle

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_own_memory_write(self, ev):  # noqa: D401
        return isinstance(ev, MemoryWritten) and ev.session_id == self.session_id

    async def _invalidate(self, _):  # noqa: D401, ANN001
        self._cached_bundle = None 