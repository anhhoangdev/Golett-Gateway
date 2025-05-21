import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

from golett.memory.storage.interface import BaseMemoryStorage
from golett.memory.storage.postgres import PostgresMemoryStorage
from golett.memory.storage.qdrant import QdrantMemoryStorage
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class MemoryManager:
    """
    Unified memory manager that integrates structured and vector-based storage.
    
    This class provides a high-level API for storing, retrieving, and searching
    information across both PostgreSQL (structured data) and Qdrant (vector-based)
    storage backends.
    """
    
    def __init__(
        self,
        postgres_connection: str,
        qdrant_url: str = "http://localhost:6333",
        postgres_table: str = "golett_memories",
        qdrant_collection: str = "golett_vectors",
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        """
        Initialize the memory manager with storage backends.
        
        Args:
            postgres_connection: PostgreSQL connection string
            qdrant_url: URL of the Qdrant server
            postgres_table: Name of the PostgreSQL table for structured data
            qdrant_collection: Name of the Qdrant collection for vector data
            embedding_model: Name of the embedding model to use
        """
        self.postgres = PostgresMemoryStorage(
            connection_string=postgres_connection,
            table_name=postgres_table
        )
        self.qdrant = QdrantMemoryStorage(
            collection_name=qdrant_collection, 
            url=qdrant_url,
            embedder_name=embedding_model
        )
        
        logger.info("Memory Manager initialized with PostgreSQL and Qdrant storage")
    
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new chat session.
        
        Args:
            metadata: Additional metadata for the session
            
        Returns:
            A unique session ID
        """
        session_id = str(uuid.uuid4())
        
        # Store session metadata
        session_data = {
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        
        # Add metadata if provided
        if metadata:
            session_data.update(metadata)
        
        # Save to both storage backends
        self.postgres.save(
            key=f"session:{session_id}",
            data=session_data,
            metadata={"type": "session", "session_id": session_id}
        )
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a message in the memory.
        
        Args:
            session_id: The session ID
            role: The role of the message sender (user, assistant, etc.)
            content: The message content
            metadata: Additional metadata for the message
            
        Returns:
            The message ID
        """
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create message data
        message_data = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        # Prepare metadata
        message_metadata = {
            "type": "message",
            "session_id": session_id,
            "message_id": message_id,
            "role": role,
            "timestamp": timestamp,
        }
        
        # Add additional metadata if provided
        if metadata:
            message_metadata.update(metadata)
        
        # Store in both backends
        # Structured storage for efficient retrieval
        self.postgres.save(
            key=f"message:{message_id}",
            data=message_data,
            metadata=message_metadata
        )
        
        # Vector storage for semantic search
        self.qdrant.save(
            key=f"message:{message_id}",
            data=content,
            metadata=message_metadata
        )
        
        logger.debug(f"Stored message in session {session_id}: {role}")
        return message_id
    
    def get_session_history(
        self, 
        session_id: str, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get the message history for a session.
        
        Args:
            session_id: The session ID
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in chronological order
        """
        # Use PostgreSQL to get structured message history
        history = self.postgres.search(
            query={"type": "message"},
            limit=limit,
            session_id=session_id
        )
        
        # Sort by timestamp
        return sorted(history, key=lambda x: x.get('metadata', {}).get('timestamp', ''))
    
    def search_message_history(
        self, 
        query: str,
        session_id: Optional[str] = None,
        limit: int = 5,
        semantic: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search through message history.
        
        Args:
            query: The search query
            session_id: Optional session ID to filter by
            limit: Maximum number of results to return
            semantic: Whether to use semantic search (True) or text search (False)
            
        Returns:
            List of matching messages
        """
        if semantic:
            # Use Qdrant for semantic search
            kwargs = {}
            if session_id:
                kwargs["session_id"] = session_id
                
            results = self.qdrant.search(
                query=query,
                limit=limit,
                **kwargs
            )
            return results
        else:
            # Use PostgreSQL for text search
            kwargs = {}
            if session_id:
                kwargs["session_id"] = session_id
                
            return self.postgres.search(
                query=query,
                limit=limit,
                **kwargs
            )
    
    def store_context(
        self,
        session_id: str,
        context_type: str,
        data: Any,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store contextual information.
        
        Args:
            session_id: The session ID
            context_type: Type of context (e.g., "bi_data", "entity", "decision")
            data: The context data to store
            importance: Importance score (0.0-1.0) for retrieval prioritization
            metadata: Additional metadata
            
        Returns:
            The context entry ID
        """
        context_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Prepare metadata
        context_metadata = {
            "type": "context",
            "context_type": context_type,
            "session_id": session_id,
            "context_id": context_id,
            "timestamp": timestamp,
            "importance": importance,
        }
        
        # Add additional metadata if provided
        if metadata:
            context_metadata.update(metadata)
        
        # Store in both backends for different retrieval patterns
        key = f"context:{context_type}:{context_id}"
        
        # Structured storage
        self.postgres.save(
            key=key,
            data=data,
            metadata=context_metadata
        )
        
        # Vector storage for semantic retrieval
        self.qdrant.save(
            key=key,
            data=data,
            metadata=context_metadata
        )
        
        logger.debug(f"Stored {context_type} context in session {session_id}")
        return context_id
    
    def retrieve_context(
        self,
        session_id: str,
        query: str,
        context_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            session_id: The session ID
            query: The query to find relevant context for
            context_types: Optional list of context types to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of relevant context entries
        """
        # Build filter conditions
        kwargs = {"session_id": session_id}
        
        # Search using vector similarity
        results = self.qdrant.search(
            query=query,
            limit=limit,
            **kwargs
        )
        
        # Filter by context type if specified
        if context_types:
            results = [
                r for r in results 
                if r.get("metadata", {}).get("context_type") in context_types
            ]
        
        return results
    
    def store_bi_data(
        self,
        session_id: str,
        data_type: str,
        data: Any,
        description: str,
        importance: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store BI-related data.
        
        Args:
            session_id: The session ID
            data_type: Type of BI data (e.g., "metric", "report", "dashboard")
            data: The BI data to store
            description: Human-readable description of the data
            importance: Importance score (0.0-1.0)
            metadata: Additional metadata
            
        Returns:
            The data entry ID
        """
        # Prepare metadata
        bi_metadata = {
            "data_type": data_type,
            "description": description,
        }
        
        # Add additional metadata if provided
        if metadata:
            bi_metadata.update(metadata)
        
        # Store as context
        return self.store_context(
            session_id=session_id,
            context_type="bi_data",
            data=data,
            importance=importance,
            metadata=bi_metadata
        )
    
    def retrieve_bi_data(
        self,
        session_id: str,
        query: str,
        data_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant BI data for a query.
        
        Args:
            session_id: The session ID
            query: The query to find relevant BI data for
            data_types: Optional list of BI data types to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of relevant BI data entries
        """
        # Get all BI context
        results = self.retrieve_context(
            session_id=session_id,
            query=query,
            context_types=["bi_data"],
            limit=limit
        )
        
        # Filter by data type if specified
        if data_types:
            results = [
                r for r in results 
                if r.get("metadata", {}).get("data_type") in data_types
            ]
        
        return results
    
    def store_decision(
        self,
        session_id: str,
        decision_type: str,
        description: str,
        reasoning: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store an agent's decision.
        
        Args:
            session_id: The session ID
            decision_type: Type of decision (e.g., "use_data", "response_mode")
            description: Short description of the decision
            reasoning: Detailed reasoning for the decision
            metadata: Additional metadata
            
        Returns:
            The decision entry ID
        """
        decision_data = {
            "decision_type": decision_type,
            "description": description,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store as context with high importance
        return self.store_context(
            session_id=session_id,
            context_type="decision",
            data=decision_data,
            importance=0.8,  # Decisions are important for context
            metadata=metadata or {}
        )
    
    def get_recent_decisions(
        self,
        session_id: str,
        decision_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent decisions for a session.
        
        Args:
            session_id: The session ID
            decision_type: Optional decision type to filter by
            limit: Maximum number of decisions to return
            
        Returns:
            List of recent decisions
        """
        # Build query
        query = {"type": "context", "context_type": "decision"}
        if decision_type:
            query["data_type"] = decision_type
        
        # Use PostgreSQL for structured query
        decisions = self.postgres.search(
            query=query,
            limit=limit,
            session_id=session_id
        )
        
        # Sort by timestamp (newest first)
        return sorted(
            decisions, 
            key=lambda x: x.get('data', {}).get('timestamp', ''),
            reverse=True
        )
    
    def reset(self) -> None:
        """Reset all memory stores."""
        self.postgres.reset()
        self.qdrant.reset()
        logger.info("Memory Manager reset complete") 