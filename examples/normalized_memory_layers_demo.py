#!/usr/bin/env python3
"""
Golett Normalized Memory Layers Demo

This is the standard demo showcasing Golett's advanced normalized memory layer architecture,
demonstrating proper layer separation, sophisticated knowledge management,
and cross-layer operations with the new three-layer system:

- Long-term Memory: Persistent across sessions, high importance (365 days retention)
- Short-term Memory: Session-scoped, medium importance (30 days retention)  
- In-session Memory: Real-time conversation, variable importance (1 day retention)

Features demonstrated:
- Normalized memory layer storage and retrieval
- Layer-aware knowledge source management
- Advanced retrieval strategies across layers
- Memory layer optimization and cleanup
- Cross-session knowledge persistence
- Collection-based knowledge organization
- Layer statistics and performance analysis
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.chat.crew import GolettKnowledgeAdapter
from golett.knowledge.sources import (
    GolettAdvancedTextFileKnowledgeSource,
    GolettAdvancedMemoryKnowledgeSource,
    KnowledgeRetrievalStrategy
)
from golett.memory.session.session_manager import SessionManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class NormalizedMemoryLayersDemo:
    """Standard demo of Golett's normalized memory layer architecture."""
    
    def __init__(self):
        """Initialize the demo with normalized memory layers enabled."""
        self.session_id = f"normalized_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.memory_manager = None
        self.knowledge_adapter = None
        self.demo_files = {}
        
        print("🚀 Golett Normalized Memory Layers Demo")
        print("=" * 60)
        print(f"📋 Session ID: {self.session_id}")
        
    async def setup(self):
        """Set up the demo environment with normalized layers."""
        try:
            # Check OpenAI API key first
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                print("❌ Error: OPENAI_API_KEY environment variable not set")
                print("💡 Please set your OpenAI API key:")
                print("   export OPENAI_API_KEY='your-api-key-here'")
                raise ValueError("Missing OpenAI API key")
            
            print("🔧 Setting up memory manager with normalized layers...")
            
            # Get database connection parameters from environment
            postgres_connection = os.getenv(
                "POSTGRES_CONNECTION", 
                "postgresql://golett_user:golett_password@localhost:5432/golett_db"
            )
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            
            print(f"   📊 PostgreSQL: {postgres_connection.split('@')[1] if '@' in postgres_connection else 'localhost'}")
            print(f"   🔍 Qdrant: {qdrant_url}")
            
            # Initialize memory manager with normalized layers enabled
            self.memory_manager = MemoryManager(
                postgres_connection=postgres_connection,
                qdrant_url=qdrant_url,
                enable_normalized_layers=True  # ✅ Enable the new architecture
            )
            
            # Create session properly using session manager
            print("🔧 Creating demo session...")
            session_manager = SessionManager(self.memory_manager)
            
            # Create session with proper metadata
            created_session_id = session_manager.create_session(
                user_id="demo_user",
                session_type="normalized_layers_demo",
                preferences={"demo_mode": True, "normalized_layers": True},
                metadata={
                    "session_id": self.session_id,
                    "demo_type": "normalized_memory_layers",
                    "created_by": "golett_standard_demo"
                }
            )
            
            # Verify the session was created with the correct ID
            if created_session_id != self.session_id:
                print(f"⚠️  Warning: Expected session ID {self.session_id}, got {created_session_id}")
                self.session_id = created_session_id
            
            print(f"   ✅ Session created: {self.session_id}")
            
            # Initialize knowledge adapter with advanced features
            print("🧠 Initializing knowledge adapter...")
            self.knowledge_adapter = GolettKnowledgeAdapter(
                memory_manager=self.memory_manager,
                session_id=self.session_id,
                enable_advanced_features=True,
                default_memory_layer=MemoryLayer.LONG_TERM,
                cross_session_access=True,
                max_knowledge_age_days=30
            )
            
            # Create demo knowledge files
            await self._create_demo_files()
            
            print(f"✅ Demo setup complete!")
            print(f"📊 Normalized layers enabled: {self.memory_manager.enable_normalized_layers}")
            print()
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            print("\n💡 Make sure the databases are running:")
            print("   docker-compose up -d postgres qdrant")
            print("   Or check your environment variables in .env file")
            raise
        
    async def _create_demo_files(self):
        """Create comprehensive demo knowledge files for testing."""
        demo_dir = Path("demo_knowledge")
        demo_dir.mkdir(exist_ok=True)
        
        # Architecture guide (Long-term memory)
        architecture_content = """
# Golett Normalized Memory Architecture

## Overview
Golett implements a sophisticated three-layer memory architecture that provides
optimal storage and retrieval based on content importance and temporal relevance.

## Memory Layers

### Long-term Memory
- **Purpose**: Persistent knowledge across sessions
- **Retention**: 365 days
- **Importance Threshold**: 0.7+
- **Use Cases**: Core knowledge, important decisions, user preferences
- **Storage**: Separate PostgreSQL table and Qdrant collection

### Short-term Memory  
- **Purpose**: Session-scoped contextual information
- **Retention**: 30 days
- **Importance Threshold**: 0.5-0.7
- **Use Cases**: Session context, temporary decisions, workflow state
- **Storage**: Session-partitioned storage with automatic cleanup

### In-session Memory
- **Purpose**: Real-time conversation and immediate context
- **Retention**: 1 day
- **Importance Threshold**: 0.3-1.0 (variable)
- **Use Cases**: Current conversation, immediate decisions, working memory
- **Storage**: Highly optimized for fast access and frequent updates

## Benefits
- **Proper Isolation**: Each layer has dedicated storage preventing confusion
- **Optimized Performance**: Layer-specific optimization strategies
- **Intelligent Routing**: Automatic layer selection based on content analysis
- **Efficient Cleanup**: Layer-specific retention and cleanup policies
- **Cross-layer Search**: Unified search across all layers with proper weighting
"""
        
        # API integration guide (Short-term memory)
        api_content = """
# Golett API Integration Guide

## Memory Layer APIs

### Layer-Aware Storage
```python
# Store in specific layer
memory_manager.store_context(
    session_id=session_id,
    context_type="knowledge",
    data=content,
    memory_layer=MemoryLayer.LONG_TERM,
    importance=0.8
)

# Auto-determine layer based on importance
memory_manager.store_context(
    session_id=session_id,
    context_type="decision", 
    data=decision_data,
    importance=0.6  # Will go to SHORT_TERM
)
```

### Cross-Layer Retrieval
```python
# Search specific layers
results = memory_manager.retrieve_context(
    session_id=session_id,
    query="API integration",
    include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
    cross_session=True
)

# Search all layers with weighting
results = memory_manager.search_across_all_layers(
    query="memory architecture",
    session_id=session_id,
    include_layer_weights=True
)
```

### Layer Management
```python
# Get layer statistics
stats = memory_manager.get_layer_statistics()

# Cleanup expired memories
report = memory_manager.cleanup_expired_memories(
    layer=MemoryLayer.IN_SESSION,
    dry_run=False
)

# Migrate between layers
migration = memory_manager.migrate_memory_between_layers(
    source_layer=MemoryLayer.IN_SESSION,
    target_layer=MemoryLayer.SHORT_TERM,
    criteria={"importance_threshold": 0.6}
)
```
"""
        
        # Best practices (In-session memory)
        practices_content = """
# Golett Memory Layer Best Practices

## Layer Selection Guidelines

### Long-term Memory
- User preferences and settings
- Core business knowledge and documentation
- Important historical decisions
- Cross-session persistent data
- High-value insights and analysis

### Short-term Memory
- Session-specific workflow state
- Temporary user preferences
- Session-scoped decisions
- Intermediate processing results
- Context that spans multiple interactions

### In-session Memory
- Current conversation messages
- Immediate working context
- Real-time decision tracking
- Temporary calculations
- Current task state

## Performance Optimization

### Storage Strategy
- Use appropriate chunk sizes for each layer
- Implement proper indexing for frequent queries
- Configure retention policies based on usage patterns
- Monitor layer utilization and adjust thresholds

### Retrieval Strategy
- Use semantic search for content discovery
- Use structured search for precise queries
- Combine strategies for hybrid approaches
- Apply temporal boosting for recent content
- Use importance weighting for relevance ranking

### Maintenance Strategy
- Regular cleanup of expired content
- Migration of important content between layers
- Performance monitoring and optimization
- Backup and recovery procedures
"""
        
        # Create files with different target layers
        files_config = [
            ("architecture_guide.md", architecture_content, MemoryLayer.LONG_TERM, 0.9),
            ("api_integration.md", api_content, MemoryLayer.SHORT_TERM, 0.7),
            ("best_practices.md", practices_content, MemoryLayer.IN_SESSION, 0.5)
        ]
        
        for filename, content, layer, importance in files_config:
            file_path = demo_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.demo_files[filename] = {
                'path': str(file_path),
                'layer': layer,
                'importance': importance,
                'content_preview': content[:200] + "..."
            }
        
        print(f"📁 Created {len(files_config)} demo knowledge files")
        
    async def demonstrate_layer_separation(self):
        """Demonstrate proper layer separation and storage."""
        print("\n" + "="*60)
        print("🏗️  DEMONSTRATING LAYER SEPARATION")
        print("="*60)
        
        # Add knowledge sources to different layers
        for filename, config in self.demo_files.items():
            collection_name = f"demo_{filename.replace('.md', '')}"
            
            print(f"\n📄 Adding {filename} to {config['layer'].value} layer...")
            
            source = self.knowledge_adapter.add_advanced_file_source(
                file_path=config['path'],
                collection_name=collection_name,
                memory_layer=config['layer'],
                tags=[config['layer'].value, "demo", "documentation"],
                importance=config['importance'],
                chunk_size=800,
                overlap_size=100,
                enable_versioning=True
            )
            
            # Load and store the content
            print(f"     🔄 Loading content from {filename}...")
            content = source.load()
            print(f"     📝 Content length: {len(content)} characters")
            
            chunks = source.add()
            print(f"     ✅ Stored {len(chunks)} chunks")
            
            # Debug: Show context IDs
            context_ids = source.get_context_ids()
            print(f"     🆔 Context IDs: {context_ids[:3]}{'...' if len(context_ids) > 3 else ''}")
            
            # Test immediate retrieval
            print(f"     🔍 Testing immediate retrieval...")
            test_results = source.retrieve("memory architecture", limit=2)
            print(f"     📊 Immediate retrieval results: {len(test_results)}")
            if test_results:
                for i, result in enumerate(test_results[:1]):
                    content_preview = str(result.get("data", ""))[:100]
                    print(f"       {i+1}. {content_preview}...")
        
        # Add advanced memory source for cross-layer access
        print("\n   🔗 Adding cross-layer memory source...")
        memory_source = self.knowledge_adapter.add_advanced_memory_source(
            collection_names=list(self.demo_files.keys()),
            memory_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM, MemoryLayer.IN_SESSION],
            context_types=["knowledge", "bi_data", "decision", "conversation_summary"],
            tags=["demo", "advanced", "golett"],
            importance_threshold=0.3
        )
        
        # Display layer statistics
        print(f"\n📈 Memory Layer Statistics:")
        stats = self.memory_manager.get_layer_statistics()
        for layer_name, layer_stats in stats.items():
            if isinstance(layer_stats, dict) and 'config' in layer_stats:
                config = layer_stats['config']
                print(f"   {layer_name.upper()}:")
                print(f"     - Retention: {config['retention_days']} days")
                print(f"     - Importance threshold: {config['importance_threshold']}")
                print(f"     - Storage: {layer_stats['storage']['postgres_table']}")
                print(f"     - Collection: {layer_stats['storage']['qdrant_collection']}")
        
        print("✅ Layer separation demonstration complete!")
        print()
        
    async def demonstrate_retrieval_strategies(self):
        """Demonstrate different retrieval strategies across layers."""
        print("\n" + "="*60)
        print("🔍 DEMONSTRATING RETRIEVAL STRATEGIES")
        print("="*60)
        
        test_queries = [
            ("memory architecture", "Understanding the overall system design"),
            ("layer separation", "How layers are separated and managed"),
            ("best practices", "Guidelines for optimal usage"),
            ("performance optimization", "Improving system performance")
        ]
        
        strategies = [
            KnowledgeRetrievalStrategy.SEMANTIC,
            KnowledgeRetrievalStrategy.STRUCTURED,
            KnowledgeRetrievalStrategy.HYBRID,
            KnowledgeRetrievalStrategy.TEMPORAL,
            KnowledgeRetrievalStrategy.IMPORTANCE
        ]
        
        for query, description in test_queries:
            print(f"\n🔎 Query: '{query}' ({description})")
            print("-" * 50)
            
            for strategy in strategies:
                try:
                    results = self.knowledge_adapter.retrieve_knowledge(
                        query=query,
                        limit=3,
                        strategy=strategy
                    )
                    
                    print(f"   📋 Strategy: {strategy.value.title()}")
                    print(f"      Results: {len(results)}")
                    
                    for i, result in enumerate(results[:2], 1):
                        metadata = result.get('metadata', {})
                        content = result.get('data', result.get('content', ''))
                        if isinstance(content, dict):
                            content = str(content)
                        
                        layer = metadata.get('memory_layer', 'unknown')
                        importance = metadata.get('importance', 0)
                        source_type = result.get('source_type', 'unknown')
                        source = metadata.get('source', metadata.get('collection_name', 'unknown'))
                        
                        # Show content preview
                        content_preview = content[:80] + "..." if len(content) > 80 else content
                        
                        print(f"         {i}. [{source}] (layer: {layer}, importance: {importance:.2f})")
                        print(f"            {content_preview}")
                        
                except Exception as e:
                    print(f"   📋 Strategy: {strategy.value.title()}")
                    print(f"      ❌ Error: {e}")
            
            print()
        
        print("✅ Retrieval strategies demonstration complete!")
        print()
        
    async def demonstrate_cross_layer_operations(self):
        """Demonstrate cross-layer search and operations."""
        print("\n" + "="*60)
        print("🔄 DEMONSTRATING CROSS-LAYER OPERATIONS")
        print("="*60)
        
        # Cross-layer search with weighting
        print("\n🌐 Cross-layer search with layer weighting:")
        query = "memory layer architecture"
        
        try:
            results = self.knowledge_adapter.search_across_layers(
                query=query,
                limit=5,
                include_layer_weights=True
            )
            
            print(f"Found {len(results)} results across all layers:")
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                layer = metadata.get('searched_in_layer', metadata.get('memory_layer', 'unknown'))
                weighted_score = result.get('weighted_score', result.get('score', 0))
                original_score = result.get('score', 0)
                layer_weight = metadata.get('layer_weight_applied', 1.0)
                
                content = result.get('data', result.get('content', ''))
                if isinstance(content, dict):
                    content = str(content)
                content_preview = content[:100] + "..." if len(content) > 100 else content
                
                print(f"   {i}. Layer: {layer}")
                print(f"      Original score: {original_score:.3f}")
                print(f"      Layer weight: {layer_weight:.3f}")
                print(f"      Weighted score: {weighted_score:.3f}")
                print(f"      Preview: {content_preview}")
                print()
                
        except Exception as e:
            print(f"❌ Error in cross-layer search: {e}")
            # Fallback to regular retrieval
            print("📋 Fallback - Regular Knowledge Retrieval:")
            results = self.knowledge_adapter.retrieve_knowledge(
                query=query,
                limit=5,
                strategy=KnowledgeRetrievalStrategy.HYBRID
            )
            
            for i, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                content = result.get("data", result.get("content", ""))
                if isinstance(content, dict):
                    content = str(content)
                
                display_content = content[:100] + "..." if len(content) > 100 else content
                source_type = result.get("source_type", "unknown")
                layer = metadata.get("memory_layer", "unknown")
                
                print(f"   {i}. [{source_type}] (layer: {layer}) {display_content}")
        
        # Layer-specific retrieval
        print(f"\n🎯 Layer-specific retrieval:")
        for layer in MemoryLayer:
            try:
                results = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query="architecture",
                    limit=2,
                    include_layers=[layer],
                    cross_session=(layer == MemoryLayer.LONG_TERM)
                )
                
                print(f"   {layer.value.upper()}: {len(results)} results")
                for result in results:
                    metadata = result.get('metadata', {})
                    context_type = metadata.get('context_type', 'unknown')
                    importance = metadata.get('importance', 0)
                    print(f"     - Type: {context_type}, Importance: {importance:.2f}")
                    
            except Exception as e:
                print(f"   {layer.value.upper()}: Error - {e}")
        
        print("✅ Cross-layer operations demonstration complete!")
        print()
    
    async def demonstrate_memory_management(self):
        """Demonstrate memory management and optimization."""
        print("\n" + "="*60)
        print("🧹 DEMONSTRATING MEMORY MANAGEMENT")
        print("="*60)
        
        # Add some test data to different layers
        print("\n📝 Adding test data to different layers...")
        
        # Add to long-term memory
        long_term_id = self.memory_manager.store_context(
            session_id=self.session_id,
            context_type="knowledge",
            data={"type": "core_concept", "content": "Normalized memory architecture principles"},
            importance=0.9,
            metadata={"category": "architecture", "permanent": True},
            memory_layer=MemoryLayer.LONG_TERM
        )
        
        # Add to short-term memory
        short_term_id = self.memory_manager.store_context(
            session_id=self.session_id,
            context_type="session_state",
            data={"type": "workflow", "content": "Current demo session state"},
            importance=0.6,
            metadata={"category": "session", "temporary": True},
            memory_layer=MemoryLayer.SHORT_TERM
        )
        
        # Add to in-session memory
        in_session_id = self.memory_manager.store_context(
            session_id=self.session_id,
            context_type="conversation",
            data={"type": "message", "content": "Demo conversation context"},
            importance=0.4,
            metadata={"category": "conversation", "ephemeral": True},
            memory_layer=MemoryLayer.IN_SESSION
        )
        
        print(f"   ✅ Long-term: {long_term_id}")
        print(f"   ✅ Short-term: {short_term_id}")
        print(f"   ✅ In-session: {in_session_id}")
        
        # Get layer statistics
        print(f"\n📊 Current layer statistics:")
        stats = self.knowledge_adapter.get_memory_layer_stats()
        if isinstance(stats, dict) and "message" not in stats:
            for layer_name, layer_stats in stats.items():
                if isinstance(layer_stats, dict):
                    print(f"   {layer_name.upper()}:")
                    print(f"     - Config: {layer_stats.get('config', {})}")
                    print(f"     - Storage: {layer_stats.get('storage', {})}")
        else:
            print(f"   {stats}")
        
        # Demonstrate optimization
        print(f"\n⚡ Memory layer optimization:")
        optimization_report = self.knowledge_adapter.optimize_memory_layers()
        
        if isinstance(optimization_report, dict) and "message" not in optimization_report:
            # Handle the actual structure returned by cleanup_expired_memories
            for layer_name, layer_info in optimization_report.items():
                if isinstance(layer_info, dict) and "layer" in layer_info:
                    print(f"   {layer_name.replace('_', ' ').title()}:")
                    print(f"      Retention: {layer_info.get('retention_days', 'N/A')} days")
                    print(f"      Cutoff Date: {layer_info.get('cutoff_date', 'N/A')}")
                    print(f"      Deleted Count: {layer_info.get('deleted_count', 0)}")
                    print(f"      Dry Run: {layer_info.get('dry_run', True)}")
                    if layer_info.get('errors'):
                        print(f"      Errors: {layer_info['errors']}")
        else:
            print(f"   {optimization_report.get('message', 'Optimization not available')}")
        
        print("✅ Memory management demonstration complete!")
        print()
    
    async def demonstrate_collection_management(self):
        """Demonstrate knowledge collection management."""
        print("\n" + "="*60)
        print("📚 DEMONSTRATING COLLECTION MANAGEMENT")
        print("="*60)
        
        # List all collections
        collections = self.knowledge_adapter.list_collections()
        print(f"\n📋 Knowledge Collections ({len(collections)}):")
        
        for name, info in collections.items():
            print(f"\n   📁 {name}:")
            print(f"      - Sources: {len(info.get('sources', []))}")
            print(f"      - Memory layers: {list(info.get('memory_layers', set()))}")
            print(f"      - Total chunks: {info.get('total_chunks', 0)}")
            print(f"      - Created: {info.get('created_at', 'Unknown')}")
        
        # Get detailed info for a specific collection
        if collections:
            first_collection = list(collections.keys())[0]
            collection_info = self.knowledge_adapter.get_collection_info(first_collection)
            
            print(f"\n🔍 Detailed info for '{first_collection}':")
            if collection_info:
                for key, value in collection_info.items():
                    if key != 'sources':  # Don't print source objects
                        print(f"   {key}: {value}")
        
        # Show memory layer statistics
        print(f"\n🧠 Memory Layer Statistics:")
        layer_stats = self.knowledge_adapter.get_memory_layer_stats()
        if isinstance(layer_stats, dict) and "message" not in layer_stats:
            for layer, stats in layer_stats.items():
                print(f"   {layer.replace('_', ' ').title()}:")
                print(f"      Config: {stats.get('config', {})}")
                print(f"      Storage: {stats.get('storage', {})}")
        else:
            print(f"   {layer_stats.get('message', 'No layer statistics available')}")
        
        print("✅ Collection management demonstration complete!")
        print()
    
    async def interactive_chat(self):
        """Interactive chat session demonstrating real-time layer usage."""
        print("\n" + "="*60)
        print("💬 INTERACTIVE CHAT WITH LAYER AWARENESS")
        print("="*60)
        print("Type 'quit' to exit, 'help' for commands")
        
        while True:
            try:
                user_input = input("\n🤖 You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    self._show_chat_help()
                    continue
                elif user_input.lower().startswith('stats'):
                    await self._show_layer_stats()
                    continue
                elif user_input.lower().startswith('search '):
                    query = user_input[7:]
                    await self._perform_search(query)
                    continue
                
                # Store user message in in-session memory
                self.memory_manager.store_message(
                    session_id=self.session_id,
                    role="user",
                    content=user_input,
                    metadata={"importance": 0.5},
                    memory_layer=MemoryLayer.IN_SESSION
                )
                
                # Retrieve relevant knowledge
                knowledge_results = self.knowledge_adapter.retrieve_knowledge(
                    query=user_input,
                    limit=3,
                    strategy=KnowledgeRetrievalStrategy.HYBRID
                )
                
                # Generate response based on knowledge
                response = self._generate_response(user_input, knowledge_results)
                
                # Store assistant response
                self.memory_manager.store_message(
                    session_id=self.session_id,
                    role="assistant", 
                    content=response,
                    metadata={"importance": 0.6, "knowledge_used": len(knowledge_results)},
                    memory_layer=MemoryLayer.IN_SESSION
                )
                
                print(f"\n🤖 Assistant: {response}")
                
                if knowledge_results:
                    print(f"\n📚 Knowledge used ({len(knowledge_results)} sources):")
                    for i, result in enumerate(knowledge_results, 1):
                        metadata = result.get('metadata', {})
                        layer = metadata.get('memory_layer', 'unknown')
                        source_type = result.get('source_type', 'unknown')
                        print(f"   {i}. {source_type} from {layer} layer")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat session ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _show_chat_help(self):
        """Show chat help commands."""
        print("\n📖 Available commands:")
        print("   help          - Show this help")
        print("   stats         - Show layer statistics")
        print("   search <query> - Search across all layers")
        print("   quit          - Exit chat")
        print("\nJust type normally to chat and see layer-aware responses!")
    
    async def _show_layer_stats(self):
        """Show current layer statistics."""
        print("\n📊 Current Layer Statistics:")
        
        # Get session history from each layer
        for layer in MemoryLayer:
            history = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=10,
                include_layers=[layer]
            )
            
            message_count = len([h for h in history if h.get('metadata', {}).get('type') == 'message'])
            context_count = len([h for h in history if h.get('metadata', {}).get('type') == 'context'])
            
            print(f"   {layer.value.upper()}:")
            print(f"     - Messages: {message_count}")
            print(f"     - Context entries: {context_count}")
            print(f"     - Total items: {len(history)}")
    
    async def _perform_search(self, query: str):
        """Perform a search across all layers."""
        print(f"\n🔍 Searching for: '{query}'")
        
        results = self.knowledge_adapter.search_across_layers(
            query=query,
            limit=5,
            include_layer_weights=True
        )
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                layer = metadata.get('searched_in_layer', 'unknown')
                score = result.get('weighted_score', result.get('score', 0))
                
                content = ""
                if 'content' in result:
                    content = str(result['content'])[:100]
                elif 'data' in result:
                    content = str(result['data'])[:100]
                
                print(f"   {i}. [{layer}] Score: {score:.3f}")
                print(f"      {content}...")
        else:
            print("   No results found.")
    
    def _generate_response(self, user_input: str, knowledge_results: List[Dict[str, Any]]) -> str:
        """Generate a response based on user input and knowledge."""
        if not knowledge_results:
            return f"I understand you're asking about '{user_input}'. Let me help you with that based on my knowledge of Golett's normalized memory architecture."
        
        # Extract relevant information from knowledge
        relevant_info = []
        for result in knowledge_results:
            metadata = result.get('metadata', {})
            layer = metadata.get('memory_layer', 'unknown')
            
            content = ""
            if 'content' in result:
                content = str(result['content'])
            elif 'data' in result:
                data = result['data']
                if isinstance(data, dict):
                    content = str(data.get('content', data))
                else:
                    content = str(data)
            
            if content and len(content) > 50:
                relevant_info.append(f"From {layer} layer: {content[:200]}...")
        
        if relevant_info:
            response = f"Based on the information in my memory layers, here's what I found about '{user_input}':\n\n"
            response += "\n\n".join(relevant_info[:2])  # Limit to top 2 results
            response += f"\n\nThis information comes from {len(knowledge_results)} different sources across my memory layers."
        else:
            response = f"I found {len(knowledge_results)} relevant sources about '{user_input}', but they need more detailed analysis."
        
        return response
    
    async def run_complete_demo(self):
        """Run the complete demo showcasing all features."""
        try:
            await self.setup()
            
            print("🎯 Running Normalized Memory Layer Demonstrations")
            print("=" * 80)
            print()
            
            # Run all demonstrations in sequence
            await self.demonstrate_layer_separation()
            await self.demonstrate_retrieval_strategies()
            await self.demonstrate_cross_layer_operations()
            await self.demonstrate_memory_management()
            await self.demonstrate_collection_management()
            
            print("\n" + "="*60)
            print("🎉 DEMO COMPLETE!")
            print("="*60)
            print("The normalized memory layer architecture has been successfully demonstrated.")
            print("Key benefits shown:")
            print("  ✅ Proper layer separation and isolation")
            print("  ✅ Intelligent layer routing based on importance")
            print("  ✅ Advanced retrieval strategies across layers")
            print("  ✅ Cross-layer search with proper weighting")
            print("  ✅ Memory management and optimization")
            print("  ✅ Collection-based knowledge organization")
            
            # Offer interactive chat
            chat_choice = input("\n🤖 Would you like to try the interactive chat? (y/n): ").strip().lower()
            if chat_choice in ['y', 'yes']:
                await self.interactive_chat()
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
            print(f"\n❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        print(f"\n🧹 Cleaning up demo session...")
        try:
            # MemoryManager doesn't have a close method, so we'll just clear our reference
            if self.memory_manager:
                self.memory_manager = None
            
            # Optionally remove demo files
            demo_dir = Path("demo_knowledge")
            if demo_dir.exists():
                import shutil
                shutil.rmtree(demo_dir)
                print("🗑️  Removed demo files")
            
            print(f"   Session {self.session_id} data preserved for inspection")
            print("✅ Cleanup complete!")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


async def main():
    """Main demo function."""
    print("🚀 Golett Normalized Memory Layers Demo - Standard Edition")
    print("=" * 70)
    print()
    print("This demo showcases Golett's advanced normalized memory layer architecture:")
    print("• Three-layer memory system (long-term, short-term, in-session)")
    print("• Proper layer separation and isolation")
    print("• Advanced retrieval strategies across layers")
    print("• Cross-layer search with intelligent weighting")
    print("• Memory management and optimization")
    print("• Collection-based knowledge organization")
    print("• Layer-aware knowledge source management")
    print()
    
    demo = NormalizedMemoryLayersDemo()
    await demo.run_complete_demo()
    
    print("\n👋 Thank you for exploring Golett's normalized memory architecture!")


if __name__ == "__main__":
    asyncio.run(main()) 