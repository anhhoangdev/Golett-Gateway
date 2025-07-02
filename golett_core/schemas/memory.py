from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from golett_core.settings import settings

__all__ = [
    "ChatRole",
    "ChatMessage",
    "ChatResponse",
    "MemoryType",
    "MemoryItem",
    "Node",
    "VectorMatch",
    "ContextBundle",
    "MemoryRing",
]


class ChatRole(str, Enum):
    """Role of a message in the chat transcript."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A single utterance in a chat session."""

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    role: ChatRole = ChatRole.USER
    content: str
    embedding: Optional[List[float]] = None  # lazy-loaded / generated elsewhere
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow"
    )


class MemoryType(str, Enum):
    """Enumeration of supported memory categories."""

    MESSAGE = "message"
    SUMMARY = "summary"
    ENTITY = "entity"
    FACT = "fact"
    PROCEDURE = "procedure"


class MemoryRing(str, Enum):
    """Logical tier a MemoryItem belongs to."""

    IN_SESSION = "in_session"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class MemoryItem(BaseModel):
    """The atomic unit stored in the memory backend, independent of storage layer."""

    id: UUID = Field(default_factory=uuid4)
    source_id: Optional[UUID] = None  # e.g. originating ChatMessage.id
    session_id: Optional[UUID] = None
    type: MemoryType = MemoryType.MESSAGE
    content: str
    importance: float = 0.5  # LLM-assigned importance score (0-1)
    ring: MemoryRing = MemoryRing.IN_SESSION  # storage tier
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_chat_message(cls, msg: "ChatMessage") -> "MemoryItem":
        """Create a MemoryItem from a ChatMessage."""
        return cls(
            source_id=msg.id,
            session_id=msg.session_id,
            type=MemoryType.MESSAGE,
            content=msg.content,
            created_at=msg.created_at,
            importance=0.3,  # Default importance for raw messages
            metadata={"role": msg.role.value},
            ring=MemoryRing.IN_SESSION,
        )

    def to_chat_message(self) -> "ChatMessage":
        """Convert a MemoryItem back to a ChatMessage."""
        if self.type != MemoryType.MESSAGE:
            raise ValueError("Can only convert MemoryItems of type MESSAGE back to a ChatMessage.")

        return ChatMessage(
            id=self.source_id,
            session_id=self.session_id,
            role=self.metadata.get("role", "user"),
            content=self.content,
            created_at=self.created_at,
        )


class Node(BaseModel):
    """Lightweight representation of a graph node (relational memory)."""

    id: UUID
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow"
    )


class VectorMatch(BaseModel):
    """Wrapper for search results from a vector DB."""

    id: UUID
    score: float
    payload: MemoryItem

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
        arbitrary_types_allowed=True,
    )


class ContextBundle(BaseModel):
    """The fully-assembled context passed to the agent for each turn."""

    session_id: UUID
    current_turn: ChatMessage
    recent_history: List[ChatMessage]
    retrieved_memories: List[MemoryItem]
    related_graph_entities: List[Node]
    relevant_metrics: Optional[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
        arbitrary_types_allowed=True,
    )


class ChatResponse(BaseModel):
    """Standard response envelope returned to API callers."""

    response: str
    session_id: UUID
    message_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow"
    ) 