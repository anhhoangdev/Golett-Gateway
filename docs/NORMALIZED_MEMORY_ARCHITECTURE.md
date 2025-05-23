# Golett Normalized Memory Layer Architecture

## Overview

We have successfully implemented a sophisticated **normalized memory layer architecture** for Golett that addresses the fundamental design flaw identified in the previous system. The new architecture provides proper separation between different types of memory, eliminating confusion and improving maintainability.

## Architecture Components

### 1. Three-Layer Memory System

#### **Long-term Memory** (`MemoryLayer.LONG_TERM`)
- **Purpose**: Persistent knowledge across sessions
- **Retention**: 365 days
- **Importance Threshold**: 0.7+
- **Storage**: `golett_memory_long_term` (PostgreSQL) + `golett_memory_long_term` (Qdrant)
- **Use Cases**: 
  - Core knowledge and documentation
  - Important historical decisions
  - User preferences and settings
  - Cross-session persistent data

#### **Short-term Memory** (`MemoryLayer.SHORT_TERM`)
- **Purpose**: Session-scoped contextual information
- **Retention**: 30 days
- **Importance Threshold**: 0.5-0.7
- **Storage**: `golett_memory_short_term` (PostgreSQL) + `golett_memory_short_term` (Qdrant)
- **Use Cases**:
  - Session-specific workflow state
  - Temporary user preferences
  - Session-scoped decisions
  - Intermediate processing results

#### **In-session Memory** (`MemoryLayer.IN_SESSION`)
- **Purpose**: Real-time conversation and immediate context
- **Retention**: 1 day
- **Importance Threshold**: 0.3-1.0 (variable)
- **Storage**: `golett_memory_in_session` (PostgreSQL) + `golett_memory_in_session` (Qdrant)
- **Use Cases**:
  - Current conversation messages
  - Immediate working context
  - Real-time decision tracking
  - Temporary calculations

### 2. Enhanced Memory Manager

The `MemoryManager` class has been completely redesigned with:

#### **Normalized Layer Support**
- `enable_normalized_layers=True` activates the new architecture
- Separate storage backends for each memory layer
- Layer-aware key generation with prefixes
- Automatic layer determination based on content importance

#### **Layer Configuration**
```python
layer_configs = {
    MemoryLayer.LONG_TERM: {
        "retention_days": 365,
        "importance_threshold": 0.7,
        "cross_session": True
    },
    MemoryLayer.SHORT_TERM: {
        "retention_days": 30,
        "importance_threshold": 0.5,
        "cross_session": False
    },
    MemoryLayer.IN_SESSION: {
        "retention_days": 1,
        "importance_threshold": 0.3,
        "cross_session": False
    }
}
```

#### **New Methods**
- `store_message()` - Layer-aware message storage
- `store_context()` - Enhanced context storage with layer routing
- `retrieve_context()` - Cross-layer context retrieval
- `get_layer_statistics()` - Layer performance analysis
- `cleanup_expired_memories()` - Layer-specific cleanup
- `migrate_memory_between_layers()` - Content migration
- `search_across_all_layers()` - Unified cross-layer search

### 3. Advanced Knowledge Sources

#### **GolettAdvancedTextFileKnowledgeSource**
- Direct integration with normalized memory layers
- Intelligent chunking with context preservation
- Layer-specific storage based on importance
- Version tracking and file modification detection
- Collection-based organization

#### **GolettAdvancedMemoryKnowledgeSource**
- Retrieves existing knowledge from memory layers
- Cross-session knowledge access
- Advanced filtering by layer, type, and importance
- Comprehensive knowledge summaries

#### **Enhanced Knowledge Adapter**
- Hybrid support for CrewAI and Golett-native sources
- Layer-aware knowledge retrieval
- Advanced ranking with layer weighting
- Collection management and optimization

### 4. Storage Architecture

#### **Separate Storage Collections/Tables**
Each memory layer has dedicated storage:

**PostgreSQL Tables:**
- `golett_memory_long_term`
- `golett_memory_short_term` 
- `golett_memory_in_session`

**Qdrant Collections:**
- `golett_memory_long_term`
- `golett_memory_short_term`
- `golett_memory_in_session`

#### **Session-Aware Partitioning**
- Layer-specific key patterns: `{layer}:{type}:{id}:{session_id}`
- Proper session isolation within each layer
- Cross-session access control based on layer policies

## Key Benefits

### 1. **Proper Isolation**
- Each memory layer has dedicated storage preventing confusion
- No more mixed data types in the same "bucket"
- Clear separation of concerns

