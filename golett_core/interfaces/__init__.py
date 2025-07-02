"""Interfaces (Protocols) for Golett Core.

This module re-exports all core protocols for convenient import access.
The interfaces are now organized into:
- core.py: Main business logic interfaces
- storage.py: Storage and persistence interfaces

Instead of importing from individual files, you can do:
`from golett_core.interfaces import MemoryInterface`
"""

# Core business logic interfaces
from .core import (
    MemoryInterface,
    SessionManagerInterface,
    ToolInterface,
    CrewInterface,
    CrewFactoryInterface,
    OrchestratorInterface,
    KnowledgeInterface,
)

# Storage and persistence interfaces
from .storage import (
    SessionStoreInterface,
    HistoryStoreInterface,
    CacheClientInterface,
    MemoryItemStoreInterface,
    VectorDBInterface,
    GraphStoreInterface,
    MemoryStorageInterface,
    MemoryStoreInterface,
    VectorStoreInterface,
    TaggerInterface,
)

__all__ = [
    # Core business interfaces
    "MemoryInterface",
    "SessionManagerInterface", 
    "ToolInterface",
    "CrewInterface",
    "CrewFactoryInterface",
    "OrchestratorInterface",
    "KnowledgeInterface",
    # Storage interfaces
    "SessionStoreInterface",
    "HistoryStoreInterface", 
    "CacheClientInterface",
    "MemoryItemStoreInterface",
    "VectorDBInterface",
    "GraphStoreInterface",
    "MemoryStorageInterface",
    "MemoryStoreInterface",
    "VectorStoreInterface",
    "TaggerInterface",
] 