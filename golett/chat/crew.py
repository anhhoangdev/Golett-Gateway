from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import inspect

try:
    from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    BaseKnowledgeSource = object

from crewai.knowledge.knowledge import Knowledge
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.utils.logger import get_logger
from golett.knowledge.sources import (
    GolettAdvancedTextFileKnowledgeSource, 
    GolettAdvancedMemoryKnowledgeSource,
    KnowledgeRetrievalStrategy
)

logger = get_logger(__name__)

class GolettKnowledgeAdapter:
    """
    Enhanced knowledge adapter with normalized memory layer support.
    
    This adapter provides seamless integration between CrewAI knowledge sources
    and Golett's sophisticated three-layer memory architecture, enabling
    advanced knowledge management with proper layer separation and routing.
    """
    
    def __init__(
        self, 
        memory_manager: MemoryManager,
        session_id: str,
        enable_advanced_features: bool = True,
        default_memory_layer: MemoryLayer = MemoryLayer.LONG_TERM,
        cross_session_access: bool = True,
        max_knowledge_age_days: int = 30
    ):
        """
        Initialize the enhanced knowledge adapter.
        
        Args:
            memory_manager: Golett memory manager instance
            session_id: Session ID for knowledge operations
            enable_advanced_features: Whether to enable advanced Golett features
            default_memory_layer: Default memory layer for new knowledge
            cross_session_access: Whether to allow cross-session knowledge access
            max_knowledge_age_days: Maximum age of knowledge to retrieve
        """
        self.memory_manager = memory_manager
        self.session_id = session_id
        self.enable_advanced_features = enable_advanced_features
        self.default_memory_layer = default_memory_layer
        self.cross_session_access = cross_session_access
        self.max_knowledge_age_days = max_knowledge_age_days
        
        # Storage for different types of knowledge sources
        self.crewai_sources = []
        self.golett_sources = []
        self.collections = {}  # Track knowledge collections
        
        # Memory layer configurations
        self.layer_configs = {
            MemoryLayer.LONG_TERM: {
                "importance_threshold": 0.7,
                "max_results": 20,
                "cross_session": True,
                "retention_priority": "high"
            },
            MemoryLayer.SHORT_TERM: {
                "importance_threshold": 0.5,
                "max_results": 15,
                "cross_session": False,
                "retention_priority": "medium"
            },
            MemoryLayer.IN_SESSION: {
                "importance_threshold": 0.3,
                "max_results": 10,
                "cross_session": False,
                "retention_priority": "low"
            }
        }
        
        logger.info(f"Initialized enhanced Golett knowledge adapter for session {session_id} "
                   f"(advanced: {enable_advanced_features}, layer: {default_memory_layer.value})")
    
    def add_source(self, source: Any) -> None:
        """Add a knowledge source (CrewAI or Golett-native)."""
        if hasattr(source, '__class__') and 'Golett' in source.__class__.__name__:
            self.golett_sources.append(source)
            
            # Register collection if it's a file source (has collection_name and memory_layer)
            if hasattr(source, 'collection_name') and hasattr(source, 'memory_layer'):
                self._register_collection(source)
                
            logger.info(f"Added Golett-native knowledge source: {source.__class__.__name__}")
        else:
            self.crewai_sources.append(source)
            logger.info(f"Added CrewAI knowledge source: {source.__class__.__name__}")
    
    def add_advanced_file_source(
        self,
        file_path: str,
        collection_name: str,
        memory_layer: MemoryLayer = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.8,
        chunk_size: int = 1000,
        overlap_size: int = 100,
        enable_versioning: bool = True
    ) -> GolettAdvancedTextFileKnowledgeSource:
        """
        Add an advanced Golett file-based knowledge source.
        
        Args:
            file_path: Path to the text file
            collection_name: Name of the knowledge collection
            memory_layer: Target memory layer (uses default if None)
            tags: Optional tags for categorization
            importance: Importance score for the knowledge
            chunk_size: Maximum size of each chunk
            overlap_size: Overlap between chunks
            enable_versioning: Whether to enable versioning
            
        Returns:
            The created knowledge source
        """
        if memory_layer is None:
            memory_layer = self.default_memory_layer
        
        source = GolettAdvancedTextFileKnowledgeSource(
            file_path=file_path,
            memory_manager=self.memory_manager,
            session_id=self.session_id,
            collection_name=collection_name,
            memory_layer=memory_layer,
            tags=tags or [],
            importance=importance,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
            enable_versioning=enable_versioning
        )
        
        self.add_source(source)
        return source
    
    def add_advanced_memory_source(
        self,
        collection_names: Optional[List[str]] = None,
        memory_layers: Optional[List[MemoryLayer]] = None,
        context_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        importance_threshold: float = 0.3,
        cross_session: bool = None,
        max_age_days: int = None
    ) -> GolettAdvancedMemoryKnowledgeSource:
        """
        Add an advanced Golett memory-based knowledge source.
        
        Args:
            collection_names: Optional list of collection names to include
            memory_layers: Memory layers to access
            context_types: Optional list of context types to include
            tags: Optional tags to filter by
            importance_threshold: Minimum importance score for retrieval
            cross_session: Whether to include cross-session knowledge
            max_age_days: Maximum age of knowledge to retrieve
            
        Returns:
            The created knowledge source
        """
        if cross_session is None:
            cross_session = self.cross_session_access
        if max_age_days is None:
            max_age_days = self.max_knowledge_age_days
        if memory_layers is None:
            memory_layers = [MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
        
        source = GolettAdvancedMemoryKnowledgeSource(
            memory_manager=self.memory_manager,
            session_id=self.session_id,
            collection_names=collection_names,
            memory_layers=memory_layers,
            context_types=context_types,
            tags=tags,
            importance_threshold=importance_threshold,
            cross_session=cross_session,
            max_age_days=max_age_days
        )
        
        self.add_source(source)
        return source
    
    def retrieve_knowledge(
        self,
        query: str,
        limit: int = 10,
        strategy: KnowledgeRetrievalStrategy = KnowledgeRetrievalStrategy.HYBRID,
        include_layers: Optional[List[MemoryLayer]] = None,
        crewai_limit: int = 5,
        golett_limit: int = 5,
        memory_limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge from all sources using advanced strategies.
        
        Args:
            query: The search query
            limit: Maximum total results to return
            strategy: Retrieval strategy to use for Golett sources
            include_layers: Memory layers to search
            crewai_limit: Maximum results from CrewAI sources
            golett_limit: Maximum results from Golett file sources
            memory_limit: Maximum results from general memory
            
        Returns:
            Combined and ranked knowledge results
        """
        all_results = []
        
        # Retrieve from CrewAI sources
        if self.crewai_sources:
            for source in self.crewai_sources:
                try:
                    if hasattr(source, 'retrieve'):
                        crewai_results = source.retrieve(query, limit=crewai_limit)
                        # Add source information
                        for result in crewai_results:
                            result['source_type'] = 'crewai'
                            result['source_class'] = source.__class__.__name__
                        all_results.extend(crewai_results)
                except Exception as e:
                    logger.error(f"Error retrieving from CrewAI source {source.__class__.__name__}: {e}")
        
        # Retrieve from Golett file sources
        if self.golett_sources:
            for source in self.golett_sources:
                try:
                    if hasattr(source, 'retrieve'):
                        golett_results = source.retrieve(
                            query=query, 
                            limit=golett_limit,
                            strategy=strategy
                        )
                        # Add source information
                        for result in golett_results:
                            result['source_type'] = 'golett_file'
                            result['source_class'] = source.__class__.__name__
                            if hasattr(source, 'collection_name'):
                                result['collection_name'] = source.collection_name
                        all_results.extend(golett_results)
                except Exception as e:
                    logger.error(f"Error retrieving from Golett source {source.__class__.__name__}: {e}")
        
        # Retrieve from general memory if advanced features enabled
        if self.enable_advanced_features:
            try:
                memory_results = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query=query,
                    limit=memory_limit,
                    include_layers=include_layers,
                    cross_session=self.cross_session_access
                )
                # Add source information
                for result in memory_results:
                    result['source_type'] = 'golett_memory'
                    result['source_class'] = 'MemoryManager'
                all_results.extend(memory_results)
            except Exception as e:
                logger.error(f"Error retrieving from memory: {e}")
        
        # Sort and limit results
        sorted_results = self._rank_and_filter_results(all_results, limit)
        
        logger.debug(f"Retrieved {len(sorted_results)} knowledge results for query: {query[:50]}...")
        return sorted_results
    
    def _register_collection(self, source: Any) -> None:
        """Register a knowledge collection."""
        collection_name = getattr(source, 'collection_name', 'unknown')
        memory_layer = getattr(source, 'memory_layer', 'unknown')
        
        if collection_name not in self.collections:
            self.collections[collection_name] = {
                'sources': [],
                'memory_layers': set(),
                'created_at': datetime.now().isoformat(),
                'total_chunks': 0
            }
        
        collection = self.collections[collection_name]
        collection['sources'].append(source)
        collection['memory_layers'].add(memory_layer)
        
        # Update chunk count if available
        if hasattr(source, 'context_ids'):
            collection['total_chunks'] += len(getattr(source, 'context_ids', []))
    
    def _rank_and_filter_results(
        self, 
        results: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Rank and filter knowledge results."""
        # Remove duplicates based on content similarity
        unique_results = []
        seen_content = set()
        
        for result in results:
            # Extract content for deduplication
            content = ""
            if 'content' in result:
                content = str(result['content'])
            elif 'data' in result and isinstance(result['data'], dict):
                content = str(result['data'].get('content', ''))
            elif 'data' in result:
                content = str(result['data'])
            
            # Simple deduplication based on content hash
            content_hash = hash(content[:200])  # Use first 200 chars for hash
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        # Sort by relevance score if available, otherwise by importance
        def get_sort_key(item):
            # Try different score fields
            score = item.get('score', item.get('relevance_score', 0))
            importance = item.get('metadata', {}).get('importance', 0.5)
            
            # Boost Golett sources slightly
            source_boost = 0.1 if item.get('source_type', '').startswith('golett') else 0
            
            return score + importance + source_boost
        
        sorted_results = sorted(unique_results, key=get_sort_key, reverse=True)
        
        return sorted_results[:limit]
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a knowledge collection."""
        return self.collections.get(collection_name)
    
    def list_collections(self) -> Dict[str, Dict[str, Any]]:
        """List all registered knowledge collections."""
        return self.collections.copy()
    
    def get_memory_layer_stats(self) -> Dict[str, Any]:
        """Get statistics about memory layer usage."""
        if not self.enable_advanced_features:
            return {"message": "Advanced features not enabled"}
        
        return self.memory_manager.get_layer_statistics()
    
    def optimize_memory_layers(self) -> Dict[str, Any]:
        """Optimize memory layers by cleaning up expired content."""
        if not self.enable_advanced_features:
            return {"message": "Advanced features not enabled"}
        
        return self.memory_manager.cleanup_expired_memories(dry_run=False)
    
    def search_across_layers(
        self,
        query: str,
        limit: int = 10,
        include_layer_weights: bool = True
    ) -> List[Dict[str, Any]]:
        """Search across all memory layers with layer-aware ranking."""
        if not self.enable_advanced_features:
            return []
        
        return self.memory_manager.search_across_all_layers(
            query=query,
            session_id=self.session_id,
            limit=limit,
            include_layer_weights=include_layer_weights
        ) 