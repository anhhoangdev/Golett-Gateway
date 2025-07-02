from __future__ import annotations

import json
from typing import List, Dict
from uuid import UUID
from collections import deque

from golett_core.schemas import Session, ChatMessage
from golett_core.interfaces import (
    SessionStoreInterface, 
    HistoryStoreInterface, 
    CacheClientInterface,
    SessionManagerInterface
)

_DEFAULT_CACHE_TTL = 300  # seconds

__all__ = [
    "SessionManager",
    "InMemorySessionManager",
]


class SessionManager:
    """High-level API for chat session management.

    This class is framework-agnostic and relies on dependency injection for
    persistence and cache layers.
    """

    def __init__(
        self,
        session_store: SessionStoreInterface,
        history_store: HistoryStoreInterface,
        cache_client: CacheClientInterface,
        cache_ttl: int = _DEFAULT_CACHE_TTL,
    ) -> None:
        self._sessions = session_store
        self._history = history_store
        self._cache = cache_client
        self._ttl = cache_ttl

    # ------------------------------------------------------------------
    # Session metadata
    # ------------------------------------------------------------------

    async def create_session(self, user_id: str, metadata: dict | None = None) -> Session:  # noqa: D401
        session = Session(user_id=user_id, metadata=metadata or {})
        await self._sessions.create_session(session)
        return session

    async def get_session(self, session_id: UUID) -> Session:  # noqa: D401
        return await self._sessions.get_session(session_id)

    # ------------------------------------------------------------------
    # Chat history
    # ------------------------------------------------------------------

    async def add_message(self, session_id: UUID, message: ChatMessage) -> None:  # noqa: D401
        await self._history.create_message(session_id, message)
        # Invalidate cache so subsequent reads see the new message
        await self._cache.delete(self._cache_key(session_id))

    async def get_history(self, session_id: UUID, limit: int = 10) -> List[ChatMessage]:  # noqa: D401
        # 1. Attempt cache lookup
        cache_key = self._cache_key(session_id, limit)
        cached = await self._cache.get(cache_key)
        if cached:
            return [ChatMessage.parse_raw(msg_json) for msg_json in cached]

        # 2. Fallback to persistent store
        history = await self._history.get_recent_messages(session_id, limit)

        # 3. Populate cache (store as JSON strings to avoid pydantic in redis)
        await self._cache.set(
            cache_key,
            [m.model_dump_json() for m in history],
            expire=self._ttl,
        )
        return history

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cache_key(session_id: UUID, limit: int = 10) -> str:  # noqa: D401
        return f"history:{session_id}:{limit}"


class InMemorySessionManager(SessionManagerInterface):
    """
    A simple, non-persistent session manager that holds history in memory.
    """
    def __init__(self) -> None:
        self._histories: Dict[UUID, deque[ChatMessage]] = {}

    async def add_message(self, session_id: UUID, message: ChatMessage) -> None:
        """Adds a message to a session's history."""
        if session_id not in self._histories:
            self._histories[session_id] = deque()
        self._histories[session_id].append(message)

    async def get_history(self, session_id: UUID, limit: int = 20) -> List[ChatMessage]:
        """Retrieves the recent message history for a session."""
        history = self._histories.get(session_id, deque())
        # Return a slice of the most recent 'limit' items
        return list(history)[-limit:] 