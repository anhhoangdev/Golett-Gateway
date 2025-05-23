import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
    
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams
except ImportError:
    raise ImportError(
        "Qdrant support requires qdrant-client. "
        "Please install it with: pip install qdrant-client"
    )

from golett.memory.storage.interface import BaseMemoryStorage
from golett.utils.logger import get_logger
from golett.utils.embeddings import get_embedding_model

logger = get_logger(__name__)

class QdrantMemoryStorage(BaseMemoryStorage):
    """
    Qdrant implementation for storing and retrieving vector-based memory.
    
    This class manages semantic search capabilities for the system,
    storing embeddings for more effective retrieval of contextually
    similar information.
    """

    def __init__(
        self,
        collection_name: str,
        url: str = "http://localhost:6333",
        embedder_name: str = "text-embedding-3-small",
        vector_size: int = 1536,  # Default for text-embedding-3-small
    ) -> None:
        """
        Initialize the Qdrant storage.
        
        Args:
            collection_name: Name of the collection to store vectors in
            url: URL of the Qdrant server
            embedder_name: Name of the embedding model to use
            vector_size: Size of the embedding vectors
        """
        self.collection_name = collection_name
        self.url = url
        self.vector_size = vector_size
        self.embedder_name = embedder_name
        self.embedder = None
        self.initialize()

    def _initialize_embedder(self):
        """Initialize the embedding model."""
        self.embedder = get_embedding_model(self.embedder_name)
        if not self.embedder:
            logger.error(f"Failed to initialize embedder: {self.embedder_name}")
            raise ValueError(f"Could not initialize embedder: {self.embedder_name}")
            
    def _get_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text."""
        if not self.embedder:
            self._initialize_embedder()
        
        if isinstance(text, dict):
            # If input is a dictionary, convert to string representation
            text = json.dumps(text)
            
        embedding = self.embedder.embed_query(text)
        return embedding
        
    def initialize(self) -> None:
        """
        Initialize the Qdrant client and create collection if it doesn't exist.
        """
        try:
            self.client = QdrantClient(url=self.url)
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                # Create new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created new Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
                
            self._initialize_embedder()
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {e}")
            raise

    def save(self, key: str, data: Any, metadata: Dict[str, Any]) -> str:
        """
        Save data with its embedding to Qdrant.
        
        Args:
            key: Unique identifier for this memory entry
            data: The data to be stored (text or structured data)
            metadata: Additional context information
            
        Returns:
            The ID of the saved entry
        """
        try:
            # Generate a unique ID
            entry_id = str(uuid.uuid4())
            
            # Convert data to string if it's a dictionary
            text_for_embedding = data
            if isinstance(data, dict):
                text_for_embedding = json.dumps(data)
            
            # Generate embedding
            embedding = self._get_embedding(text_for_embedding)
            
            # Add created/updated timestamps
            now = datetime.now().isoformat()
            metadata.update({
                "key": key,
                "created_at": now,
                "updated_at": now
            })
            
            # Add point to collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=entry_id,
                        vector=embedding,
                        payload={
                            "key": key,
                            "data": data if isinstance(data, dict) else {"content": data},
                            "metadata": metadata
                        }
                    )
                ]
            )
            logger.debug(f"Saved vector memory with key: {key}, id: {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Error saving to Qdrant: {e}")
            raise

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific memory entry by key.
        
        This implementation will search for the most recent entry with the given key.
        
        Args:
            key: The identifier of the memory to retrieve
            
        Returns:
            The memory entry if found, None otherwise
        """
        try:
            # Search for entries with the given key
            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="payload.key",
                        match=models.MatchValue(value=key)
                    )
                ]
            )
            
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                filter=filter_query,
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            
            # Get the first result if any
            if search_result[0]:
                point = search_result[0][0]
                return {
                    "id": point.id,
                    "key": point.payload["key"],
                    "data": point.payload["data"],
                    "metadata": point.payload["metadata"]
                }
            return None
        except Exception as e:
            logger.error(f"Error loading from Qdrant: {e}")
            return None

    def search(self, query: Any, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for semantically similar entries.
        
        Args:
            query: The search query (text or structured data)
            limit: Maximum number of results to return
            **kwargs: Additional search parameters including:
                - session_id: Filter by session
                - score_threshold: Minimum similarity score (0.0-1.0)
                
        Returns:
            List of matching memory entries with similarity scores
        """
        try:
            # Generate embedding for the query
            query_embedding = self._get_embedding(query)
            
            # Build filter conditions
            filter_conditions = []
            
            if "session_id" in kwargs and kwargs["session_id"]:
                filter_conditions.append(
                    models.FieldCondition(
                        key="payload.metadata.session_id",
                        match=models.MatchValue(value=kwargs["session_id"])
                    )
                )
            
            # Set up filter if we have conditions
            filter_query = None
            if filter_conditions:
                filter_query = models.Filter(
                    must=filter_conditions
                )
            
            # Set score threshold if provided (lowered default from 0.7 to 0.3)
            score_threshold = kwargs.get("score_threshold", 0.3)
            
            logger.debug(f"Qdrant search: query='{query}', session_id={kwargs.get('session_id')}, "
                        f"threshold={score_threshold}, limit={limit}")
            
            # Search in collection
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=filter_query,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            logger.debug(f"Qdrant search returned {len(search_result)} results")
            
            # Format results
            results = []
            for scored_point in search_result:
                result = {
                    "id": scored_point.id,
                    "key": scored_point.payload["key"],
                    "data": scored_point.payload["data"],
                    "metadata": scored_point.payload["metadata"],
                    "similarity_score": scored_point.score
                }
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching in Qdrant: {e}")
            return []

    def delete(self, key: str) -> bool:
        """
        Delete entries with the specified key.
        
        Args:
            key: The identifier of the memories to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all points with the given key
            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="payload.key",
                        match=models.MatchValue(value=key)
                    )
                ]
            )
            
            # Get all matching points
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                filter=filter_query,
                limit=100,  # Limit to avoid too many results
                with_payload=False,
                with_vectors=False
            )
            
            # Extract IDs
            if search_result[0]:
                point_ids = [point.id for point in search_result[0]]
                
                # Delete the points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
                
                logger.info(f"Deleted {len(point_ids)} vector entries with key: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from Qdrant: {e}")
            return False

    def reset(self) -> None:
        """Reset/clear all data from storage."""
        try:
            # Recreate the collection (fastest way to clear all data)
            self.client.delete_collection(collection_name=self.collection_name)
            
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Reset Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error resetting Qdrant collection: {e}")
            raise
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for entries by metadata fields.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory entries
        """
        if not metadata_filter:
            logger.warning("Empty filter for metadata search")
            return []
            
        try:
            # Build filter conditions for each metadata key
            filter_conditions = []
            
            for key, value in metadata_filter.items():
                filter_conditions.append(
                    models.FieldCondition(
                        key=f"payload.metadata.{key}",
                        match=models.MatchValue(value=value)
                    )
                )
            
            # Set up filter
            filter_query = models.Filter(
                must=filter_conditions
            )
            
            # Search in collection
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                filter=filter_query,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            results = []
            if search_result[0]:
                for point in search_result[0]:
                    result = {
                        "id": point.id,
                        "key": point.payload["key"],
                        "data": point.payload["data"],
                        "metadata": point.payload["metadata"]
                    }
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching by metadata in Qdrant: {e}")
            return [] 