from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime

from golett.memory.memory_manager import MemoryManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class ContextManager:
    """
    Manages contextual information for conversational agents and crews.
    
    This class provides specialized methods for storing, retrieving, and
    organizing different types of contextual information that agents
    might need during conversations.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the context manager.
        
        Args:
            memory_manager: The memory manager instance to use for storage
        """
        self.memory_manager = memory_manager
        logger.info("Context Manager initialized")
    
    def store_knowledge_context(
        self,
        session_id: str,
        content: Any,
        source: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store knowledge-related contextual information.
        
        Args:
            session_id: The session ID
            content: The knowledge content to store
            source: Source of the knowledge (e.g., "document", "api", "user")
            description: Optional human-readable description
            tags: Optional tags for categorization
            metadata: Additional metadata
            
        Returns:
            The context entry ID
        """
        combined_metadata = {
            "source": source,
            "description": description or "Knowledge context",
            "tags": tags or [],
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            combined_metadata.update(metadata)
        
        return self.memory_manager.store_context(
            session_id=session_id,
            context_type="knowledge",
            data=content,
            importance=0.7,  # Knowledge context is typically important
            metadata=combined_metadata
        )
    
    def store_crew_context(
        self,
        session_id: str,
        crew_id: str,
        context_type: str,
        data: Any,
        importance: float = 0.6,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store crew-specific contextual information.
        
        Args:
            session_id: The session ID
            crew_id: The ID of the crew this context relates to
            context_type: Type of crew context (e.g., "decision", "intermediate_result")
            data: The context data to store
            importance: Importance score (0.0-1.0)
            metadata: Additional metadata
            
        Returns:
            The context entry ID
        """
        combined_metadata = {
            "crew_id": crew_id,
            "context_subtype": context_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            combined_metadata.update(metadata)
        
        return self.memory_manager.store_context(
            session_id=session_id,
            context_type="crew_context",
            data=data,
            importance=importance,
            metadata=combined_metadata
        )
    
    def retrieve_knowledge_for_query(
        self,
        session_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge context relevant to a query.
        
        Args:
            session_id: The session ID
            query: The query to search for
            tags: Optional list of tags to filter by
            sources: Optional list of sources to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of relevant knowledge context entries
        """
        results = self.memory_manager.retrieve_context(
            session_id=session_id,
            query=query,
            context_types=["knowledge"],
            limit=limit
        )
        
        # Apply additional filters
        if tags or sources:
            filtered_results = []
            for item in results:
                metadata = item.get("metadata", {})
                
                # Filter by tags if specified
                if tags and not any(tag in metadata.get("tags", []) for tag in tags):
                    continue
                
                # Filter by sources if specified
                if sources and metadata.get("source") not in sources:
                    continue
                
                filtered_results.append(item)
            
            return filtered_results
        
        return results
    
    def retrieve_crew_context(
        self,
        session_id: str,
        crew_id: Optional[str] = None,
        context_type: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve crew-specific context.
        
        Args:
            session_id: The session ID
            crew_id: Optional crew ID to filter by
            context_type: Optional context subtype to filter by
            query: Optional query for semantic search
            limit: Maximum number of results to return
            
        Returns:
            List of relevant crew context entries
        """
        if query:
            # Use semantic search first
            results = self.memory_manager.retrieve_context(
                session_id=session_id,
                query=query,
                context_types=["crew_context"],
                limit=limit
            )
        else:
            # Use structured search
            query = {"type": "context", "context_type": "crew_context"}
            results = self.memory_manager.postgres.search(
                query=query,
                limit=limit,
                session_id=session_id
            )
        
        # Apply additional filters
        if crew_id or context_type:
            filtered_results = []
            for item in results:
                metadata = item.get("metadata", {})
                
                # Filter by crew_id if specified
                if crew_id and metadata.get("crew_id") != crew_id:
                    continue
                
                # Filter by context_subtype if specified
                if context_type and metadata.get("context_subtype") != context_type:
                    continue
                
                filtered_results.append(item)
            
            return filtered_results
        
        return results
    
    def store_conversation_summary(
        self,
        session_id: str,
        summary: str,
        start_time: str,
        end_time: str,
        topics: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a summary of part of a conversation.
        
        Args:
            session_id: The session ID
            summary: The conversation summary
            start_time: Timestamp for the start of the summarized period
            end_time: Timestamp for the end of the summarized period
            topics: List of topics discussed in this summary
            metadata: Additional metadata
            
        Returns:
            The context entry ID
        """
        summary_data = {
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "topics": topics
        }
        
        combined_metadata = {
            "start_time": start_time,
            "end_time": end_time,
            "topics": topics
        }
        
        if metadata:
            combined_metadata.update(metadata)
        
        return self.memory_manager.store_context(
            session_id=session_id,
            context_type="conversation_summary",
            data=summary_data,
            importance=0.8,  # Summaries are important for context
            metadata=combined_metadata
        )
    
    def retrieve_conversation_summaries(
        self,
        session_id: str,
        topic: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation summaries.
        
        Args:
            session_id: The session ID
            topic: Optional topic to filter by
            query: Optional query for semantic search
            limit: Maximum number of summaries to return
            
        Returns:
            List of conversation summaries
        """
        if query:
            # Use semantic search if query provided
            results = self.memory_manager.retrieve_context(
                session_id=session_id,
                query=query,
                context_types=["conversation_summary"],
                limit=limit
            )
        else:
            # Use structured search
            query = {"type": "context", "context_type": "conversation_summary"}
            results = self.memory_manager.postgres.search(
                query=query,
                limit=limit,
                session_id=session_id
            )
        
        # Filter by topic if specified
        if topic:
            filtered_results = []
            for item in results:
                topics = item.get("data", {}).get("topics", [])
                if topic.lower() in [t.lower() for t in topics]:
                    filtered_results.append(item)
            
            return filtered_results
        
        return results 