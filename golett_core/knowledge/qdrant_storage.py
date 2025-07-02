from __future__ import annotations

"""Qdrant-backed knowledge storage compatible with CrewAI's `Knowledge` api.

This implements the minimal subset of the original `KnowledgeStorage` interface
needed by `crewai.knowledge.knowledge.Knowledge` *without* depending on Chroma.
It relies on the official ``qdrant-client`` SDK and OpenAI embeddings by
default.

Only simple `save()` and `search()` operations are provided – enough for the
in-memory RAG flow used by Golett.  Feel free to extend with hybrid search,
batching or metadata filtering if your use-case requires it.
"""

import hashlib
import os
from typing import Any, Dict, List, Optional, Sequence, Union
from uuid import uuid4

import openai
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.models import Distance, VectorParams

from crewai.knowledge.storage.base_knowledge_storage import BaseKnowledgeStorage

__all__ = [
    "QdrantKnowledgeStorage",
]


class QdrantKnowledgeStorage(BaseKnowledgeStorage):
    """Qdrant implementation of the CrewAI knowledge storage contract."""

    # The Qdrant collection is created lazily on first use

    def __init__(
        self,
        collection_name: str,
        embedder: Optional[Any] = None,
        qdrant_url: str | None = None,
        prefer_grpc: bool = False,
    ) -> None:  # noqa: D401 – ctor
        self.collection_name: str = collection_name or "knowledge"
        self.embedder = embedder or self._default_embedder()
        self._client = QdrantClient(url=qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333"), prefer_grpc=prefer_grpc)
        self._vector_dim: Optional[int] = None  # filled on initialise
        # Explicit initialise to mirror original KnowledgeStorage API
        self.initialize_knowledge_storage()

    # ------------------------------------------------------------------
    # BaseKnowledgeStorage contract
    # ------------------------------------------------------------------

    def search(  # type: ignore[override]
        self,
        query: List[str],
        limit: int = 3,
        filter: Optional[dict] = None,
        score_threshold: float = 0.35,
    ) -> List[Dict[str, Any]]:
        if not query:
            return []

        # Qdrant currently supports single query vector → we take first element
        query_vector = self._embed_texts(query)[0]

        # Build filter conditions if provided (simple tag equality only)
        q_filter = None
        if filter:
            must = [qmodels.FieldCondition(key=k, match=qmodels.MatchValue(value=v)) for k, v in filter.items()]
            q_filter = qmodels.Filter(must=must)

        results = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=q_filter,  # type: ignore[arg-type]
            with_payload=True,
            with_vectors=False,
            limit=limit,
        )

        processed: List[Dict[str, Any]] = []
        for pt in results:
            score: float = pt.score or 0.0  # similarity score (higher = closer)
            if score < score_threshold:
                continue
            payload = pt.payload or {}
            processed.append(
                {
                    "id": pt.id,
                    "metadata": payload.get("metadata", {}),
                    "context": payload.get("document", ""),
                    "score": score,
                }
            )
        return processed

    def save(  # type: ignore[override]
        self,
        documents: List[str],
        metadata: Union[Dict[str, Any], List[Dict[str, Any]], None] = None,
    ) -> None:
        if not documents:
            return

        vectors: List[List[float]] = self._embed_texts(documents)

        # Handle metadata broadcast & per-doc values
        if metadata is None:
            metadata_list: List[Dict[str, Any]] = [{} for _ in documents]
        elif isinstance(metadata, list):
            metadata_list = metadata
        else:
            metadata_list = [metadata for _ in documents]

        points: List[qmodels.PointStruct] = []
        for doc, vector, meta in zip(documents, vectors, metadata_list):
            # Use SHA256 of content for deduplication (mirrors Chroma impl)
            doc_id = hashlib.sha256(doc.encode("utf-8")).hexdigest()
            # Prepare payload – keep document text for quick retrieval
            payload: Dict[str, Any] = {
                "document": doc,
                "metadata": meta or {},
            }
            points.append(qmodels.PointStruct(id=doc_id, vector=vector, payload=payload))

        # Upsert into Qdrant
        self._client.upsert(collection_name=self.collection_name, points=points)

    def reset(self) -> None:  # type: ignore[override]
        self._client.delete_collection(self.collection_name, wait=True)
        self.initialize_knowledge_storage()

    # ------------------------------------------------------------------
    # Public helper expected by Knowledge.__init__ ----------------------
    # ------------------------------------------------------------------

    def initialize_knowledge_storage(self):  # noqa: D401 – match Chroma API
        # Ensure collection exists with correct vector size
        if self._vector_dim is None:
            # Lazy embed to determine dimension (costly but only once)
            self._vector_dim = len(self._embed_texts(["placeholder"])[0])

        if self.collection_name not in {c.name for c in self._client.get_collections().collections}:
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self._vector_dim, distance=Distance.COSINE),
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        """Return list of embedding vectors for `texts`."""
        # If the configured embedder is a callable (e.g., from Chroma utils) we
        # can call it directly.  Otherwise default to OpenAI function.
        if callable(self.embedder):
            return self.embedder(texts)  # type: ignore[arg-type]
        else:
            # Fallback – assume OpenAI model string supplied
            response = openai.embeddings.create(model=str(self.embedder), input=list(texts))
            # openai>=1.0 returns .data list with .embedding
            return [d.embedding for d in response.data]  # type: ignore[attr-defined]

    @staticmethod
    def _default_embedder():
        """Return a simple OpenAI embedding function (list[str] -> list[list[float]])."""

        def _embed(texts: Sequence[str]) -> List[List[float]]:  # type: ignore[return-type]
            response = openai.embeddings.create(model="text-embedding-3-small", input=list(texts))
            return [d.embedding for d in response.data]  # type: ignore[attr-defined]

        return _embed 