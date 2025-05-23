import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum

from golett.memory.storage.interface import BaseMemoryStorage
from golett.memory.storage.postgres import PostgresMemoryStorage
from golett.memory.storage.qdrant import QdrantMemoryStorage
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryLayer(Enum):
    """Memory layer types in Golett's normalized architecture."""
    LONG_TERM = "long_term"      # Persistent across sessions, high importance
    SHORT_TERM = "short_term"    # Session-scoped, medium importance  
    IN_SESSION = "in_session"    # Current conversation, variable importance


class MemoryManager:
    """
    Unified memory manager with normalized multi-layer architecture.
    
    This enhanced implementation provides proper separation between memory layers,
    with each layer having its own storage collections/tables for better isolation,
    maintenance, and performance.
    
    Architecture:
    - Long-term Memory: Cross-session persistent storage (365 days retention)
    - Short-term Memory: Session-scoped storage (30 days retention)  
    - In-session Memory: Real-time conversation storage (1 day retention)
    """
    
    def __init__(
        self,
        postgres_connection: str,
        qdrant_url: str = "http://localhost:6333",
        postgres_base_table: str = "golett_memories",
        qdrant_base_collection: str = "golett_vectors",
        embedding_model: str = "text-embedding-3-small",
        enable_normalized_layers: bool = True,
    ) -> None:
        """
        Initialize the memory manager with normalized layer storage.
        
        Args:
            postgres_connection: PostgreSQL connection string
            qdrant_url: URL of the Qdrant server
            postgres_base_table: Base name for PostgreSQL tables (will be suffixed by layer)
            qdrant_base_collection: Base name for Qdrant collections (will be suffixed by layer)
            embedding_model: Name of the embedding model to use
            enable_normalized_layers: Whether to use normalized layer architecture
        """
        self.enable_normalized_layers = enable_normalized_layers
        self.postgres_base_table = postgres_base_table
        self.qdrant_base_collection = qdrant_base_collection
        
        # Layer configurations with retention policies and importance thresholds
        self.layer_configs = {
            MemoryLayer.LONG_TERM: {
                "retention_days": 365,
                "importance_threshold": 0.7,
                "cross_session": True,
                "priority": "high",
                "cleanup_frequency": "weekly"
            },
            MemoryLayer.SHORT_TERM: {
                "retention_days": 30,
                "importance_threshold": 0.5,
                "cross_session": False,
                "priority": "medium", 
                "cleanup_frequency": "daily"
            },
            MemoryLayer.IN_SESSION: {
                "retention_days": 1,
                "importance_threshold": 0.3,
                "cross_session": False,
                "priority": "low",
                "cleanup_frequency": "hourly"
            }
        }
        
        if enable_normalized_layers:
            # Initialize separate storage backends for each memory layer
            self.layer_storage = {}
            
            for layer in MemoryLayer:
                # Create layer-specific table and collection names
                postgres_table = f"{postgres_base_table}_{layer.value}"
                qdrant_collection = f"{qdrant_base_collection}_{layer.value}"
                
                # Initialize PostgreSQL storage for this layer
                postgres_storage = PostgresMemoryStorage(
                    connection_string=postgres_connection,
                    table_name=postgres_table
                )
                
                # Initialize Qdrant storage for this layer
                qdrant_storage = QdrantMemoryStorage(
                    collection_name=qdrant_collection,
                    url=qdrant_url,
                    embedder_name=embedding_model
                )
                
                self.layer_storage[layer] = {
                    "postgres": postgres_storage,
                    "qdrant": qdrant_storage
                }
                
                logger.info(f"Initialized {layer.value} memory layer: "
                           f"table={postgres_table}, collection={qdrant_collection}")
        else:
            # Backward compatibility: single storage backend
            self.postgres = PostgresMemoryStorage(
                connection_string=postgres_connection,
                table_name=postgres_base_table
            )
            self.qdrant = QdrantMemoryStorage(
                collection_name=qdrant_base_collection, 
                url=qdrant_url,
                embedder_name=embedding_model
            )
        
        logger.info(f"Memory Manager initialized with normalized layers: {enable_normalized_layers}")

    def _get_storage_for_layer(self, layer: MemoryLayer) -> Tuple[PostgresMemoryStorage, QdrantMemoryStorage]:
        """Get the storage backends for a specific memory layer."""
        if self.enable_normalized_layers:
            storage = self.layer_storage[layer]
            return storage["postgres"], storage["qdrant"]
        else:
            # Backward compatibility
            return self.postgres, self.qdrant

    def _determine_memory_layer(
        self, 
        context_type: str, 
        importance: float, 
        session_id: str,
        explicit_layer: Optional[MemoryLayer] = None
    ) -> MemoryLayer:
        """
        Determine the appropriate memory layer for storing content.
        
        Args:
            context_type: Type of context being stored
            importance: Importance score (0.0-1.0)
            session_id: Session ID
            explicit_layer: Explicitly specified layer (overrides automatic determination)
            
        Returns:
            The appropriate memory layer
        """
        if explicit_layer:
            return explicit_layer
            
        # Automatic layer determination based on content type and importance
        if context_type in ["knowledge", "bi_data"] and importance >= 0.7:
            return MemoryLayer.LONG_TERM
        elif context_type in ["decision", "conversation_summary"] and importance >= 0.5:
            return MemoryLayer.SHORT_TERM
        elif context_type in ["message", "intermediate_result"]:
            return MemoryLayer.IN_SESSION
        else:
            # Default based on importance
            if importance >= 0.7:
                return MemoryLayer.LONG_TERM
            elif importance >= 0.5:
                return MemoryLayer.SHORT_TERM
            else:
                return MemoryLayer.IN_SESSION

    def _generate_layer_aware_key(
        self, 
        base_key: str, 
        layer: MemoryLayer, 
        session_id: str
    ) -> str:
        """
        Generate a layer-aware storage key with proper partitioning.
        
        Args:
            base_key: Base key for the content
            layer: Memory layer
            session_id: Session ID
            
        Returns:
            Layer-aware storage key
        """
        if layer == MemoryLayer.LONG_TERM:
            # Long-term: global namespace, no session prefix
            return f"lt:{base_key}"
        elif layer == MemoryLayer.SHORT_TERM:
            # Short-term: session-scoped namespace
            return f"st:{session_id}:{base_key}"
        else:  # IN_SESSION
            # In-session: session and timestamp scoped
            timestamp = datetime.now().strftime("%Y%m%d_%H")
            return f"is:{session_id}:{timestamp}:{base_key}"

    def create_session(self, metadata: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> str:
        """
        Create a new chat session with layer-aware initialization.
        
        Args:
            metadata: Additional metadata for the session
            session_id: Optional custom session ID (generates UUID if None)
            
        Returns:
            A unique session ID
        """
        # Use provided session ID or generate a new UUID
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Store session metadata
        session_data = {
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        
        # Add metadata if provided
        if metadata:
            session_data.update(metadata)
        
        # Store session in short-term memory layer (session-scoped)
        layer = MemoryLayer.SHORT_TERM
        postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
        
        session_key = self._generate_layer_aware_key("session", layer, session_id)
        session_metadata = {
            "type": "session", 
            "session_id": session_id,
            "memory_layer": layer.value,
            "created_at": datetime.now().isoformat()
        }
        
        # Save to appropriate layer storage
        postgres_storage.save(
            key=session_key,
            data=session_data,
            metadata=session_metadata
        )
        
        logger.info(f"Created new session: {session_id} in {layer.value} layer")
        return session_id

    def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None
    ) -> str:
        """
        Store a message in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            role: The role of the message sender (user, assistant, etc.)
            content: The message content
            metadata: Additional metadata for the message
            memory_layer: Explicit memory layer (auto-determined if None)
            
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
        
        # Determine memory layer (messages typically go to in-session)
        importance = metadata.get("importance", 0.5) if metadata else 0.5
        layer = self._determine_memory_layer("message", importance, session_id, memory_layer)
        
        # Get appropriate storage backends
        postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
        
        # Generate layer-aware key
        message_key = self._generate_layer_aware_key(f"message:{message_id}", layer, session_id)
        
        # Prepare metadata
        message_metadata = {
            "type": "message",
            "session_id": session_id,
            "message_id": message_id,
            "role": role,
            "timestamp": timestamp,
            "memory_layer": layer.value,
            "importance": importance,
        }
        
        # Add additional metadata if provided
        if metadata:
            message_metadata.update(metadata)
        
        # Store in appropriate layer backends
        postgres_storage.save(
            key=message_key,
            data=message_data,
            metadata=message_metadata
        )
        
        # Vector storage for semantic search
        qdrant_storage.save(
            key=message_key,
            data=content,
            metadata=message_metadata
        )
        
        logger.debug(f"Stored message in session {session_id}: {role} (layer: {layer.value})")
        return message_id

    def get_session_history(
        self, 
        session_id: str, 
        limit: int = 100,
        include_layers: Optional[List[MemoryLayer]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the message history for a session across memory layers.
        
        Args:
            session_id: The session ID
            limit: Maximum number of messages to return
            include_layers: Memory layers to include (default: all layers)
            
        Returns:
            List of messages in chronological order
        """
        if include_layers is None:
            include_layers = list(MemoryLayer)
        
        all_messages = []
        
        for layer in include_layers:
            postgres_storage, _ = self._get_storage_for_layer(layer)
            
            # Get session history from this layer
            if self.enable_normalized_layers:
                layer_history = postgres_storage.get_session_history(
                    session_id=session_id, 
                    limit=limit
                )
            else:
                # Backward compatibility
                layer_history = postgres_storage.get_session_history(
                    session_id=session_id, 
                    limit=limit
                )
            
            # Filter to only include messages and add layer info
            layer_messages = []
            for entry in layer_history:
                if entry.get('metadata', {}).get('type') == 'message':
                    entry['metadata']['retrieved_from_layer'] = layer.value
                    layer_messages.append(entry)
            
            all_messages.extend(layer_messages)
        
        # Sort by timestamp and limit results
        sorted_messages = sorted(
            all_messages, 
            key=lambda x: x.get('metadata', {}).get('timestamp', '')
        )
        
        return sorted_messages[:limit]

    def search_message_history(
        self, 
        query: str,
        session_id: Optional[str] = None,
        limit: int = 5,
        semantic: bool = True,
        include_layers: Optional[List[MemoryLayer]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search through message history across memory layers.
        
        Args:
            query: The search query
            session_id: Optional session ID to filter by
            limit: Maximum number of results to return
            semantic: Whether to use semantic search (True) or text search (False)
            include_layers: Memory layers to search (default: all layers)
            
        Returns:
            List of matching messages
        """
        if include_layers is None:
            include_layers = list(MemoryLayer)
        
        all_results = []
        
        for layer in include_layers:
            postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
            
            if semantic:
                # Use Qdrant for semantic search
                kwargs = {}
                if session_id:
                    kwargs["session_id"] = session_id
                    
                layer_results = qdrant_storage.search(
                    query=query,
                    limit=limit // len(include_layers) + 1,
                    **kwargs
                )
            else:
                # Use PostgreSQL for text search
                search_query = {"content": query}
                if session_id:
                    search_query["session_id"] = session_id
                    
                layer_results = postgres_storage.search(
                    query=search_query,
                    limit=limit // len(include_layers) + 1
                )
            
            # Add layer information to results
            for result in layer_results:
                result.get("metadata", {})["searched_in_layer"] = layer.value
            
            all_results.extend(layer_results)
        
        # Sort by relevance/timestamp and limit
        return all_results[:limit]

    def store_context(
        self,
        session_id: str,
        context_type: str,
        data: Any,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None
    ) -> str:
        """
        Store contextual information in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            context_type: Type of context (e.g., "bi_data", "entity", "decision", "knowledge")
            data: The context data to store
            importance: Importance score (0.0-1.0) for retrieval prioritization
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            
        Returns:
            The context entry ID
        """
        context_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Determine appropriate memory layer
        layer = self._determine_memory_layer(context_type, importance, session_id, memory_layer)
        
        # Get appropriate storage backends
        postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
        
        # Generate layer-aware key
        context_key = self._generate_layer_aware_key(f"context:{context_type}:{context_id}", layer, session_id)
        
        # Prepare metadata
        context_metadata = {
            "type": "context",
            "context_type": context_type,
            "session_id": session_id,
            "context_id": context_id,
            "timestamp": timestamp,
            "importance": importance,
            "memory_layer": layer.value,
        }
        
        # Add additional metadata if provided
        if metadata:
            context_metadata.update(metadata)
        
        # Store in both backends for different retrieval patterns
        postgres_storage.save(
            key=context_key,
            data=data,
            metadata=context_metadata
        )
        
        # Vector storage for semantic retrieval
        qdrant_storage.save(
            key=context_key,
            data=data,
            metadata=context_metadata
        )
        
        logger.debug(f"Stored {context_type} context in session {session_id} (layer: {layer.value})")
        return context_id

    def retrieve_context(
        self,
        session_id: str,
        query: str,
        context_types: Optional[List[str]] = None,
        limit: int = 5,
        include_layers: Optional[List[MemoryLayer]] = None,
        cross_session: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context across memory layers.
        
        Args:
            session_id: The session ID
            query: The query to find relevant context for
            context_types: Optional list of context types to filter by
            limit: Maximum number of results to return
            include_layers: Memory layers to search (default: all layers)
            cross_session: Whether to include cross-session results (long-term layer only)
            
        Returns:
            List of relevant context entries
        """
        if include_layers is None:
            include_layers = list(MemoryLayer)
        
        all_results = []
        
        for layer in include_layers:
            _, qdrant_storage = self._get_storage_for_layer(layer)
            
            # Build search parameters
            kwargs = {}
            
            # Session filtering based on layer and cross_session setting
            if layer == MemoryLayer.LONG_TERM and cross_session:
                # Long-term: allow cross-session if explicitly requested
                pass  # No session filter
            else:
                # Other layers: always filter by session
                kwargs["session_id"] = session_id
            
            # Search using vector similarity
            layer_results = qdrant_storage.search(
                query=query,
                limit=limit // len(include_layers) + 1,
                **kwargs
            )
            
            # Filter by context type if specified
            if context_types:
                layer_results = [
                    r for r in layer_results 
                    if r.get("metadata", {}).get("context_type") in context_types
                ]
            
            # Add layer information
            for result in layer_results:
                result.get("metadata", {})["retrieved_from_layer"] = layer.value
            
            all_results.extend(layer_results)
        
        # Sort by relevance and return limited results
        return all_results[:limit]
    
    def store_bi_data(
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
        Store BI-related data in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            data_type: Type of BI data (e.g., "query_result", "analysis", "insight")
            data: The BI data to store
            description: Human-readable description of the data
            importance: Importance score (0.0-1.0)
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            
        Returns:
            The BI data entry ID
        """
        # BI data is typically important and should go to long-term or short-term memory
        layer = self._determine_memory_layer("bi_data", importance, session_id, memory_layer)
        
        bi_data = {
            "data_type": data_type,
            "data": data,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store as context with enhanced metadata
        enhanced_metadata = {
            "bi_data_type": data_type,
            "description": description,
        }
        if metadata:
            enhanced_metadata.update(metadata)
        
        return self.store_context(
            session_id=session_id,
            context_type="bi_data",
            data=bi_data,
            importance=importance,
            metadata=enhanced_metadata,
            memory_layer=layer
        )

    def retrieve_bi_data(
        self,
        session_id: str,
        query: str,
        data_types: Optional[List[str]] = None,
        limit: int = 5,
        include_layers: Optional[List[MemoryLayer]] = None,
        cross_session: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve BI data across memory layers.
        
        Args:
            session_id: The session ID
            query: The search query
            data_types: Optional list of BI data types to filter by
            limit: Maximum number of results to return
            include_layers: Memory layers to search (default: long-term and short-term)
            cross_session: Whether to include cross-session results
            
        Returns:
            List of relevant BI data entries
        """
        if include_layers is None:
            # BI data typically stored in long-term and short-term layers
            include_layers = [MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
        
        # Retrieve BI context
        results = self.retrieve_context(
            session_id=session_id,
            query=query,
            context_types=["bi_data"],
            limit=limit,
            include_layers=include_layers,
            cross_session=cross_session
        )
        
        # Additional filtering by BI data types
        if data_types:
            filtered_results = []
            for result in results:
                metadata = result.get("metadata", {})
                if metadata.get("bi_data_type") in data_types:
                    filtered_results.append(result)
            return filtered_results
        
        return results

    def store_decision(
        self,
        session_id: str,
        decision_type: str,
        description: str,
        reasoning: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_layer: Optional[MemoryLayer] = None
    ) -> str:
        """
        Store an agent's decision in the appropriate memory layer.
        
        Args:
            session_id: The session ID
            decision_type: Type of decision (e.g., "use_data", "response_mode")
            description: Short description of the decision
            reasoning: Detailed reasoning for the decision
            metadata: Additional metadata
            memory_layer: Explicit memory layer (auto-determined if None)
            
        Returns:
            The decision entry ID
        """
        decision_data = {
            "decision_type": decision_type,
            "description": description,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        # Decisions are typically important for context
        importance = 0.8
        layer = self._determine_memory_layer("decision", importance, session_id, memory_layer)
        
        enhanced_metadata = {
            "decision_type": decision_type,
            "description": description,
        }
        if metadata:
            enhanced_metadata.update(metadata)
        
        return self.store_context(
            session_id=session_id,
            context_type="decision",
            data=decision_data,
            importance=importance,
            metadata=enhanced_metadata,
            memory_layer=layer
        )

    def get_recent_decisions(
        self,
        session_id: str,
        decision_type: Optional[str] = None,
        limit: int = 5,
        include_layers: Optional[List[MemoryLayer]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent decisions across memory layers.
        
        Args:
            session_id: The session ID
            decision_type: Optional decision type to filter by
            limit: Maximum number of decisions to return
            include_layers: Memory layers to search (default: short-term and in-session)
            
        Returns:
            List of recent decisions
        """
        if include_layers is None:
            # Decisions typically in short-term and in-session layers
            include_layers = [MemoryLayer.SHORT_TERM, MemoryLayer.IN_SESSION]
        
        all_decisions = []
        
        for layer in include_layers:
            postgres_storage, _ = self._get_storage_for_layer(layer)
            
            # Build search query
            search_query = {
                "metadata.context_type": "decision",
                "metadata.session_id": session_id
            }
            
            if decision_type:
                search_query["metadata.decision_type"] = decision_type
            
            layer_decisions = postgres_storage.search(
                query=search_query,
                limit=limit
            )
            
            # Add layer information
            for decision in layer_decisions:
                decision.get("metadata", {})["retrieved_from_layer"] = layer.value
            
            all_decisions.extend(layer_decisions)
        
        # Sort by timestamp (most recent first) and limit
        sorted_decisions = sorted(
            all_decisions,
            key=lambda x: x.get("metadata", {}).get("timestamp", ""),
            reverse=True
        )
        
        return sorted_decisions[:limit]

    # New layer management methods

    def get_layer_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each memory layer.
        
        Returns:
            Dictionary with statistics for each layer
        """
        if not self.enable_normalized_layers:
            return {"message": "Normalized layers not enabled"}
        
        stats = {}
        
        for layer in MemoryLayer:
            postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
            
            # Get basic counts (this would need to be implemented in storage classes)
            try:
                # Placeholder - would need actual implementation in storage classes
                layer_stats = {
                    "layer": layer.value,
                    "config": self.layer_configs[layer],
                    "storage": {
                        "postgres_table": f"{self.postgres_base_table}_{layer.value}",
                        "qdrant_collection": f"{self.qdrant_base_collection}_{layer.value}"
                    },
                    "estimated_entries": "N/A",  # Would need storage implementation
                    "last_cleanup": "N/A",
                    "retention_status": "active"
                }
                stats[layer.value] = layer_stats
            except Exception as e:
                logger.error(f"Error getting stats for layer {layer.value}: {e}")
                stats[layer.value] = {"error": str(e)}
        
        return stats

    def cleanup_expired_memories(
        self, 
        layer: Optional[MemoryLayer] = None,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up expired memories based on retention policies.
        
        Args:
            layer: Specific layer to clean (default: all layers)
            dry_run: If True, only report what would be deleted
            
        Returns:
            Cleanup report
        """
        if not self.enable_normalized_layers:
            return {"message": "Normalized layers not enabled"}
        
        layers_to_clean = [layer] if layer else list(MemoryLayer)
        cleanup_report = {}
        
        for target_layer in layers_to_clean:
            config = self.layer_configs[target_layer]
            retention_days = config["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            postgres_storage, qdrant_storage = self._get_storage_for_layer(target_layer)
            
            # This would need implementation in storage classes
            layer_report = {
                "layer": target_layer.value,
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat(),
                "dry_run": dry_run,
                "deleted_count": 0,  # Placeholder
                "errors": []
            }
            
            if not dry_run:
                try:
                    # Actual cleanup would be implemented here
                    logger.info(f"Cleaning up {target_layer.value} layer (retention: {retention_days} days)")
                    # deleted_count = storage.delete_before_date(cutoff_date)
                    # layer_report["deleted_count"] = deleted_count
                except Exception as e:
                    layer_report["errors"].append(str(e))
                    logger.error(f"Error cleaning up {target_layer.value} layer: {e}")
            
            cleanup_report[target_layer.value] = layer_report
        
        return cleanup_report

    def migrate_memory_between_layers(
        self,
        source_layer: MemoryLayer,
        target_layer: MemoryLayer,
        criteria: Dict[str, Any],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate memories between layers based on criteria.
        
        Args:
            source_layer: Source memory layer
            target_layer: Target memory layer
            criteria: Migration criteria (e.g., importance threshold, age)
            dry_run: If True, only report what would be migrated
            
        Returns:
            Migration report
        """
        if not self.enable_normalized_layers:
            return {"message": "Normalized layers not enabled"}
        
        source_postgres, source_qdrant = self._get_storage_for_layer(source_layer)
        target_postgres, target_qdrant = self._get_storage_for_layer(target_layer)
        
        migration_report = {
            "source_layer": source_layer.value,
            "target_layer": target_layer.value,
            "criteria": criteria,
            "dry_run": dry_run,
            "migrated_count": 0,
            "errors": []
        }
        
        try:
            # This would need implementation to find and migrate matching entries
            logger.info(f"Migration from {source_layer.value} to {target_layer.value} "
                       f"(criteria: {criteria}, dry_run: {dry_run})")
            
            if not dry_run:
                # Actual migration logic would be implemented here
                pass
                
        except Exception as e:
            migration_report["errors"].append(str(e))
            logger.error(f"Error during migration: {e}")
        
        return migration_report

    def search_across_all_layers(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
        include_layer_weights: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search across all memory layers with layer-aware ranking.
        
        Args:
            query: Search query
            session_id: Optional session filter
            limit: Maximum results
            include_layer_weights: Whether to apply layer-based importance weighting
            
        Returns:
            Ranked results from all layers
        """
        all_results = []
        
        # Search each layer
        for layer in MemoryLayer:
            _, qdrant_storage = self._get_storage_for_layer(layer)
            
            kwargs = {}
            if session_id and layer != MemoryLayer.LONG_TERM:
                kwargs["session_id"] = session_id
            
            layer_results = qdrant_storage.search(
                query=query,
                limit=limit,
                **kwargs
            )
            
            # Add layer information and apply weights
            for result in layer_results:
                metadata = result.get("metadata", {})
                metadata["searched_in_layer"] = layer.value
                
                if include_layer_weights:
                    # Apply layer-based importance weighting
                    original_score = result.get("score", 0.5)
                    layer_weight = self.layer_configs[layer]["importance_threshold"]
                    weighted_score = original_score * (1 + layer_weight)
                    result["weighted_score"] = weighted_score
                    metadata["layer_weight_applied"] = layer_weight
            
            all_results.extend(layer_results)
        
        # Sort by weighted score if weights are applied, otherwise by original score
        sort_key = "weighted_score" if include_layer_weights else "score"
        sorted_results = sorted(
            all_results,
            key=lambda x: x.get(sort_key, 0),
            reverse=True
        )
        
        return sorted_results[:limit]

    def reset(self) -> None:
        """
        Reset all memory storage (clear all data).
        """
        if self.enable_normalized_layers:
            for layer in MemoryLayer:
                postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
                postgres_storage.reset()
                qdrant_storage.reset()
                logger.info(f"Reset {layer.value} memory layer")
        else:
            # Backward compatibility
            self.postgres.reset()
            self.qdrant.reset()
            logger.info("Reset memory storage")

    # Backward compatibility properties
    @property
    def postgres(self):
        """Backward compatibility: return long-term postgres storage."""
        if self.enable_normalized_layers:
            return self.layer_storage[MemoryLayer.LONG_TERM]["postgres"]
        else:
            return self._postgres

    @postgres.setter
    def postgres(self, value):
        """Backward compatibility: set postgres storage."""
        if not self.enable_normalized_layers:
            self._postgres = value

    @property
    def qdrant(self):
        """Backward compatibility: return long-term qdrant storage."""
        if self.enable_normalized_layers:
            return self.layer_storage[MemoryLayer.LONG_TERM]["qdrant"]
        else:
            return self._qdrant

    @qdrant.setter
    def qdrant(self, value):
        """Backward compatibility: set qdrant storage."""
        if not self.enable_normalized_layers:
            self._qdrant = value 