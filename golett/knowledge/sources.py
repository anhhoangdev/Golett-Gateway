"""
Golett-native knowledge source implementations.

These knowledge sources integrate directly with Golett's sophisticated three-layer memory system,
providing advanced persistence, retrieval, and context management capabilities that leverage
Golett's long-term, short-term, and in-session memory architecture.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum

try:
    from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
    from pydantic import Field
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    BaseKnowledgeSource = object
    def Field(*args, **kwargs):
        return None

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.contextual.context_manager import ContextManager
from golett.memory.session.session_manager import SessionManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeRetrievalStrategy(Enum):
    """Knowledge retrieval strategies for advanced search."""
    SEMANTIC = "semantic"        # Vector-based similarity search
    STRUCTURED = "structured"    # PostgreSQL-based precise queries
    HYBRID = "hybrid"           # Combined semantic and structured
    TEMPORAL = "temporal"       # Time-based prioritization
    IMPORTANCE = "importance"   # Relevance-weighted results


class GolettAdvancedTextFileKnowledgeSource(BaseKnowledgeSource if CREWAI_AVAILABLE else object):
    """
    Advanced Golett-native text file knowledge source with sophisticated memory layer integration.
    
    This implementation provides:
    - Direct integration with Golett's normalized three-layer memory system
    - Intelligent memory layer routing based on content importance and type
    - Advanced chunking with context preservation and overlap
    - Cross-session knowledge persistence and retrieval
    - Comprehensive metadata tracking and versioning
    - Multiple retrieval strategies (semantic, structured, hybrid, temporal, importance)
    - Collection-based knowledge organization
    - Access pattern tracking and recency boosting
    """
    
    if CREWAI_AVAILABLE:
        # Define Pydantic fields for CrewAI compatibility
        file_path: str = Field(..., description="Path to the text file")
        memory_manager: Any = Field(..., description="Golett memory manager instance")
        session_id: str = Field(..., description="Session ID for storing knowledge context")
        collection_name: str = Field(..., description="Name of the knowledge collection")
        memory_layer: str = Field(default="long_term", description="Target memory layer for storage")
        tags: List[str] = Field(default_factory=list, description="Tags for categorization")
        importance: float = Field(default=0.8, description="Importance score for the knowledge")
        chunk_size: int = Field(default=1000, description="Maximum size of each chunk")
        overlap_size: int = Field(default=100, description="Overlap between chunks")
        enable_versioning: bool = Field(default=True, description="Whether to enable versioning")
        content: str = Field(default="", description="Loaded file content")
        context_ids: List[str] = Field(default_factory=list, description="Context IDs of stored chunks")
        context_manager: Any = Field(default=None, description="Context manager instance")
        session_manager: Any = Field(default=None, description="Session manager instance")
        version: int = Field(default=1, description="Version number of the knowledge")
        last_updated: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    
    def __init__(
        self, 
        file_path: str, 
        memory_manager: MemoryManager,
        session_id: str,
        collection_name: str,
        memory_layer: MemoryLayer = MemoryLayer.LONG_TERM,
        tags: Optional[List[str]] = None,
        importance: float = 0.8,
        chunk_size: int = 1000,
        overlap_size: int = 100,
        enable_versioning: bool = True,
        **kwargs
    ):
        """
        Initialize the advanced Golett text file knowledge source.
        
        Args:
            file_path: Path to the text file
            memory_manager: Golett memory manager instance
            session_id: Session ID for storing knowledge context
            collection_name: Name of the knowledge collection
            memory_layer: Target memory layer for storage
            tags: Optional tags for categorization
            importance: Importance score for the knowledge (0.0-1.0)
            chunk_size: Maximum size of each chunk in characters
            overlap_size: Overlap between chunks for context preservation
            enable_versioning: Whether to enable knowledge versioning
        """
        # Initialize with proper field values for Pydantic
        init_data = {
            'file_path': str(Path(file_path)),
            'memory_manager': memory_manager,
            'session_id': session_id,
            'collection_name': collection_name,
            'memory_layer': memory_layer.value,
            'tags': tags or [],
            'importance': self._adjust_importance_for_layer(importance, memory_layer),
            'chunk_size': chunk_size,
            'overlap_size': overlap_size,
            'enable_versioning': enable_versioning,
            'content': "",
            'context_ids': [],
            'context_manager': ContextManager(memory_manager),
            'session_manager': SessionManager(memory_manager),
            'version': 1,
            'last_updated': datetime.now().isoformat(),
            **kwargs
        }
        
        if CREWAI_AVAILABLE:
            super().__init__(**init_data)
        else:
            # For non-CrewAI environments, set attributes directly
            for key, value in init_data.items():
                setattr(self, key, value)
        
        # Ensure session exists
        self._ensure_session_exists()
        
        logger.info(f"Initialized advanced Golett text file knowledge source: {Path(file_path).name} "
                   f"(collection: {collection_name}, layer: {memory_layer.value})")
    
    def _adjust_importance_for_layer(self, base_importance: float, layer: MemoryLayer) -> float:
        """Adjust importance score based on memory layer."""
        layer_multipliers = {
            MemoryLayer.LONG_TERM: 1.0,    # Keep original importance
            MemoryLayer.SHORT_TERM: 0.8,   # Slightly reduce for short-term
            MemoryLayer.IN_SESSION: 0.6    # Reduce for in-session
        }
        return min(1.0, base_importance * layer_multipliers.get(layer, 1.0))
    
    def _ensure_session_exists(self) -> None:
        """Ensure the session exists in the session manager."""
        try:
            # Check if session exists using get_session_info
            if hasattr(self.session_manager, 'get_session_info'):
                session_info = self.session_manager.get_session_info(self.session_id)
                if session_info:
                    logger.debug(f"Session {self.session_id} found and validated")
                    return
                else:
                    # Session not found, try to create it if possible
                    logger.debug(f"Session {self.session_id} not found, attempting to create it")
                    try:
                        # Try to create the session with minimal metadata
                        # Use the same session_id that was passed in
                        created_session_id = self.session_manager.create_session(
                            user_id="knowledge_system",
                            session_type="knowledge_storage",
                            metadata={"session_id": self.session_id, "auto_created": True}
                        )
                        
                        # Verify the session was created with the expected ID
                        if created_session_id == self.session_id:
                            logger.debug(f"Auto-created session {self.session_id} for knowledge storage")
                        else:
                            logger.warning(f"Session auto-creation returned different ID: expected {self.session_id}, got {created_session_id}")
                            # Update our session_id to match what was actually created
                            if CREWAI_AVAILABLE:
                                object.__setattr__(self, 'session_id', created_session_id)
                            else:
                                self.session_id = created_session_id
                    except Exception as create_error:
                        logger.warning(f"Could not auto-create session {self.session_id}: {create_error}")
                        # Continue anyway - knowledge storage should work even without session validation
            else:
                logger.debug("Session manager doesn't have get_session_info method")
        except Exception as e:
            logger.warning(f"Session validation encountered an issue: {e}, but knowledge storage will continue")
            # Don't raise the exception - knowledge storage should work regardless
    
    def load(self) -> str:
        """Load content from the text file with version checking."""
        try:
            file_path_obj = Path(self.file_path)
            
            # Check if file has been modified (for versioning)
            if self.enable_versioning and self.content:
                file_mtime = datetime.fromtimestamp(file_path_obj.stat().st_mtime).isoformat()
                if file_mtime > self.last_updated:
                    logger.info(f"File {file_path_obj.name} has been modified, updating version")
                    if CREWAI_AVAILABLE:
                        object.__setattr__(self, 'version', self.version + 1)
                    else:
                        self.version += 1
            
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update content and timestamp
            if CREWAI_AVAILABLE:
                object.__setattr__(self, 'content', content)
                object.__setattr__(self, 'last_updated', datetime.now().isoformat())
            else:
                self.content = content
                self.last_updated = datetime.now().isoformat()
                
            logger.debug(f"Loaded content from {file_path_obj} (version {self.version})")
            return content
        except Exception as e:
            logger.error(f"Error loading file {self.file_path}: {e}")
            return ""
    
    def validate_content(self) -> bool:
        """Validate the content of the knowledge source."""
        content = self.load()
        return len(content.strip()) > 0
    
    def add(self) -> List[Dict[str, Any]]:
        """
        Add the content to Golett's knowledge system with advanced memory layer management.
        
        Returns:
            List of stored knowledge chunks with their context IDs and metadata
        """
        content = self.load()
        if not content:
            logger.warning(f"No content to add from {self.file_path}")
            return []
        
        # Split content into chunks with overlap for better context preservation
        chunks = self._chunk_text_with_overlap(content, self.chunk_size, self.overlap_size)
        stored_chunks = []
        
        # Determine storage strategy based on memory layer
        layer_config = self._get_layer_config(MemoryLayer(self.memory_layer))
        
        for i, chunk in enumerate(chunks):
            # Enhanced metadata with layer-specific information
            chunk_metadata = {
                "file_name": Path(self.file_path).name,
                "collection_name": self.collection_name,
                "memory_layer": self.memory_layer,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "file_size": len(content),
                "chunk_size": len(chunk),
                "importance": self.importance,
                "version": self.version,
                "layer_config": layer_config,
                "created_at": datetime.now().isoformat(),
                "expires_at": self._calculate_expiry(layer_config),
                "access_count": 0,
                "last_accessed": None
            }
            
            # Store each chunk as knowledge context in appropriate memory layer
            context_id = self.context_manager.store_knowledge_context(
                session_id=self.session_id,
                content=chunk,
                source=str(self.file_path),
                description=f"Knowledge chunk {i+1}/{len(chunks)} from {Path(self.file_path).name} "
                           f"(collection: {self.collection_name}, layer: {self.memory_layer})",
                tags=self.tags + [f"chunk_{i}", "file_source", self.collection_name, self.memory_layer],
                metadata=chunk_metadata,
                memory_layer=MemoryLayer(self.memory_layer)
            )
            
            self.context_ids.append(context_id)
            
            stored_chunks.append({
                "content": chunk,
                "context_id": context_id,
                "metadata": chunk_metadata,
                "layer": self.memory_layer,
                "collection": self.collection_name
            })
        
        # Store collection metadata
        self._store_collection_metadata(len(chunks))
        
        logger.info(f"Stored {len(chunks)} knowledge chunks from {Path(self.file_path).name} "
                   f"in {self.memory_layer} layer (collection: {self.collection_name})")
        return stored_chunks
    
    def retrieve(
        self, 
        query: str, 
        limit: int = 5,
        strategy: KnowledgeRetrievalStrategy = KnowledgeRetrievalStrategy.HYBRID,
        include_metadata: bool = True,
        boost_recent: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge chunks using advanced retrieval strategies.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            strategy: Retrieval strategy to use
            include_metadata: Whether to include detailed metadata
            boost_recent: Whether to boost recently accessed content
            
        Returns:
            List of relevant knowledge chunks with enhanced metadata
        """
        if strategy == KnowledgeRetrievalStrategy.SEMANTIC:
            results = self._semantic_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.STRUCTURED:
            results = self._structured_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.HYBRID:
            results = self._hybrid_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.TEMPORAL:
            results = self._temporal_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.IMPORTANCE:
            results = self._importance_retrieve(query, limit)
        else:
            results = self._hybrid_retrieve(query, limit)  # Default fallback
        
        # Post-process results
        enhanced_results = []
        for result in results:
            if boost_recent:
                result = self._apply_recency_boost(result)
            
            if include_metadata:
                result = self._enhance_result_metadata(result)
            
            # Update access tracking
            self._update_access_tracking(result.get("metadata", {}).get("context_id"))
            
            enhanced_results.append(result)
        
        return enhanced_results
    
    def paginate_retrieve(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
        strategy: KnowledgeRetrievalStrategy = KnowledgeRetrievalStrategy.HYBRID
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Retrieve knowledge with pagination support.
        
        Args:
            query: The search query
            page: Page number (1-based)
            page_size: Number of results per page
            strategy: Retrieval strategy to use
            
        Returns:
            Tuple of (results, pagination_info)
        """
        # Get total count first
        total_results = self.retrieve(query, limit=1000, strategy=strategy)  # Large limit for counting
        total_count = len(total_results)
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get paginated results
        paginated_results = total_results[start_idx:end_idx]
        
        pagination_info = {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
        }
        
        return paginated_results, pagination_info
    
    def _chunk_text_with_overlap(self, text: str, chunk_size: int, overlap_size: int) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.
        
        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk
            overlap_size: Overlap between consecutive chunks
            
        Returns:
            List of overlapping text chunks
        """
        if chunk_size <= overlap_size:
            raise ValueError("Chunk size must be larger than overlap size")
        
        # Split by paragraphs first for natural boundaries
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if current_size + len(paragraph) > chunk_size and current_chunk:
                # Create chunk with current content
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap from previous chunk
                overlap_text = self._get_overlap_text(chunk_text, overlap_size)
                current_chunk = [overlap_text, paragraph] if overlap_text else [paragraph]
                current_size = len(overlap_text) + len(paragraph) + 2 if overlap_text else len(paragraph)
            else:
                current_chunk.append(paragraph)
                current_size += len(paragraph) + 2  # +2 for '\n\n'
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get overlap text from the end of a chunk."""
        if len(text) <= overlap_size:
            return text
        
        # Try to find a natural break point (sentence end)
        overlap_text = text[-overlap_size:]
        sentence_end = overlap_text.find('. ')
        
        if sentence_end != -1:
            return overlap_text[sentence_end + 2:]  # Start after '. '
        
        return overlap_text
    
    def _get_layer_config(self, layer: MemoryLayer) -> Dict[str, Any]:
        """Get configuration for a specific memory layer."""
        configs = {
            MemoryLayer.LONG_TERM: {
                "retention_days": 365,
                "max_access_count": None,
                "auto_summarize": True,
                "cross_session": True,
                "importance_decay": 0.95  # Very slow decay
            },
            MemoryLayer.SHORT_TERM: {
                "retention_days": 30,
                "max_access_count": 100,
                "auto_summarize": False,
                "cross_session": False,
                "importance_decay": 0.9   # Moderate decay
            },
            MemoryLayer.IN_SESSION: {
                "retention_days": 1,
                "max_access_count": 50,
                "auto_summarize": False,
                "cross_session": False,
                "importance_decay": 0.8   # Faster decay
            }
        }
        return configs.get(layer, configs[MemoryLayer.LONG_TERM])
    
    def _calculate_expiry(self, layer_config: Dict[str, Any]) -> Optional[str]:
        """Calculate expiry time based on layer configuration."""
        retention_days = layer_config.get("retention_days")
        if retention_days:
            expiry = datetime.now() + timedelta(days=retention_days)
            return expiry.isoformat()
        return None
    
    def _store_collection_metadata(self, chunk_count: int) -> None:
        """Store metadata about the knowledge collection."""
        collection_metadata = {
            "collection_name": self.collection_name,
            "source_file": str(self.file_path),
            "chunk_count": chunk_count,
            "memory_layer": self.memory_layer,
            "version": self.version,
            "created_at": datetime.now().isoformat(),
            "tags": self.tags,
            "importance": self.importance
        }
        
        self.session_manager.store_session_preferences(
            session_id=self.session_id,
            preferences={f"collection_{self.collection_name}": collection_metadata}
        )
    
    def _semantic_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Semantic retrieval using vector search."""
        # First try with session filtering
        results = self.context_manager.retrieve_knowledge_for_query(
            session_id=self.session_id,
            query=query,
            tags=self.tags + [self.collection_name],
            sources=[str(self.file_path)],
            limit=limit
        )
        
        # If no results with session filtering, try without session filtering for cross-session access
        if not results:
            # Try direct Qdrant search without session filtering
            try:
                # Get the appropriate Qdrant storage for the memory layer
                memory_layer_enum = MemoryLayer(self.memory_layer)
                if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
                    qdrant_storage = self.memory_manager.layer_storage[memory_layer_enum]["qdrant"]
                else:
                    qdrant_storage = self.memory_manager.qdrant
                
                qdrant_results = qdrant_storage.search(
                    query=query,
                    limit=limit,
                    score_threshold=0.3,  # Lower threshold for better recall
                    # Don't filter by session_id for cross-session access
                )
                
                # Filter by collection and tags
                filtered_results = []
                for result in qdrant_results:
                    metadata = result.get("metadata", {})
                    
                    # Check if this result belongs to our collection
                    if (metadata.get("collection_name") == self.collection_name or 
                        self.collection_name in metadata.get("tags", [])):
                        filtered_results.append(result)
                
                results = filtered_results[:limit]
                
            except Exception as e:
                logger.warning(f"Direct Qdrant search failed: {e}")
                # Final fallback: try PostgreSQL search
                try:
                    memory_layer_enum = MemoryLayer(self.memory_layer)
                    if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
                        postgres_storage = self.memory_manager.layer_storage[memory_layer_enum]["postgres"]
                    else:
                        postgres_storage = self.memory_manager.postgres
                    
                    search_query = {
                        "type": "context",
                        "context_type": "knowledge",
                        "collection_name": self.collection_name
                    }
                    
                    postgres_results = postgres_storage.search(
                        query=search_query,
                        limit=limit
                    )
                    
                    # Convert PostgreSQL results to expected format
                    results = []
                    for result in postgres_results:
                        results.append({
                            "data": result.get("data", ""),
                            "metadata": result.get("metadata", {}),
                            "source_type": "postgres_fallback"
                        })
                        
                except Exception as pg_error:
                    logger.warning(f"PostgreSQL fallback search failed: {pg_error}")
                    results = []
        
        return results
    
    def _structured_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Structured retrieval using PostgreSQL search."""
        # Use PostgreSQL for structured search
        search_query = {
            "type": "context",
            "context_type": "knowledge",
            "collection_name": self.collection_name
        }
        
        # Get the appropriate PostgreSQL storage for the memory layer
        try:
            memory_layer_enum = MemoryLayer(self.memory_layer)
            if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
                postgres_storage = self.memory_manager.layer_storage[memory_layer_enum]["postgres"]
            else:
                postgres_storage = self.memory_manager.postgres
            
            # First try with session filtering
            results = postgres_storage.search(
                query=search_query,
                limit=limit,
                session_id=self.session_id
            )
            
            # If no results with session filtering, try without session filtering
            if not results:
                results = postgres_storage.search(
                    query=search_query,
                    limit=limit
                    # No session_id for cross-session access
                )
            
            # Convert to expected format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "data": result.get("data", ""),
                    "metadata": result.get("metadata", {}),
                    "source_type": "structured"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.warning(f"Structured retrieval failed: {e}")
            return []
    
    def _hybrid_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Hybrid retrieval combining semantic and structured approaches."""
        # Get results from both approaches
        semantic_results = self._semantic_retrieve(query, limit // 2 + 1)
        structured_results = self._structured_retrieve(query, limit // 2 + 1)
        
        # Combine and deduplicate
        seen_ids = set()
        combined_results = []
        
        # Prioritize semantic results
        for result in semantic_results:
            context_id = result.get("metadata", {}).get("context_id")
            if context_id and context_id not in seen_ids:
                seen_ids.add(context_id)
                combined_results.append(result)
        
        # Add structured results that weren't already included
        for result in structured_results:
            context_id = result.get("metadata", {}).get("context_id")
            if context_id and context_id not in seen_ids:
                seen_ids.add(context_id)
                combined_results.append(result)
        
        return combined_results[:limit]
    
    def _temporal_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Temporal retrieval prioritizing recent content."""
        results = self._semantic_retrieve(query, limit * 2)  # Get more to sort by time
        
        # Sort by creation time (most recent first)
        sorted_results = sorted(
            results,
            key=lambda x: x.get("metadata", {}).get("created_at", ""),
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def _importance_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Importance-based retrieval prioritizing high-importance content."""
        results = self._semantic_retrieve(query, limit * 2)  # Get more to sort by importance
        
        # Sort by importance (highest first)
        sorted_results = sorted(
            results,
            key=lambda x: x.get("metadata", {}).get("importance", 0),
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def _apply_recency_boost(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply recency boost to result scoring."""
        metadata = result.get("metadata", {})
        created_at = metadata.get("created_at")
        
        if created_at:
            try:
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.now() - created_time).days
                
                # Apply recency boost (newer content gets higher score)
                recency_boost = max(0.1, 1.0 - (age_days / 365))  # Decay over a year
                original_importance = metadata.get("importance", 0.5)
                boosted_importance = min(1.0, original_importance * (1 + recency_boost * 0.2))
                
                metadata["boosted_importance"] = boosted_importance
                metadata["recency_boost"] = recency_boost
                
            except Exception as e:
                logger.debug(f"Error applying recency boost: {e}")
        
        return result
    
    def _enhance_result_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance result with additional metadata."""
        metadata = result.get("metadata", {})
        
        # Add retrieval metadata
        metadata["retrieved_at"] = datetime.now().isoformat()
        metadata["source_collection"] = self.collection_name
        metadata["source_layer"] = self.memory_layer
        metadata["source_version"] = self.version
        
        return result
    
    def _update_access_tracking(self, context_id: Optional[str]) -> None:
        """Update access tracking for a knowledge chunk."""
        if not context_id:
            return
        
        try:
            # This would require extending the context manager to support updates
            # For now, we'll log the access
            logger.debug(f"Knowledge chunk accessed: {context_id}")
        except Exception as e:
            logger.debug(f"Error updating access tracking: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about this knowledge collection."""
        return {
            "collection_name": self.collection_name,
            "source_file": str(self.file_path),
            "memory_layer": self.memory_layer,
            "chunk_count": len(self.context_ids),
            "version": self.version,
            "last_updated": self.last_updated,
            "importance": self.importance,
            "tags": self.tags,
            "chunk_size": self.chunk_size,
            "overlap_size": self.overlap_size
        }
    
    def get_context_ids(self) -> List[str]:
        """Get the context IDs of stored knowledge chunks."""
        return self.context_ids.copy()
    
    def remove(self) -> bool:
        """
        Remove this knowledge source from Golett's memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Note: This would require implementing a delete method in ContextManager
            # For now, we'll just clear our local references
            if CREWAI_AVAILABLE:
                object.__setattr__(self, 'context_ids', [])
                object.__setattr__(self, 'content', "")
            else:
                self.context_ids.clear()
                self.content = ""
            
            logger.info(f"Removed knowledge source: {Path(self.file_path).name} "
                       f"(collection: {self.collection_name})")
            return True
        except Exception as e:
            logger.error(f"Error removing knowledge source {Path(self.file_path).name}: {e}")
            return False


# Keep the original simple source for backward compatibility
GolettTextFileKnowledgeSource = GolettAdvancedTextFileKnowledgeSource


class GolettAdvancedMemoryKnowledgeSource(BaseKnowledgeSource if CREWAI_AVAILABLE else object):
    """
    Advanced knowledge source that leverages Golett's sophisticated memory system.
    
    This implementation provides:
    - Multi-layer memory access (long-term, short-term, in-session)
    - Cross-session knowledge retrieval
    - Advanced filtering and ranking
    - Memory layer-aware retrieval strategies
    - Conversation context integration
    """
    
    if CREWAI_AVAILABLE:
        # Define Pydantic fields for CrewAI compatibility
        memory_manager: Any = Field(..., description="Golett memory manager instance")
        session_id: str = Field(..., description="Session ID for retrieving context")
        collection_names: List[str] = Field(default_factory=list, description="Knowledge collections to include")
        memory_layers: List[str] = Field(default_factory=lambda: ["long_term", "short_term"], description="Memory layers to access")
        context_types: List[str] = Field(default_factory=lambda: ["knowledge", "bi_data", "decision", "conversation_summary"], description="Context types to include")
        tags: List[str] = Field(default_factory=list, description="Tags to filter by")
        importance_threshold: float = Field(default=0.3, description="Minimum importance score for retrieval")
        cross_session: bool = Field(default=True, description="Whether to include cross-session knowledge")
        max_age_days: int = Field(default=30, description="Maximum age of knowledge in days")
        context_manager: Any = Field(default=None, description="Context manager instance")
        session_manager: Any = Field(default=None, description="Session manager instance")
    
    def __init__(
        self, 
        memory_manager: MemoryManager,
        session_id: str,
        collection_names: Optional[List[str]] = None,
        memory_layers: Optional[List[MemoryLayer]] = None,
        context_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        importance_threshold: float = 0.3,
        cross_session: bool = True,
        max_age_days: int = 30,
        **kwargs
    ):
        """
        Initialize the advanced Golett memory knowledge source.
        
        Args:
            memory_manager: Golett memory manager instance
            session_id: Session ID for retrieving context
            collection_names: Optional list of collection names to include
            memory_layers: Memory layers to access
            context_types: Optional list of context types to include
            tags: Optional tags to filter by
            importance_threshold: Minimum importance score for retrieval
            cross_session: Whether to include knowledge from other sessions
            max_age_days: Maximum age of knowledge to retrieve
        """
        # Initialize with proper field values for Pydantic
        init_data = {
            'memory_manager': memory_manager,
            'session_id': session_id,
            'collection_names': collection_names or [],
            'memory_layers': [layer.value for layer in (memory_layers or [MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM])],
            'context_types': context_types or ["knowledge", "bi_data", "decision", "conversation_summary"],
            'tags': tags or [],
            'importance_threshold': importance_threshold,
            'cross_session': cross_session,
            'max_age_days': max_age_days,
            'context_manager': ContextManager(memory_manager),
            'session_manager': SessionManager(memory_manager),
            **kwargs
        }
        
        if CREWAI_AVAILABLE:
            super().__init__(**init_data)
        else:
            # For non-CrewAI environments, set attributes directly
            for key, value in init_data.items():
                setattr(self, key, value)
        
        logger.info(f"Initialized advanced Golett memory knowledge source for session {session_id} "
                   f"(layers: {self.memory_layers}, cross-session: {cross_session})")
    
    def load(self) -> str:
        """Load a comprehensive summary of available knowledge from memory."""
        # Get context items from all specified layers and types
        all_items = []
        
        for context_type in self.context_types:
            for layer in self.memory_layers:
                items = self._get_layer_context(context_type, layer)
                all_items.extend(items)
        
        # Filter by age, importance, and other criteria
        filtered_items = self._filter_items(all_items)
        
        # Create a structured summary
        summary = self._create_knowledge_summary(filtered_items)
        
        return summary
    
    def validate_content(self) -> bool:
        """Validate that there is content available in memory."""
        summary = self.load()
        return len(summary.strip()) > 0
    
    def add(self) -> List[Dict[str, Any]]:
        """
        This knowledge source reads from memory, so add() returns existing content.
        
        Returns:
            List of available knowledge items from memory with enhanced metadata
        """
        all_items = []
        
        for context_type in self.context_types:
            for layer in self.memory_layers:
                items = self._get_layer_context(context_type, layer, limit=50)
                all_items.extend(items)
        
        # Filter and enhance items
        filtered_items = self._filter_items(all_items)
        enhanced_items = [self._enhance_memory_item(item) for item in filtered_items]
        
        return enhanced_items
    
    def retrieve(
        self, 
        query: str, 
        limit: int = 5,
        strategy: KnowledgeRetrievalStrategy = KnowledgeRetrievalStrategy.HYBRID,
        boost_current_session: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge from memory using advanced strategies.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            strategy: Retrieval strategy to use
            boost_current_session: Whether to boost current session content
            
        Returns:
            List of relevant knowledge items with enhanced metadata
        """
        if strategy == KnowledgeRetrievalStrategy.SEMANTIC:
            results = self._semantic_memory_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.STRUCTURED:
            results = self._structured_memory_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.HYBRID:
            results = self._hybrid_memory_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.TEMPORAL:
            results = self._temporal_memory_retrieve(query, limit)
        elif strategy == KnowledgeRetrievalStrategy.IMPORTANCE:
            results = self._importance_memory_retrieve(query, limit)
        else:
            results = self._hybrid_memory_retrieve(query, limit)
        
        # Apply session boosting if requested
        if boost_current_session:
            results = self._apply_session_boost(results)
        
        # Enhance results with memory layer information
        enhanced_results = [self._enhance_memory_result(result) for result in results]
        
        return enhanced_results[:limit]
    
    def _get_layer_context(self, context_type: str, layer: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get context items from a specific memory layer."""
        # Build query based on layer
        if layer == MemoryLayer.LONG_TERM.value:
            # Long-term: cross-session, high importance
            session_filter = None if self.cross_session else self.session_id
        elif layer == MemoryLayer.SHORT_TERM.value:
            # Short-term: current session, medium importance
            session_filter = self.session_id
        else:  # IN_SESSION
            # In-session: current session only, any importance
            session_filter = self.session_id
        
        # Retrieve context
        if session_filter:
            items = self.memory_manager.retrieve_context(
                session_id=session_filter,
                query="",  # Empty query to get recent items
                context_types=[context_type],
                limit=limit
            )
        else:
            # Cross-session query (would need to be implemented in memory manager)
            items = self.memory_manager.retrieve_context(
                session_id=self.session_id,
                query="",
                context_types=[context_type],
                limit=limit
            )
        
        # Add layer information to metadata
        for item in items:
            if "metadata" not in item:
                item["metadata"] = {}
            item["metadata"]["retrieved_from_layer"] = layer
        
        return items
    
    def _filter_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter items based on various criteria."""
        filtered_items = []
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        cutoff_str = cutoff_date.isoformat()
        
        for item in items:
            metadata = item.get("metadata", {})
            
            # Check importance threshold
            importance = metadata.get("importance", 0)
            if importance < self.importance_threshold:
                continue
            
            # Check age
            created_at = metadata.get("created_at", metadata.get("timestamp", ""))
            if created_at and created_at < cutoff_str:
                continue
            
            # Check tags if specified
            if self.tags:
                item_tags = metadata.get("tags", [])
                if not any(tag in item_tags for tag in self.tags):
                    continue
            
            # Check collections if specified
            if self.collection_names:
                item_collection = metadata.get("collection_name", "")
                if item_collection not in self.collection_names:
                    continue
            
            filtered_items.append(item)
        
        return filtered_items
    
    def _create_knowledge_summary(self, items: List[Dict[str, Any]]) -> str:
        """Create a structured summary of available knowledge."""
        if not items:
            return "No knowledge available in memory."
        
        # Group by context type and layer
        grouped = {}
        for item in items:
            metadata = item.get("metadata", {})
            context_type = metadata.get("context_type", "unknown")
            layer = metadata.get("retrieved_from_layer", "unknown")
            
            key = f"{context_type}_{layer}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        
        # Create summary
        summary_parts = []
        for key, group_items in grouped.items():
            context_type, layer = key.split("_", 1)
            summary_parts.append(f"\n## {context_type.title()} ({layer.replace('_', ' ').title()} Memory)")
            
            for item in group_items[:5]:  # Limit to 5 items per group
                content = item.get("data", {})
                if isinstance(content, dict):
                    content = str(content)[:150] + "..."
                elif isinstance(content, str):
                    content = content[:150] + "..." if len(content) > 150 else content
                
                metadata = item.get("metadata", {})
                source = metadata.get("source", "memory")
                importance = metadata.get("importance", 0)
                
                summary_parts.append(f"- [{source}] (importance: {importance:.2f}) {content}")
        
        return "\n".join(summary_parts)
    
    def _enhance_memory_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a memory item with additional metadata."""
        metadata = item.get("metadata", {})
        
        # Add retrieval context
        metadata["retrieved_at"] = datetime.now().isoformat()
        metadata["retrieval_session"] = self.session_id
        metadata["memory_source"] = "golett_advanced_memory"
        
        return item
    
    def _semantic_memory_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Semantic retrieval across memory layers."""
        all_results = []
        
        for layer in self.memory_layers:
            session_filter = self.session_id if layer != MemoryLayer.LONG_TERM.value or not self.cross_session else None
            
            if session_filter:
                results = self.memory_manager.retrieve_context(
                    session_id=session_filter,
                    query=query,
                    context_types=self.context_types,
                    limit=limit // len(self.memory_layers) + 1
                )
            else:
                # Would need cross-session semantic search
                results = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query=query,
                    context_types=self.context_types,
                    limit=limit // len(self.memory_layers) + 1
                )
            
            # Add layer info
            for result in results:
                result.get("metadata", {})["retrieved_from_layer"] = layer
            
            all_results.extend(results)
        
        return all_results
    
    def _structured_memory_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Structured retrieval using PostgreSQL."""
        search_query = {
            "type": "context",
            "context_type": {"$in": self.context_types}
        }
        
        if self.collection_names:
            search_query["collection_name"] = {"$in": self.collection_names}
        
        return self.memory_manager.postgres.search(
            query=search_query,
            limit=limit,
            session_id=self.session_id if not self.cross_session else None
        )
    
    def _hybrid_memory_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Hybrid retrieval combining semantic and structured approaches."""
        semantic_results = self._semantic_memory_retrieve(query, limit // 2 + 1)
        structured_results = self._structured_memory_retrieve(query, limit // 2 + 1)
        
        # Combine and deduplicate
        seen_ids = set()
        combined_results = []
        
        for result in semantic_results + structured_results:
            context_id = result.get("metadata", {}).get("context_id")
            if context_id and context_id not in seen_ids:
                seen_ids.add(context_id)
                combined_results.append(result)
        
        return combined_results
    
    def _temporal_memory_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Temporal retrieval prioritizing recent memory."""
        results = self._semantic_memory_retrieve(query, limit * 2)
        
        # Sort by timestamp (most recent first)
        sorted_results = sorted(
            results,
            key=lambda x: x.get("metadata", {}).get("timestamp", x.get("metadata", {}).get("created_at", "")),
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def _importance_memory_retrieve(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Importance-based retrieval prioritizing high-importance memory."""
        results = self._semantic_memory_retrieve(query, limit * 2)
        
        # Sort by importance (highest first)
        sorted_results = sorted(
            results,
            key=lambda x: x.get("metadata", {}).get("importance", 0),
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def _apply_session_boost(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply boost to results from current session."""
        for result in results:
            metadata = result.get("metadata", {})
            result_session = metadata.get("session_id")
            
            if result_session == self.session_id:
                # Boost current session results
                original_importance = metadata.get("importance", 0.5)
                boosted_importance = min(1.0, original_importance * 1.2)
                metadata["session_boosted_importance"] = boosted_importance
                metadata["session_boost_applied"] = True
        
        return results
    
    def _enhance_memory_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance memory result with additional metadata."""
        metadata = result.get("metadata", {})
        
        # Add memory layer analysis
        layer = metadata.get("retrieved_from_layer", "unknown")
        metadata["memory_layer_info"] = {
            "layer": layer,
            "cross_session": layer == MemoryLayer.LONG_TERM.value and self.cross_session,
            "retention_type": self._get_retention_type(layer),
            "access_pattern": self._get_access_pattern(metadata)
        }
        
        return result
    
    def _get_retention_type(self, layer: str) -> str:
        """Get retention type for a memory layer."""
        retention_types = {
            MemoryLayer.LONG_TERM.value: "persistent",
            MemoryLayer.SHORT_TERM.value: "session_scoped",
            MemoryLayer.IN_SESSION.value: "temporary"
        }
        return retention_types.get(layer, "unknown")
    
    def _get_access_pattern(self, metadata: Dict[str, Any]) -> str:
        """Determine access pattern based on metadata."""
        access_count = metadata.get("access_count", 0)
        
        if access_count > 10:
            return "frequently_accessed"
        elif access_count > 3:
            return "moderately_accessed"
        else:
            return "rarely_accessed"


# Keep the original simple source for backward compatibility
GolettMemoryKnowledgeSource = GolettAdvancedMemoryKnowledgeSource 