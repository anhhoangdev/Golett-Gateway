#!/usr/bin/env python3
"""
Enhanced Golett Native Knowledge System Demo

This demo showcases Golett's advanced knowledge management capabilities including:
- Multi-layer memory architecture (long-term, short-term, in-session)
- Advanced knowledge sources with sophisticated retrieval strategies
- Collection-based knowledge organization
- Pagination and filtering capabilities
- Cross-session knowledge persistence
- Memory layer optimization
- Knowledge versioning and updates
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from golett.memory.memory_manager import MemoryManager
from golett.chat.crew import GolettKnowledgeAdapter
from golett.knowledge.sources import (
    GolettAdvancedTextFileKnowledgeSource,
    GolettAdvancedMemoryKnowledgeSource,
    MemoryLayer,
    KnowledgeRetrievalStrategy
)
from golett.utils.logger import get_logger
from golett.memory.session.session_manager import SessionManager

logger = get_logger(__name__)


class AdvancedKnowledgeDemo:
    """Enhanced demo showcasing Golett's advanced knowledge capabilities."""
    
    def __init__(self):
        """Initialize the advanced knowledge demo."""
        self.session_id = f"advanced_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.memory_manager = None
        self.knowledge_adapter = None
        self.demo_files = {}
        
        print("🚀 Initializing Enhanced Golett Knowledge System Demo")
        print(f"📋 Session ID: {self.session_id}")
        print("=" * 80)
    
    async def initialize(self):
        """Initialize the memory manager and knowledge adapter."""
        try:
            # Check OpenAI API key first
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                print("❌ Error: OPENAI_API_KEY environment variable not set")
                print("💡 Please set your OpenAI API key:")
                print("   export OPENAI_API_KEY='your-api-key-here'")
                raise ValueError("Missing OpenAI API key")
            
            print("🔧 Setting up memory manager...")
            
            # Get database connection parameters from environment
            postgres_connection = os.getenv(
                "POSTGRES_CONNECTION", 
                "postgresql://golett_user:golett_password@localhost:5432/golett_db"
            )
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            
            print(f"   📊 PostgreSQL: {postgres_connection.split('@')[1] if '@' in postgres_connection else 'localhost'}")
            print(f"   🔍 Qdrant: {qdrant_url}")
            
            self.memory_manager = MemoryManager(
                postgres_connection=postgres_connection,
                qdrant_url=qdrant_url
            )
            
            # Create session properly in session manager
            print("🔧 Creating demo session...")
            session_manager = SessionManager(self.memory_manager)
            
            # Create session with proper metadata
            created_session_id = session_manager.create_session(
                user_id="demo_user",
                session_type="knowledge_demo",
                preferences={"demo_mode": True},
                metadata={
                    "session_id": self.session_id,
                    "demo_type": "advanced_knowledge",
                    "created_by": "golett_demo"
                }
            )
            
            # Verify the session was created with the correct ID
            if created_session_id != self.session_id:
                print(f"⚠️  Warning: Expected session ID {self.session_id}, got {created_session_id}")
                self.session_id = created_session_id
            
            print(f"   ✅ Session created: {self.session_id}")
            
            print("🧠 Initializing advanced knowledge adapter...")
            self.knowledge_adapter = GolettKnowledgeAdapter(
                memory_manager=self.memory_manager,
                session_id=self.session_id,
                enable_advanced_features=True,
                default_memory_layer=MemoryLayer.LONG_TERM,
                cross_session_access=True,
                max_knowledge_age_days=30
            )
            
            print("✅ Initialization complete!")
            print()
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            print("\n💡 Make sure the databases are running:")
            print("   docker-compose up -d postgres qdrant")
            print("   Or check your environment variables in .env file")
            raise
    
    def create_demo_knowledge_files(self):
        """Create comprehensive demo knowledge files for testing."""
        print("📝 Creating enhanced demo knowledge files...")
        
        # Create demo directory
        demo_dir = Path("demo_knowledge_advanced")
        demo_dir.mkdir(exist_ok=True)
        
        # 1. Golett Architecture Guide (Long-term memory)
        architecture_content = """
# Golett Framework Architecture Guide

## Overview
Golett is a sophisticated conversational agent framework that provides advanced memory management, 
contextual understanding, and multi-layered persistence capabilities.

## Core Components

### Memory Architecture
Golett implements a three-layer memory system:

1. **Long-term Memory**: Persistent across sessions, stored in PostgreSQL and Qdrant
   - High importance knowledge (>0.7)
   - Cross-session accessibility
   - Automatic summarization and indexing
   - Retention: 365 days

2. **Short-term Memory**: Session-scoped memory for current context
   - Medium importance knowledge (0.5-0.7)
   - Session-specific context
   - Temporary working memory
   - Retention: 30 days

3. **In-session Memory**: Real-time conversation context
   - Variable importance (0.3-1.0)
   - Current conversation flow
   - Immediate decision context
   - Retention: 1 day

### Knowledge Management
- Advanced chunking with context preservation
- Semantic search using vector embeddings
- Structured search using PostgreSQL
- Hybrid retrieval strategies
- Knowledge versioning and updates
- Collection-based organization

### Business Intelligence Integration
- Real-time data processing
- Customer analytics and insights
- Performance metrics tracking
- Automated reporting capabilities
- Decision support systems

## Advanced Features

### Retrieval Strategies
1. **Semantic**: Vector-based similarity search
2. **Structured**: SQL-based precise queries
3. **Hybrid**: Combined semantic and structured
4. **Temporal**: Time-based prioritization
5. **Importance**: Relevance-weighted results

### Memory Layer Optimization
- Automatic importance adjustment
- Access pattern analysis
- Cross-session knowledge migration
- Performance monitoring
- Resource optimization

### Collection Management
- Hierarchical knowledge organization
- Tag-based categorization
- Version control and updates
- Metadata enrichment
- Access control and permissions
"""
        
        # 2. API Integration Guide (Short-term memory)
        api_content = """
# Golett API Integration Guide

## REST API Endpoints

### Memory Management
- GET /api/memory/sessions - List active sessions
- POST /api/memory/context - Store context
- GET /api/memory/context/{id} - Retrieve context
- DELETE /api/memory/context/{id} - Remove context

### Knowledge Management
- POST /api/knowledge/collections - Create collection
- GET /api/knowledge/collections - List collections
- POST /api/knowledge/sources - Add knowledge source
- GET /api/knowledge/search - Search knowledge

### Business Intelligence
- GET /api/bi/customers - Customer analytics
- GET /api/bi/performance - Performance metrics
- POST /api/bi/reports - Generate reports
- GET /api/bi/insights - AI-generated insights

## WebSocket Integration
Real-time communication for:
- Live conversation updates
- Memory synchronization
- Knowledge notifications
- BI data streaming

## Authentication
- JWT token-based authentication
- Role-based access control
- Session management
- API key authentication

## Rate Limiting
- 1000 requests per hour for standard users
- 10000 requests per hour for premium users
- Burst allowance: 100 requests per minute

## Error Handling
Standard HTTP status codes with detailed error messages:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error
"""
        
        # 3. Implementation Best Practices (In-session memory)
        practices_content = """
# Golett Implementation Best Practices

## Memory Management Best Practices

### Layer Selection Guidelines
1. **Long-term Memory**: Use for persistent knowledge, user preferences, learned patterns
2. **Short-term Memory**: Use for session context, temporary data, working memory
3. **In-session Memory**: Use for current conversation, immediate context, real-time decisions

### Importance Scoring
- 0.9-1.0: Critical system knowledge, user preferences
- 0.7-0.8: Important domain knowledge, frequently accessed data
- 0.5-0.6: General information, moderate relevance
- 0.3-0.4: Contextual information, temporary relevance
- 0.1-0.2: Debug information, low priority data

### Chunking Strategies
- Use paragraph-based chunking for natural boundaries
- Implement overlap (100-200 characters) for context preservation
- Adjust chunk size based on content type (1000-2000 characters)
- Consider semantic boundaries for technical content

## Knowledge Source Design

### File-based Sources
- Organize by topic and importance level
- Use descriptive collection names
- Implement proper tagging strategies
- Enable versioning for dynamic content

### Memory-based Sources
- Filter by relevance and recency
- Use appropriate context types
- Implement cross-session access carefully
- Monitor performance and optimize

## Performance Optimization

### Retrieval Optimization
- Use hybrid strategies for best results
- Implement pagination for large result sets
- Cache frequently accessed knowledge
- Monitor query performance

### Memory Optimization
- Regular cleanup of expired content
- Importance-based archiving
- Cross-session knowledge migration
- Resource usage monitoring

## Security Considerations

### Data Protection
- Encrypt sensitive knowledge
- Implement access controls
- Audit knowledge access
- Secure API endpoints

### Privacy Compliance
- GDPR compliance for EU users
- Data retention policies
- User consent management
- Right to be forgotten implementation

## Monitoring and Analytics

### Performance Metrics
- Query response times
- Memory usage patterns
- Knowledge access frequency
- User engagement metrics

### Quality Metrics
- Knowledge relevance scores
- User satisfaction ratings
- Accuracy measurements
- Coverage analysis
"""
        
        # 4. Troubleshooting Guide (Mixed memory layers)
        troubleshooting_content = """
# Golett Troubleshooting Guide

## Common Issues and Solutions

### Memory Management Issues

#### High Memory Usage
**Symptoms**: Slow response times, memory warnings
**Causes**: 
- Too many active sessions
- Large knowledge chunks
- Inefficient queries
**Solutions**:
- Implement session cleanup
- Optimize chunk sizes
- Use pagination
- Monitor memory usage

#### Knowledge Not Found
**Symptoms**: Empty search results, missing context
**Causes**:
- Incorrect memory layer
- Expired content
- Wrong collection name
**Solutions**:
- Check memory layer configuration
- Verify retention settings
- Update collection mappings
- Review importance thresholds

### Performance Issues

#### Slow Query Response
**Symptoms**: Long wait times, timeouts
**Causes**:
- Large result sets
- Complex queries
- Database performance
**Solutions**:
- Implement result limits
- Use appropriate indexes
- Optimize query strategies
- Consider caching

#### Memory Leaks
**Symptoms**: Gradually increasing memory usage
**Causes**:
- Unclosed connections
- Retained references
- Large object accumulation
**Solutions**:
- Implement proper cleanup
- Use connection pooling
- Monitor object lifecycle
- Regular garbage collection

### Integration Issues

#### API Connection Failures
**Symptoms**: Connection timeouts, authentication errors
**Causes**:
- Network issues
- Invalid credentials
- Rate limiting
**Solutions**:
- Check network connectivity
- Verify API credentials
- Implement retry logic
- Monitor rate limits

#### Data Synchronization Problems
**Symptoms**: Inconsistent data, missing updates
**Causes**:
- Race conditions
- Transaction failures
- Network interruptions
**Solutions**:
- Implement proper locking
- Use transactions
- Add retry mechanisms
- Monitor sync status

## Diagnostic Tools

### Logging Configuration
- Enable debug logging for troubleshooting
- Use structured logging formats
- Implement log rotation
- Monitor log levels

### Performance Monitoring
- Track response times
- Monitor memory usage
- Analyze query patterns
- Set up alerts

### Health Checks
- Database connectivity
- Memory manager status
- Knowledge source availability
- API endpoint health

## Recovery Procedures

### Data Recovery
- Backup and restore procedures
- Point-in-time recovery
- Cross-session data migration
- Emergency data export

### System Recovery
- Service restart procedures
- Configuration rollback
- Database recovery
- Cache invalidation
"""
        
        # Write files to disk
        files_to_create = {
            "golett_architecture.md": (architecture_content, MemoryLayer.LONG_TERM, ["architecture", "core", "memory"], 0.9),
            "api_integration.md": (api_content, MemoryLayer.SHORT_TERM, ["api", "integration", "endpoints"], 0.7),
            "best_practices.md": (practices_content, MemoryLayer.IN_SESSION, ["practices", "guidelines", "optimization"], 0.8),
            "troubleshooting.md": (troubleshooting_content, MemoryLayer.LONG_TERM, ["troubleshooting", "issues", "solutions"], 0.6)
        }
        
        for filename, (content, layer, tags, importance) in files_to_create.items():
            file_path = demo_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.demo_files[filename] = {
                "path": str(file_path),
                "layer": layer,
                "tags": tags,
                "importance": importance,
                "size": len(content)
            }
        
        print(f"✅ Created {len(files_to_create)} enhanced demo files")
        for filename, info in self.demo_files.items():
            print(f"   📄 {filename} ({info['size']} chars, {info['layer'].value} layer)")
        print()
    
    async def setup_advanced_knowledge_sources(self):
        """Set up advanced knowledge sources with different memory layers."""
        print("🧠 Setting up advanced knowledge sources...")
        
        # Add file-based sources with different memory layers
        for filename, info in self.demo_files.items():
            collection_name = filename.replace('.md', '').replace('_', '-')
            
            print(f"   📚 Adding {filename} to {info['layer'].value} memory...")
            
            source = self.knowledge_adapter.add_advanced_file_source(
                file_path=info["path"],
                collection_name=collection_name,
                memory_layer=info["layer"],
                tags=info["tags"],
                importance=info["importance"],
                chunk_size=1200,  # Larger chunks for better context
                overlap_size=150,  # More overlap for continuity
                enable_versioning=True
            )
            
            # Add content to memory
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
            
            # Debug: Test direct memory manager retrieval
            print(f"     🔧 Testing direct memory manager retrieval...")
            direct_results = self.memory_manager.retrieve_context(
                session_id=self.session_id,
                query="memory architecture",
                context_types=["knowledge"],
                limit=2
            )
            print(f"     📊 Direct memory manager results: {len(direct_results)}")
            if direct_results:
                for i, result in enumerate(direct_results[:1]):
                    content_preview = str(result.get("data", ""))[:100]
                    print(f"       {i+1}. {content_preview}...")
            
            # Debug: Test Qdrant search without session filter
            print(f"     🔧 Testing Qdrant search without session filter...")
            qdrant_results = self.memory_manager.qdrant.search(
                query="memory architecture",
                limit=2,
                score_threshold=0.1  # Very low threshold
            )
            print(f"     📊 Qdrant results (no session filter): {len(qdrant_results)}")
            if qdrant_results:
                for i, result in enumerate(qdrant_results[:1]):
                    content_preview = str(result.get("data", ""))[:100]
                    print(f"       {i+1}. {content_preview}...")
            
            # Debug: Test Qdrant search with session filter
            print(f"     🔧 Testing Qdrant search with session filter...")
            qdrant_results_filtered = self.memory_manager.qdrant.search(
                query="memory architecture",
                limit=2,
                score_threshold=0.1,
                session_id=self.session_id
            )
            print(f"     📊 Qdrant results (with session filter): {len(qdrant_results_filtered)}")
            if qdrant_results_filtered:
                for i, result in enumerate(qdrant_results_filtered[:1]):
                    content_preview = str(result.get("data", ""))[:100]
                    print(f"       {i+1}. {content_preview}...")
        
        # Add advanced memory source for cross-layer access
        print("   🔗 Adding cross-layer memory source...")
        memory_source = self.knowledge_adapter.add_advanced_memory_source(
            collection_names=list(self.demo_files.keys()),
            memory_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM, MemoryLayer.IN_SESSION],
            context_types=["knowledge", "bi_data", "decision", "conversation_summary"],
            tags=["demo", "advanced", "golett"],
            importance_threshold=0.3
        )
        
        print("✅ Advanced knowledge sources setup complete!")
        print()
    
    def demonstrate_collection_management(self):
        """Demonstrate collection management capabilities."""
        print("📚 Collection Management Demonstration")
        print("-" * 50)
        
        # Get collections from the knowledge adapter
        collections = self.knowledge_adapter.list_collections()
        print(f"📋 Total Collections: {len(collections)}")
        
        for collection_name, collection_info in collections.items():
            print(f"   📁 {collection_name}")
            print(f"      Memory layers: {list(collection_info.get('memory_layers', set()))}")
            print(f"      Total chunks: {collection_info.get('total_chunks', 0)}")
            print(f"      Sources: {len(collection_info.get('sources', []))}")
            print(f"      Created: {collection_info.get('created_at', 'Unknown')}")
            print()
        
        # Get memory layer statistics
        layer_stats = self.knowledge_adapter.get_memory_layer_stats()
        print("🧠 Memory Layer Statistics:")
        if isinstance(layer_stats, dict) and "message" not in layer_stats:
            for layer, stats in layer_stats.items():
                print(f"   {layer.replace('_', ' ').title()}:")
                print(f"      Config: {stats.get('config', {})}")
                print(f"      Storage: {stats.get('storage', {})}")
                print()
        else:
            print(f"   {layer_stats.get('message', 'No statistics available')}")
        
        # Get collection info for first collection if available
        if collections:
            first_collection_name = list(collections.keys())[0]
            collection_info = self.knowledge_adapter.get_collection_info(first_collection_name)
            print(f"ℹ️  Detailed info for '{first_collection_name}':")
            if collection_info:
                for key, value in collection_info.items():
                    if key != 'sources':  # Don't print source objects
                        print(f"   {key}: {value}")
            print()
        
        print()
    
    async def demonstrate_retrieval_strategies(self):
        """Demonstrate different retrieval strategies."""
        print("🔍 Advanced Retrieval Strategies Demonstration")
        print("-" * 60)
        
        test_queries = [
            "How does Golett's memory architecture work?",
            "What are the API endpoints for knowledge management?",
            "Best practices for memory optimization",
            "Troubleshooting slow query performance"
        ]
        
        strategies = [
            KnowledgeRetrievalStrategy.SEMANTIC,
            KnowledgeRetrievalStrategy.STRUCTURED,
            KnowledgeRetrievalStrategy.HYBRID,
            KnowledgeRetrievalStrategy.TEMPORAL,
            KnowledgeRetrievalStrategy.IMPORTANCE
        ]
        
        for query in test_queries:
            print(f"🔎 Query: '{query}'")
            print()
            
            for strategy in strategies:
                print(f"   📋 Strategy: {strategy.value.title()}")
                
                try:
                    results = self.knowledge_adapter.retrieve_knowledge(
                        query=query,
                        limit=3,
                        strategy=strategy
                    )
                    
                    print(f"      Results: {len(results)}")
                    
                    for i, result in enumerate(results[:2], 1):  # Show top 2 results
                        metadata = result.get("metadata", {})
                        content = result.get("data", "")
                        if isinstance(content, dict):
                            content = str(content)
                        
                        # Truncate content for display
                        display_content = content[:100] + "..." if len(content) > 100 else content
                        
                        print(f"         {i}. [{metadata.get('source', 'unknown')}] "
                              f"(importance: {metadata.get('importance', 0):.2f}) "
                              f"{display_content}")
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                
                print()
            
            print("-" * 40)
            print()
    
    async def demonstrate_pagination(self):
        """Demonstrate pagination capabilities using individual knowledge sources."""
        print("📄 Pagination Demonstration")
        print("-" * 40)
        
        query = "Golett framework features and capabilities"
        page_size = 3
        
        print(f"🔎 Query: '{query}'")
        print(f"📄 Page Size: {page_size}")
        print()
        
        # Get the first Golett source for pagination demo
        if not self.knowledge_adapter.golett_sources:
            print("❌ No Golett sources available for pagination demo")
            return
        
        first_source = self.knowledge_adapter.golett_sources[0]
        
        # Get first page using the source's pagination method
        try:
            results, pagination_info = first_source.paginate_retrieve(
                query=query,
                page=1,
                page_size=page_size,
                strategy=KnowledgeRetrievalStrategy.HYBRID
            )
            
            print(f"📊 Pagination Info:")
            print(f"   Total Results: {pagination_info['total_count']}")
            print(f"   Total Pages: {pagination_info['total_pages']}")
            print(f"   Current Page: {pagination_info['page']}")
            print(f"   Page Size: {pagination_info['page_size']}")
            print(f"   Has Next: {pagination_info['has_next']}")
            print(f"   Has Previous: {pagination_info['has_prev']}")
            print()
            
            # Show results from first page
            print("📋 Page 1 Results:")
            for i, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                content = result.get("data", result.get("content", ""))
                if isinstance(content, dict):
                    content = str(content)
                
                display_content = content[:80] + "..." if len(content) > 80 else content
                
                print(f"   {i}. [{metadata.get('collection_name', 'unknown')}] "
                      f"(layer: {metadata.get('memory_layer', 'unknown')}) "
                      f"{display_content}")
            
            print()
            
            # Get second page if available
            if pagination_info['has_next']:
                print("📋 Page 2 Results:")
                results_page2, _ = first_source.paginate_retrieve(
                    query=query,
                    page=2,
                    page_size=page_size,
                    strategy=KnowledgeRetrievalStrategy.HYBRID
                )
                
                for i, result in enumerate(results_page2, 1):
                    metadata = result.get("metadata", {})
                    content = result.get("data", result.get("content", ""))
                    if isinstance(content, dict):
                        content = str(content)
                    
                    display_content = content[:80] + "..." if len(content) > 80 else content
                    
                    print(f"   {i}. [{metadata.get('collection_name', 'unknown')}] "
                          f"(layer: {metadata.get('memory_layer', 'unknown')}) "
                          f"{display_content}")
            
        except Exception as e:
            print(f"❌ Error during pagination demo: {e}")
            # Fallback: show regular retrieval
            print("📋 Fallback - Regular Retrieval:")
            results = self.knowledge_adapter.retrieve_knowledge(
                query=query,
                limit=page_size * 2,
                strategy=KnowledgeRetrievalStrategy.HYBRID
            )
            
            for i, result in enumerate(results[:page_size], 1):
                metadata = result.get("metadata", {})
                content = result.get("data", result.get("content", ""))
                if isinstance(content, dict):
                    content = str(content)
                
                display_content = content[:80] + "..." if len(content) > 80 else content
                
                print(f"   {i}. [{metadata.get('source_type', 'unknown')}] "
                      f"{display_content}")
        
        print()
    
    async def demonstrate_layer_optimization(self):
        """Demonstrate memory layer optimization."""
        print("⚡ Memory Layer Optimization Demonstration")
        print("-" * 55)
        
        # Run optimization analysis
        optimization_report = self.knowledge_adapter.optimize_memory_layers()
        
        print("📊 Layer Analysis:")
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
                    print()
        else:
            print(f"❌ Demo error: {optimization_report}")
        
        print("💡 Recommendations:")
        # Generate some basic recommendations based on the cleanup report
        if isinstance(optimization_report, dict) and "message" not in optimization_report:
            recommendations = []
            for layer_name, layer_info in optimization_report.items():
                if isinstance(layer_info, dict):
                    deleted_count = layer_info.get('deleted_count', 0)
                    if deleted_count > 0:
                        recommendations.append(f"Cleaned up {deleted_count} expired items from {layer_name} layer")
                    elif layer_info.get('dry_run', True):
                        recommendations.append(f"Run actual cleanup for {layer_name} layer (currently in dry-run mode)")
            
            if recommendations:
                for recommendation in recommendations:
                    print(f"   • {recommendation}")
            else:
                print("   ✅ No optimization recommendations at this time")
        else:
            print("   ℹ️  Optimization analysis not available")
        
        print()
        
        print("🔍 Actions Taken:")
        if isinstance(optimization_report, dict) and "message" not in optimization_report:
            actions = []
            for layer_name, layer_info in optimization_report.items():
                if isinstance(layer_info, dict):
                    if not layer_info.get('dry_run', True):
                        deleted_count = layer_info.get('deleted_count', 0)
                        if deleted_count > 0:
                            actions.append(f"Deleted {deleted_count} expired items from {layer_name} layer")
                        else:
                            actions.append(f"Analyzed {layer_name} layer (no items to delete)")
                    else:
                        actions.append(f"Analyzed {layer_name} layer (dry run)")
            
            if actions:
                for action in actions:
                    print(f"   ✓ {action}")
            else:
                print("   ℹ️  No automatic actions taken")
        else:
            print("   ℹ️  No actions taken")
        
        print()
    
    async def demonstrate_cross_layer_search(self):
        """Demonstrate cross-layer search with weighted results."""
        print("🌐 Cross-Layer Search Demonstration")
        print("-" * 45)
        
        query = "memory management and optimization"
        
        print(f"🔎 Query: '{query}'")
        print()
        
        # Note: Layer weights are handled internally by the memory manager
        print("ℹ️  Using internal layer weighting strategy")
        print()
        
        # Perform cross-layer search
        try:
            results = self.knowledge_adapter.search_across_layers(
                query=query,
                limit=10,
                include_layer_weights=True
            )
            
            print(f"📋 Cross-Layer Results ({len(results)} total):")
            for i, result in enumerate(results[:5], 1):  # Show top 5
                metadata = result.get("metadata", {})
                content = result.get("data", result.get("content", ""))
                if isinstance(content, dict):
                    content = str(content)
                
                display_content = content[:100] + "..." if len(content) > 100 else content
                
                layer = metadata.get("retrieved_from_layer", metadata.get("memory_layer", "unknown"))
                importance = metadata.get("importance", 0)
                source_type = result.get("source_type", "unknown")
                
                print(f"   {i}. [{layer.replace('_', ' ').title()}] ({source_type})")
                print(f"      Importance: {importance:.2f}")
                print(f"      {display_content}")
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
                
                print(f"   {i}. [{source_type}] {display_content}")
            print()
    
    async def interactive_chat_demo(self):
        """Interactive chat demonstration with advanced knowledge."""
        print("💬 Interactive Chat with Advanced Knowledge")
        print("-" * 50)
        print("Ask questions about Golett's features, architecture, or best practices.")
        print("Type 'quit' to exit, 'help' for commands, or 'stats' for statistics.")
        print()
        
        while True:
            try:
                user_input = input("🤔 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("📋 Available commands:")
                    print("   • 'stats' - Show knowledge statistics")
                    print("   • 'collections' - List all collections")
                    print("   • 'layers' - Show memory layer info")
                    print("   • 'optimize' - Run optimization analysis")
                    print("   • 'quit' - Exit chat")
                    print()
                    continue
                
                if user_input.lower() == 'stats':
                    collections = self.knowledge_adapter.list_collections()
                    print(f"📊 Knowledge Statistics:")
                    print(f"   Collections: {len(collections)}")
                    print(f"   Session: {self.session_id}")
                    print()
                    continue
                
                if user_input.lower() == 'collections':
                    collections = self.knowledge_adapter.list_collections()
                    print("📁 Collections:")
                    for collection_name, collection_info in collections.items():
                        memory_layers = list(collection_info.get('memory_layers', set()))
                        print(f"   • {collection_name} (layers: {memory_layers})")
                    print()
                    continue
                
                if user_input.lower() == 'layers':
                    layer_stats = self.knowledge_adapter.get_memory_layer_stats()
                    print("🧠 Memory Layers:")
                    if isinstance(layer_stats, dict) and "message" not in layer_stats:
                        for layer, stats in layer_stats.items():
                            print(f"   • {layer.replace('_', ' ').title()}: {stats}")
                    else:
                        print(f"   {layer_stats.get('message', 'No layer statistics available')}")
                    print()
                    continue
                
                if user_input.lower() == 'optimize':
                    report = self.knowledge_adapter.optimize_memory_layers()
                    print("⚡ Optimization Report:")
                    if isinstance(report, dict) and "message" not in report:
                        recommendations = report.get("recommendations", [])
                        for rec in recommendations[:3]:
                            print(f"   • {rec}")
                        if not recommendations:
                            print("   ✅ No recommendations")
                    else:
                        print(f"   {report.get('message', 'Optimization not available')}")
                    print()
                    continue
                
                if not user_input:
                    continue
                
                # Retrieve relevant knowledge
                print("🔍 Searching knowledge base...")
                
                results = self.knowledge_adapter.retrieve_knowledge(
                    query=user_input,
                    limit=5,
                    strategy=KnowledgeRetrievalStrategy.HYBRID
                )
                
                if results:
                    print(f"🤖 Golett: Based on my knowledge base, here's what I found:")
                    print()
                    
                    # Combine and summarize results
                    relevant_info = []
                    for result in results[:3]:  # Use top 3 results
                        content = result.get("data", "")
                        if isinstance(content, dict):
                            content = str(content)
                        
                        metadata = result.get("metadata", {})
                        source = metadata.get("collection_name", "unknown")
                        layer = metadata.get("memory_layer", "unknown")
                        importance = metadata.get("importance", 0)
                        
                        # Extract relevant snippet
                        snippet = content[:300] + "..." if len(content) > 300 else content
                        relevant_info.append(f"[{source}] {snippet}")
                    
                    for i, info in enumerate(relevant_info, 1):
                        print(f"{i}. {info}")
                        print()
                    
                    print(f"📚 Found {len(results)} relevant knowledge chunks across memory layers.")
                    
                else:
                    print("🤖 Golett: I couldn't find specific information about that in my knowledge base.")
                    print("Try asking about Golett's architecture, API integration, best practices, or troubleshooting.")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
    
    async def cleanup(self):
        """Clean up resources."""
        print("🧹 Cleaning up resources...")
        
        try:
            # MemoryManager doesn't have a close method, so we'll just clear our reference
            if self.memory_manager:
                self.memory_manager = None
            
            # Optionally remove demo files
            demo_dir = Path("demo_knowledge_advanced")
            if demo_dir.exists():
                import shutil
                shutil.rmtree(demo_dir)
                print("🗑️  Removed demo files")
            
            print("✅ Cleanup complete!")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")
    
    async def run_full_demo(self):
        """Run the complete advanced knowledge demo."""
        try:
            await self.initialize()
            self.create_demo_knowledge_files()
            await self.setup_advanced_knowledge_sources()
            
            print("🎯 Running Advanced Knowledge System Demonstrations")
            print("=" * 80)
            print()
            
            # Run all demonstrations
            self.demonstrate_collection_management()
            await self.demonstrate_retrieval_strategies()
            await self.demonstrate_pagination()
            await self.demonstrate_layer_optimization()
            await self.demonstrate_cross_layer_search()
            
            # Interactive chat
            await self.interactive_chat_demo()
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.cleanup()


async def main():
    """Main demo function."""
    print("🚀 Enhanced Golett Native Knowledge System Demo")
    print("=" * 80)
    print()
    print("This demo showcases Golett's advanced knowledge management capabilities:")
    print("• Multi-layer memory architecture (long-term, short-term, in-session)")
    print("• Advanced retrieval strategies (semantic, structured, hybrid, temporal, importance)")
    print("• Collection-based knowledge organization")
    print("• Pagination and filtering capabilities")
    print("• Cross-session knowledge persistence")
    print("• Memory layer optimization")
    print("• Knowledge versioning and updates")
    print()
    
    demo = AdvancedKnowledgeDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main()) 