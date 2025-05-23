from typing import Any, Dict, List, Optional
from datetime import datetime

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class ContextManager:
    """
    Enhanced context manager with normalized memory layer support.
    
    This manager provides high-level context operations that leverage
    Golett's normalized three-layer memory architecture for optimal
    storage and retrieval based on content type and importance.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the context manager.
        
        Args:
            memory_manager: The memory manager instance
        """
        self.memory_manager = memory_manager
        logger.debug("Context manager initialized with normalized layer support")
    
    def store_knowledge_context(
        self,
        session_id: str,
        content: Any,
        source: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None,
        importance: Optional[float] = None
    ) -> str:
        """
        Store knowledge-related contextual information in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            content: The knowledge content to store
            source: Source of the knowledge (e.g., "document", "api", "user")
            description: Optional human-readable description
            tags: Optional tags for categorization
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            importance: Importance score (auto-determined if None)
            
        Returns:
            The context entry ID
        """
        # Determine importance if not provided
        if importance is None:
            importance = 0.7  # Knowledge context is typically important
        
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
            importance=importance,
            metadata=combined_metadata,
            memory_layer=memory_layer
        )
    
    def store_crew_context(
        self,
        session_id: str,
        crew_id: str,
        context_type: str,
        data: Any,
        importance: float = 0.6,
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None
    ) -> str:
        """
        Store crew-specific contextual information in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            crew_id: The ID of the crew this context relates to
            context_type: Type of crew context (e.g., "decision", "intermediate_result")
            data: The context data to store
            importance: Importance score (0.0-1.0)
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            
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
            metadata=combined_metadata,
            memory_layer=memory_layer
        )
    
    def retrieve_knowledge_for_query(
        self,
        session_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        limit: int = 5,
        include_layers: Optional[List[MemoryLayer]] = None,
        cross_session: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge context relevant to a query across memory layers.
        
        Args:
            session_id: The session ID
            query: The query to search for
            tags: Optional list of tags to filter by
            sources: Optional list of sources to filter by
            limit: Maximum number of results to return
            include_layers: Memory layers to search (default: all layers)
            cross_session: Whether to include cross-session results
            
        Returns:
            List of relevant knowledge context entries
        """
        # Default to searching knowledge-relevant layers
        if include_layers is None:
            include_layers = [MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
        
        results = self.memory_manager.retrieve_context(
            session_id=session_id,
            query=query,
            context_types=["knowledge"],
            limit=limit,
            include_layers=include_layers,
            cross_session=cross_session
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
        crew_id: str,
        context_type: Optional[str] = None,
        limit: int = 10,
        include_layers: Optional[List[MemoryLayer]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve crew-specific context across memory layers.
        
        Args:
            session_id: The session ID
            crew_id: The crew ID to filter by
            context_type: Optional context subtype to filter by
            limit: Maximum number of results to return
            include_layers: Memory layers to search (default: short-term and in-session)
            
        Returns:
            List of crew context entries
        """
        # Default to crew-relevant layers
        if include_layers is None:
            include_layers = [MemoryLayer.SHORT_TERM, MemoryLayer.IN_SESSION]
        
        results = self.memory_manager.retrieve_context(
            session_id=session_id,
            query="",  # Empty query to get recent items
            context_types=["crew_context"],
            limit=limit,
            include_layers=include_layers,
            cross_session=False
        )
        
        # Filter by crew_id and context_type
        filtered_results = []
        for item in results:
            metadata = item.get("metadata", {})
            
            # Filter by crew_id
            if metadata.get("crew_id") != crew_id:
                continue
            
            # Filter by context_type if specified
            if context_type and metadata.get("context_subtype") != context_type:
                continue
            
            filtered_results.append(item)
        
        return filtered_results
    
    def store_bi_context(
        self,
        session_id: str,
        data_type: str,
        data: Any,
        description: str,
        importance: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None
    ) -> str:
        """
        Store BI-related context in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            data_type: Type of BI data
            data: The BI data to store
            description: Human-readable description
            importance: Importance score (0.0-1.0)
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            
        Returns:
            The context entry ID
        """
        return self.memory_manager.store_bi_data(
            session_id=session_id,
            data_type=data_type,
            data=data,
            description=description,
            importance=importance,
            metadata=metadata,
            memory_layer=memory_layer
        )
    
    def retrieve_bi_context(
        self,
        session_id: str,
        query: str,
        data_types: Optional[List[str]] = None,
        limit: int = 5,
        include_layers: Optional[List[MemoryLayer]] = None,
        cross_session: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve BI context across memory layers.
        
        Args:
            session_id: The session ID
            query: The search query
            data_types: Optional list of BI data types to filter by
            limit: Maximum number of results to return
            include_layers: Memory layers to search (default: long-term and short-term)
            cross_session: Whether to include cross-session results
            
        Returns:
            List of relevant BI context entries
        """
        return self.memory_manager.retrieve_bi_data(
            session_id=session_id,
            query=query,
            data_types=data_types,
            limit=limit,
            include_layers=include_layers,
            cross_session=cross_session
        )
    
    def get_layer_context_summary(
        self,
        session_id: str,
        layer: MemoryLayer,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get a summary of context stored in a specific memory layer.
        
        Args:
            session_id: The session ID
            layer: The memory layer to summarize
            limit: Maximum number of items to include in summary
            
        Returns:
            Summary of layer context
        """
        # Get context from the specific layer
        results = self.memory_manager.retrieve_context(
            session_id=session_id,
            query="",  # Empty query to get recent items
            limit=limit,
            include_layers=[layer],
            cross_session=(layer == MemoryLayer.LONG_TERM)
        )
        
        # Analyze context types and create summary
        context_types = {}
        total_items = len(results)
        
        for item in results:
            context_type = item.get("metadata", {}).get("context_type", "unknown")
            if context_type not in context_types:
                context_types[context_type] = 0
            context_types[context_type] += 1
        
        return {
            "layer": layer.value,
            "total_items": total_items,
            "context_types": context_types,
            "sample_items": results[:5],  # First 5 items as samples
            "layer_config": self.memory_manager.layer_configs.get(layer, {}),
            "generated_at": datetime.now().isoformat()
        }

    def store_conversation_summary(
        self,
        session_id: str,
        summary: str,
        start_time: str,
        end_time: str,
        topics: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None
    ) -> str:
        """
        Store a conversation summary in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            summary: The conversation summary text
            start_time: Start time of the conversation segment
            end_time: End time of the conversation segment
            topics: List of topics covered in the summary
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            
        Returns:
            The context entry ID
        """
        combined_metadata = {
            "start_time": start_time,
            "end_time": end_time,
            "topics": topics,
            "summary_type": "conversation",
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            combined_metadata.update(metadata)
        
        return self.memory_manager.store_context(
            session_id=session_id,
            context_type="conversation_summary",
            data=summary,
            importance=0.6,  # Summaries are moderately important
            metadata=combined_metadata,
            memory_layer=memory_layer
        )

    def retrieve_conversation_summaries(
        self,
        session_id: str,
        query: Optional[str] = None,
        topics: Optional[List[str]] = None,
        limit: int = 5,
        include_layers: Optional[List[MemoryLayer]] = None,
        cross_session: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation summaries relevant to a query or topics.
        
        Args:
            session_id: The session ID
            query: Optional search query
            topics: Optional list of topics to filter by
            limit: Maximum number of results to return
            include_layers: Memory layers to search (default: short-term and long-term)
            cross_session: Whether to include cross-session results
            
        Returns:
            List of relevant conversation summaries
        """
        # Default to summary-relevant layers
        if include_layers is None:
            include_layers = [MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
        
        results = self.memory_manager.retrieve_context(
            session_id=session_id,
            query=query or "",
            context_types=["conversation_summary"],
            limit=limit,
            include_layers=include_layers,
            cross_session=cross_session
        )
        
        # Apply topic filters if specified
        if topics:
            filtered_results = []
            for item in results:
                metadata = item.get("metadata", {})
                summary_topics = metadata.get("topics", [])
                
                # Check if any of the requested topics are in the summary topics
                if any(topic in summary_topics for topic in topics):
                    filtered_results.append(item)
            
            return filtered_results
        
        return results 