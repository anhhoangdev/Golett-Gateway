"""Core business logic interfaces for Golett.

This module contains all the main protocol definitions for business logic components.
These are high-level interfaces that define the behavior of core system components.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Type, runtime_checkable
from uuid import UUID

from golett_core.schemas.knowledge import Document

if TYPE_CHECKING:
    from pydantic import BaseModel
    from crewai import Agent, Task
    from golett_core.schemas import ChatMessage, KnowledgeDocument
    from golett_core.schemas.memory import ContextBundle
    from golett_core.crew.spec import CrewSpec


@runtime_checkable
class MemoryInterface(Protocol):
    """Protocol for core memory operations."""

    async def save_message(self, msg: "ChatMessage") -> None:
        """Saves a message to memory."""
        ...

    async def search(
        self, session_id: UUID, query: str, include_recent: bool = True
    ) -> ContextBundle:
        """Searches memory to build a context bundle for a query."""
        ...


@runtime_checkable
class SessionManagerInterface(Protocol):
    """Protocol for session management."""
    
    async def add_message(self, session_id: UUID, message: "ChatMessage") -> None:
        """Adds a message to a session's history."""
        ...
        
    async def get_history(self, session_id: UUID, limit: int = 10) -> List["ChatMessage"]:
        """Retrieves the recent message history for a session."""
        ...


@runtime_checkable
class ToolInterface(Protocol):
    """Protocol for agent tools."""

    name: str
    description: str
    args_schema: Type["BaseModel"] | None

    def run(
        self, argument: str | Dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Executes the tool with the given arguments."""
        ...


@runtime_checkable
class CrewInterface(Protocol):
    """Protocol for a crew of agents."""

    agents: List[Agent]
    tasks: List[Task]

    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """Kicks off the crew to start working on its assigned tasks."""
        ...

    async def save_user_message(self, message: str) -> None:
        """Saves a user message to the crew's memory."""
        ...

    async def save_assistant_message(self, message: str) -> None:
        """Saves an assistant message to the crew's memory."""
        ...


@runtime_checkable
class CrewFactoryInterface(Protocol):
    """Protocol for a factory that creates and runs a crew from a spec."""

    async def create_and_run(
        self, spec: CrewSpec, prompt: str, history: List["ChatMessage"]
    ) -> str:
        """Creates and runs a crew, returning the string result."""
        ...


@runtime_checkable
class OrchestratorInterface(Protocol):
    """Protocol for an agent orchestrator."""

    async def run(self, message: str) -> str:
        """Runs the orchestration logic for a given user message."""
        ...


@runtime_checkable
class KnowledgeInterface(Protocol):
    """Protocol for knowledge management operations."""

    async def ingest_document(self, doc: Document) -> None:
        """Ingests a single document into the knowledge base."""
        ...

    async def get_retrieval_context(
        self,
        query: str,
        user_id: str | None = None,
        chat_history: List["ChatMessage"] | None = None,
        top_k: int = 5,
    ) -> List[str]:
        """Retrieves relevant context from the knowledge base for a query."""
        ...