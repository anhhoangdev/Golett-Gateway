"""Storage and persistence interfaces for Golett.

This module contains all protocol definitions for storage, persistence, and data access.
These are low-level interfaces that define how data is stored and retrieved.
"""

from __future__ import annotations

from typing import Protocol, List, Dict, Any, Optional, runtime_checkable
from uuid import UUID

from golett_core.schemas import Session, ChatMessage, Document
from golett_core.schemas.memory import (
    MemoryItem,
    Node,
    VectorMatch,
    MemoryType,
)


# =============================================================================
# Session Storage Interfaces
# =============================================================================

@runtime_checkable
class SessionStoreInterface(Protocol):
    """Persistence contract for session metadata."""

    async def create_session(self, session: Session) -> None:
        ...

    async def get_session(self, session_id: str | UUID) -> Session:
        ...


@runtime_checkable
class HistoryStoreInterface(Protocol):
    """Persistence contract for chat history."""

    async def create_message(self, session_id: str | UUID, message: ChatMessage) -> None:
        ...

    async def get_recent_messages(self, session_id: str | UUID, limit: int = 10) -> List[ChatMessage]:
        ...


@runtime_checkable
class CacheClientInterface(Protocol):
    """Minimal async key-value cache contract (e.g., Redis)."""

    async def get(self, key: str) -> Any:
        ...

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        ...

    async def delete(self, key: str) -> None:
        ...


# =============================================================================
# Memory Storage Interfaces
# =============================================================================

@runtime_checkable
class MemoryItemStoreInterface(Protocol):
    """Read/write access to memory items in the relational store."""

    async def get_messages(self, session_id: UUID, limit: int) -> List[ChatMessage]:
        ...

    async def create_memory_item(self, item: MemoryItem) -> UUID:
        ...


@runtime_checkable
class VectorDBInterface(Protocol):
    """Contract for vector database access (e.g., Qdrant)."""

    async def upsert_vector(
        self, collection: str, point_id: UUID, vector: List[float], payload: Dict[str, Any]
    ) -> None:
        ...

    async def search(
        self, collection: str, query_vector: List[float], top_k: int
    ) -> List[VectorMatch]:
        ...


@runtime_checkable
class GraphStoreInterface(Protocol):
    """Optional abstraction for graph storage operations."""

    async def upsert_nodes(self, nodes: List[Node]) -> None:
        ...

    async def upsert_edges(self, edges: List[Dict[str, Any]]) -> None:
        ...

    async def neighborhood(self, node_ids: List[UUID], depth: int) -> List[Node]:
        ...


# =============================================================================
# Unified Storage Interfaces
# =============================================================================

@runtime_checkable
class MemoryStorageInterface(Protocol):
    """Unified storage interface for both relational and vector data."""

    async def store_message(self, message: ChatMessage) -> None:
        """Persist a raw chat message (no semantic indexing)."""
        ...

    async def store_memory_item(self, item: MemoryItem) -> None:
        """Persist any MemoryItem and (optionally) its vector representation."""
        ...

    async def get_recent_messages(self, session_id: UUID, limit: int) -> List[ChatMessage]:
        """Return the most recent *limit* ChatMessage objects for the session."""
        ...

    async def search_memories(
        self,
        session_id: UUID,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Semantic search across all memory types for the given session."""
        ...


# =============================================================================
# Legacy Data Access Interfaces (for backward compatibility)
# =============================================================================

@runtime_checkable
class MemoryStoreInterface(Protocol):
    """Legacy interface for basic memory store operations."""

    def get_session(self, session_id: UUID) -> Optional[Session]:
        ...

    def create_session(self, session: Session) -> Session:
        ...

    def get_messages(self, session_id: UUID) -> List[ChatMessage]:
        ...

    def add_message(self, message: ChatMessage) -> None:
        ...


@runtime_checkable
class VectorStoreInterface(Protocol):
    """Legacy interface for basic vector store operations."""

    def add(self, documents: List[Document]):
        ...

    def search(self, query_embedding: List[float], top_k: int) -> List[Document]:
        ...


# =============================================================================
# Processing Interfaces
# =============================================================================

@runtime_checkable
class TaggerInterface(Protocol):
    """Pluggable contract for message taggers used by the memory pipeline."""

    async def tag(self, msg: ChatMessage) -> Dict[str, str | float]:
        ...