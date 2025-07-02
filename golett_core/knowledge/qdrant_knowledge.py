from __future__ import annotations

"""CrewAI `Knowledge` variant backed by Qdrant.

This thin wrapper mirrors the public signature of ``crewai.knowledge.knowledge.Knowledge``
so it can be used as a drop-in replacement anywhere in *Golett* without touching
upstream code.
"""

from typing import Any, Dict, List, Optional

from crewai.knowledge.knowledge import Knowledge  # type: ignore
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource  # type: ignore

from golett_core.knowledge.qdrant_storage import QdrantKnowledgeStorage

__all__ = [
    "QdrantKnowledge",
]


class QdrantKnowledge(Knowledge):
    """Overrides the default Chroma storage with the Qdrant backend."""

    def __init__(
        self,
        collection_name: str,
        sources: Optional[List[BaseKnowledgeSource]] = None,
        embedder: Optional[Dict[str, Any]] = None,
        qdrant_url: str | None = None,
        prefer_grpc: bool = False,
    ) -> None:  # noqa: D401 – ctor
        storage = QdrantKnowledgeStorage(
            collection_name=collection_name,
            embedder=embedder,
            qdrant_url=qdrant_url,
            prefer_grpc=prefer_grpc,
        )

        super().__init__(
            collection_name=collection_name,
            sources=sources or [],
            embedder=embedder,
            storage=storage,
        ) 