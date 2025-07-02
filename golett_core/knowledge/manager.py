from __future__ import annotations
from typing import List
from pathlib import Path

from golett_core.interfaces import KnowledgeInterface
from golett_core.schemas import Document, ChatMessage
from golett_core.knowledge.qdrant_knowledge import QdrantKnowledge as Knowledge


class KnowledgeManager(KnowledgeInterface):
    def __init__(
        self,
        collection_name: str,
        base_path: str | Path | None = None,
        embedder_config: dict | None = None,
    ) -> None:
        from pathlib import Path

        self._base_path = Path(base_path or "documents").expanduser().resolve()
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._knowledge = Knowledge(
            collection_name=collection_name,
            sources=[],
            embedder=embedder_config,
        )

    async def ingest_document(self, doc: Document) -> None:
        import os
        path = Path(doc.source_uri)
        if not path.is_absolute():
            path = self._base_path / path

        if not path.exists():
            raise FileNotFoundError(path)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        self._knowledge.storage.save([text], metadata={"user_id": doc.user_id})

    async def ingest_directory(self, directory: str | None = None, user_id: str | None = None) -> None:
        from pathlib import Path
        dir_path = Path(directory or self._base_path).expanduser().resolve()
        if not dir_path.exists():
            raise FileNotFoundError(dir_path)

        for file_path in dir_path.rglob("*.*"):
            if file_path.suffix.lower() not in {".txt", ".md", ".html"}:
                continue
            doc = Document(user_id=user_id or "anonymous", source_uri=str(file_path))
            await self.ingest_document(doc)

    async def get_retrieval_context(
        self,
        query: str,
        user_id: str | None = None,
        chat_history: List[ChatMessage] | None = None,
        top_k: int = 5,
    ) -> List[str]:
        filter_dict = {"user_id": user_id} if user_id else None
        results = self._knowledge.query([query], results_limit=top_k, score_threshold=0.0)
        return [r["context"] for r in results]

    def reset(self) -> None:
        self._knowledge.reset() 