### 2. **Optimized Performance**
- Layer-specific optimization strategies
- Targeted indexing and query patterns
- Efficient retention and cleanup policies

### 3. **Intelligent Routing**
- Automatic layer selection based on content analysis
- Importance-based storage decisions
- Context-aware retrieval strategies

### 4. **Enhanced Maintainability**
- Clear data organization and lifecycle management
- Layer-specific monitoring and optimization
- Simplified debugging and troubleshooting

### 5. **Advanced Features**
- Cross-layer search with proper weighting
- Memory migration between layers
- Comprehensive analytics and reporting
- Collection-based knowledge organization

## Implementation Details

### Layer Determination Logic
```python
def _determine_memory_layer(self, context_type: str, importance: float, 
                          session_id: str, explicit_layer: Optional[MemoryLayer]) -> MemoryLayer:
    if explicit_layer:
        return explicit_layer
    
    # Auto-determine based on importance and type
    if importance >= 0.7 or context_type in ["knowledge", "user_preference"]:
        return MemoryLayer.LONG_TERM
    elif importance >= 0.5 or context_type in ["session_state", "decision"]:
        return MemoryLayer.SHORT_TERM
    else:
        return MemoryLayer.IN_SESSION
```

### Storage Backend Management
```python
def _get_storage_for_layer(self, layer: MemoryLayer) -> Tuple[PostgresMemoryStorage, QdrantMemoryStorage]:
    if layer not in self.layer_storage:
        # Create dedicated storage instances for the layer
        postgres_table = f"{self.postgres_base_table}_{layer.value}"
        qdrant_collection = f"{self.qdrant_base_collection}_{layer.value}"
        
        self.layer_storage[layer] = {
            "postgres": PostgresMemoryStorage(table_name=postgres_table),
            "qdrant": QdrantMemoryStorage(collection_name=qdrant_collection)
        }
    
    return (self.layer_storage[layer]["postgres"], 
            self.layer_storage[layer]["qdrant"])
```

### Cross-Layer Retrieval
```python
def retrieve_context(self, session_id: str, query: str, 
                    include_layers: Optional[List[MemoryLayer]] = None,
                    cross_session: bool = False) -> List[Dict[str, Any]]:
    if include_layers is None:
        include_layers = list(MemoryLayer)
    
    all_results = []
    for layer in include_layers:
        postgres_storage, qdrant_storage = self._get_storage_for_layer(layer)
        
        # Layer-specific retrieval logic
        kwargs = {}
        if layer == MemoryLayer.LONG_TERM and cross_session:
            pass  # Allow cross-session for long-term
        else:
            kwargs["session_id"] = session_id
        
        layer_results = qdrant_storage.search(query=query, **kwargs)
        all_results.extend(layer_results)
    
    return all_results
```

## Demo and Testing

The comprehensive demo (`examples/normalized_memory_layers_demo.py`) showcases:

1. **Layer Separation**: Proper storage in different layers
2. **Retrieval Strategies**: Semantic, hybrid, temporal, and importance-based
3. **Cross-Layer Operations**: Unified search with layer weighting
4. **Memory Management**: Cleanup, optimization, and migration
5. **Collection Management**: Knowledge organization and tracking
6. **Interactive Chat**: Real-time layer-aware conversation

## Migration Path

### From Legacy System
1. Enable normalized layers: `enable_normalized_layers=True`
2. Existing data remains accessible through backward compatibility
3. New data automatically uses the normalized architecture
4. Gradual migration using `migrate_memory_between_layers()`

### Backward Compatibility
- Legacy `postgres` and `qdrant` properties still work
- Existing code continues to function
- Gradual adoption of new layer-aware methods

## Performance Considerations

### Storage Optimization
- Layer-specific indexing strategies
- Optimized retention policies
- Efficient cleanup procedures
- Targeted query patterns

### Retrieval Optimization
- Layer-aware caching
- Importance-based ranking
- Temporal boosting for recent content
- Cross-layer result deduplication

## Future Enhancements

1. **Advanced Analytics**: Layer utilization metrics and optimization recommendations
2. **Automatic Migration**: AI-driven content migration between layers
3. **Dynamic Configuration**: Runtime adjustment of layer parameters
4. **Distributed Storage**: Multi-node layer distribution for scalability
5. **Compression**: Layer-specific compression strategies for storage efficiency

## Conclusion

The normalized memory layer architecture represents a significant advancement in Golett's memory management capabilities. By providing proper separation, intelligent routing, and advanced features, this architecture enables more sophisticated and maintainable conversational AI systems.

The implementation successfully addresses the fundamental design flaw of the previous system while maintaining backward compatibility and providing a clear migration path for existing deployments. 