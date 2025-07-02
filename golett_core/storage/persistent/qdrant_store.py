import os
from typing import List, Optional
from uuid import UUID

from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams

from golett_core.schemas import Document
from golett_core.interfaces import VectorStoreInterface


class QdrantVectorStore(VectorStoreInterface):
    def __init__(self, url: Optional[str] = None, collection_name: str = "golett_documents"):
        if url is None:
            url = os.getenv("QDRANT_URL")
            if not url:
                raise ValueError("Qdrant URL must be provided via argument or QDRANT_URL env var")
        self.client = QdrantClient(url)
        self.collection_name = collection_name
        
        # Ensure collection exists
        try:
            self.client.get_collection(collection_name=self.collection_name)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE), # Assuming OpenAI embeddings
            )

    def add(self, documents: List[Document]):
        points = [
            models.PointStruct(
                id=str(doc.id),
                vector=doc.embedding,
                payload=doc.metadata,
            ) for doc in documents
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Document]:
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
        
        return [
            Document(
                id=hit.id,
                embedding=hit.vector, # Note: Qdrant doesn't return the vector by default on search
                metadata=hit.payload
            ) for hit in search_result
        ] 