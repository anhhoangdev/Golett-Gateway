# Golett AI - API Reference

## Overview

This document provides a comprehensive reference for all APIs and interfaces available in Golett AI. The framework provides both programmatic APIs for direct integration and RESTful APIs for web-based applications.

## Table of Contents

1. [Core Memory APIs](#core-memory-apis)
2. [Knowledge Management APIs](#knowledge-management-apis)
3. [Session Management APIs](#session-management-apis)
4. [Chat Flow APIs](#chat-flow-apis)
5. [Agent Coordination APIs](#agent-coordination-apis)
6. [Storage APIs](#storage-apis)
7. [RESTful Web APIs](#restful-web-apis)
8. [WebSocket APIs](#websocket-apis)
9. [Error Handling](#error-handling)
10. [Authentication](#authentication)

---

## Core Memory APIs

### MemoryManager

**Location**: `golett.memory.MemoryManager`

#### Initialization

```python
from golett.memory import MemoryManager, MemoryLayer

memory_manager = MemoryManager(
    postgres_connection="postgresql://user:pass@localhost/golett",
    qdrant_url="http://localhost:6333",
    postgres_base_table="golett_memories",
    qdrant_base_collection="golett_vectors",
    embedding_model="text-embedding-3-small",
    enable_normalized_layers=True
)
```

#### Session Management

```python
# Create a new session
session_id = memory_manager.create_session(
    metadata={
        "user_id": "user123",
        "session_type": "crew_enabled",
        "preferences": {...}
    },
    session_id=None  # Optional custom session ID
)

# Returns: str (session ID)
```

#### Message Operations

```python
# Store a message
message_id = memory_manager.store_message(
    session_id="session123",
    role="user",  # "user", "assistant", "system"
    content="Hello, how can you help me?",
    metadata={
        "timestamp": "2024-01-01T12:00:00Z",
        "importance": 0.5,
        "message_type": "query"
    },
    memory_layer=MemoryLayer.IN_SESSION  # Optional
)

# Search message history
messages = memory_manager.search_message_history(
    query="help with data analysis",
    session_id="session123",  # Optional
    limit=10,
    semantic=True,
    include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
)

# Returns: List[Dict[str, Any]]
```

#### Context Operations

```python
# Store context
context_id = memory_manager.store_context(
    session_id="session123",
    context_type="knowledge",  # "knowledge", "bi_data", "decision", etc.
    data={
        "content": "Important business insight",
        "source": "analysis_report.pdf",
        "confidence": 0.9
    },
    importance=0.8,
    metadata={
        "category": "business_intelligence",
        "tags": ["analysis", "report"]
    },
    memory_layer=MemoryLayer.LONG_TERM
)

# Retrieve context
contexts = memory_manager.retrieve_context(
    session_id="session123",
    query="business insights",
    context_types=["knowledge", "bi_data"],
    limit=5,
    include_layers=[MemoryLayer.LONG_TERM],
    cross_session=True
)

# Returns: List[Dict[str, Any]]
```

#### BI Data Operations

```python
# Store BI data
bi_id = memory_manager.store_bi_data(
    session_id="session123",
    data_type="query_result",
    data={
        "query": "SELECT * FROM sales WHERE date > '2024-01-01'",
        "results": [...],
        "row_count": 1500
    },
    description="Q1 2024 sales data analysis",
    importance=0.9,
    metadata={
        "database": "sales_db",
        "execution_time": 2.3
    }
)

# Retrieve BI data
bi_data = memory_manager.retrieve_bi_data(
    session_id="session123",
    query="sales data Q1 2024",
    data_types=["query_result", "analysis"],
    limit=5,
    cross_session=True
)
```

#### Decision Tracking

```python
# Store decision
decision_id = memory_manager.store_decision(
    session_id="session123",
    decision_type="use_data",
    description="Use sales data for trend analysis",
    reasoning="User requested quarterly sales trends, sales data is most relevant",
    metadata={
        "confidence": 0.85,
        "alternatives": ["use_forecast_data", "use_historical_data"]
    }
)

# Get recent decisions
decisions = memory_manager.get_recent_decisions(
    session_id="session123",
    decision_type="use_data",  # Optional
    limit=10
)
```

#### Layer Management

```python
# Get layer statistics
stats = memory_manager.get_layer_statistics()
# Returns: Dict[str, Dict[str, Any]]

# Cleanup expired memories
cleanup_report = memory_manager.cleanup_expired_memories(
    layer=MemoryLayer.IN_SESSION,  # Optional, defaults to all layers
    dry_run=False
)

# Search across all layers
results = memory_manager.search_across_all_layers(
    query="important business decisions",
    session_id="session123",
    limit=20,
    include_layer_weights=True
)
```

---

## Knowledge Management APIs

### GolettKnowledgeAdapter

**Location**: `golett.chat.GolettKnowledgeAdapter`

#### Initialization

```python
from golett.chat import GolettKnowledgeAdapter
from golett.memory import MemoryLayer

knowledge_adapter = GolettKnowledgeAdapter(
    memory_manager=memory_manager,
    session_id="session123",
    enable_advanced_features=True,
    default_memory_layer=MemoryLayer.LONG_TERM,
    cross_session_access=True,
    max_knowledge_age_days=30
)
```

#### Knowledge Sources

```python
# Add advanced file source
file_source = knowledge_adapter.add_advanced_file_source(
    file_path="documents/company_handbook.txt",
    collection_name="company_docs",
    memory_layer=MemoryLayer.LONG_TERM,
    tags=["handbook", "policies", "procedures"],
    importance=0.9,
    chunk_size=1000,
    overlap_size=100,
    enable_versioning=True
)

# Add advanced memory source
memory_source = knowledge_adapter.add_advanced_memory_source(
    collection_names=["company_docs", "technical_docs"],
    memory_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
    context_types=["knowledge", "decision"],
    tags=["documentation"],
    importance_threshold=0.5,
    cross_session=True,
    max_age_days=60
)
```

#### Knowledge Retrieval

```python
from golett.knowledge import KnowledgeRetrievalStrategy

# Retrieve knowledge
results = knowledge_adapter.retrieve_knowledge(
    query="company vacation policy",
    limit=10,
    strategy=KnowledgeRetrievalStrategy.HYBRID,
    include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
    crewai_limit=5,
    golett_limit=5,
    memory_limit=3
)

# Search across layers
layer_results = knowledge_adapter.search_across_layers(
    query="technical documentation",
    limit=15,
    include_layer_weights=True
)
```

#### Collection Management

```python
# List collections
collections = knowledge_adapter.list_collections()
# Returns: Dict[str, Dict[str, Any]]

# Get collection info
collection_info = knowledge_adapter.get_collection_info("company_docs")
# Returns: Optional[Dict[str, Any]]

# Get memory layer statistics
layer_stats = knowledge_adapter.get_memory_layer_stats()

# Optimize memory layers
optimization_report = knowledge_adapter.optimize_memory_layers()
```

### Knowledge Sources

#### GolettAdvancedTextFileKnowledgeSource

```python
from golett.knowledge import GolettAdvancedTextFileKnowledgeSource, KnowledgeRetrievalStrategy

source = GolettAdvancedTextFileKnowledgeSource(
    file_path="documents/manual.pdf",
    memory_manager=memory_manager,
    session_id="session123",
    collection_name="manuals",
    memory_layer=MemoryLayer.LONG_TERM,
    tags=["manual", "instructions"],
    importance=0.8,
    chunk_size=1000,
    overlap_size=100,
    enable_versioning=True
)

# Retrieve from source
results = source.retrieve(
    query="installation instructions",
    limit=5,
    strategy=KnowledgeRetrievalStrategy.SEMANTIC
)

# Paginated retrieval
results, pagination_info = source.paginate_retrieve(
    query="configuration settings",
    page=1,
    page_size=10,
    strategy=KnowledgeRetrievalStrategy.HYBRID
)
```

#### GolettAdvancedMemoryKnowledgeSource

```python
from golett.knowledge import GolettAdvancedMemoryKnowledgeSource

memory_source = GolettAdvancedMemoryKnowledgeSource(
    memory_manager=memory_manager,
    session_id="session123",
    collection_names=["docs", "knowledge"],
    memory_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
    context_types=["knowledge", "bi_data"],
    tags=["important"],
    importance_threshold=0.5,
    cross_session=True,
    max_age_days=30
)

# Retrieve from memory
results = memory_source.retrieve(
    query="recent analysis results",
    limit=10,
    strategy=KnowledgeRetrievalStrategy.TEMPORAL,
    boost_current_session=True
)
```

---

## Session Management APIs

### SessionManager

**Location**: `golett.memory.SessionManager`

#### Initialization

```python
from golett.memory import SessionManager

session_manager = SessionManager(memory_manager)
```

#### Session Lifecycle

```python
# Create session
session_id = session_manager.create_session(
    user_id="user123",
    metadata={
        "user_preferences": {
            "language": "en",
            "timezone": "UTC"
        },
        "session_type": "crew_enabled"
    }
)

# Get session info
session_info = session_manager.get_session_info("session123")
# Returns: Optional[Dict[str, Any]]

# Close session
success = session_manager.close_session("session123")
# Returns: bool
```

#### Session Preferences

```python
# Store preferences
success = session_manager.store_session_preferences(
    session_id="session123",
    preferences={
        "response_style": "detailed",
        "preferred_sources": ["company_docs", "technical_docs"],
        "auto_summarize": True
    }
)

# Get preferences
preferences = session_manager.get_session_preferences("session123")
# Returns: Dict[str, Any]
```

#### Crew Management

```python
# Register crew with session
success = session_manager.register_crew_with_session(
    session_id="session123",
    crew_id="bi_analysis",
    crew_config={
        "max_iterations": 3,
        "timeout": 300,
        "verbose": True
    }
)

# Update crew task count
session_manager.update_crew_task_count("session123", "bi_analysis")
```

#### Session Analytics

```python
# Get active sessions
active_sessions = session_manager.get_active_sessions(limit=20)
# Returns: List[Dict[str, Any]]

# Get session statistics
stats = session_manager.get_session_statistics()
# Returns: Dict[str, Any]
```

---

## Chat Flow APIs

### CrewChatSession

**Location**: `golett.chat.CrewChatSession`

#### Initialization

```python
from golett.chat import CrewChatSession

session = CrewChatSession(
    session_id="session123",
    memory_manager=memory_manager,
    enable_knowledge=True,
    auto_summarize=True,
    max_message_history=100
)
```

#### Message Operations

```python
# Add user message
session.add_user_message("What are our Q1 sales figures?")

# Add assistant message
session.add_assistant_message("Based on the data, Q1 sales were $2.5M...")

# Get message history
history = session.get_message_history(limit=20)
# Returns: List[Dict[str, Any]]
```

#### Crew Management

```python
# Create crew
crew = session.create_crew(
    crew_id="sales_analysis",
    crew_name="Sales Analysis Team",
    agents=[sales_analyst, data_scientist],
    process="sequential"
)

# Execute crew task
result = session.execute_crew_task(
    crew_id="sales_analysis",
    task_description="Analyze Q1 sales performance and identify trends"
)

# Get crew
crew = session.get_crew("sales_analysis")
```

#### Knowledge Integration

```python
# Add knowledge source
session.add_knowledge_source(knowledge_source)

# Check if knowledge is available
has_knowledge = session.has_knowledge
```

### CrewChatFlowManager

**Location**: `golett.chat.CrewChatFlowManager`

#### Initialization

```python
from golett.chat import CrewChatFlowManager

flow_manager = CrewChatFlowManager(
    session=crew_session,
    llm_provider="openai",
    llm_model="gpt-4o",
    temperature=0.7,
    use_crew_for_complex=True,
    auto_summarize=True,
    messages_per_summary=10
)
```

#### Message Processing

```python
# Process user message
response = flow_manager.process_user_message(
    "Can you analyze our customer satisfaction trends?"
)
# Returns: str (assistant response)
```

---

## Agent Coordination APIs

### Agent Creation

```python
from crewai import Agent

# Create specialized agents
bi_analyst = Agent(
    role="Business Intelligence Analyst",
    goal="Extract insights from business data",
    backstory="Expert in data analysis and business intelligence",
    tools=[data_query_tool, visualization_tool],
    llm=llm_instance
)

knowledge_expert = Agent(
    role="Knowledge Expert",
    goal="Retrieve and analyze domain knowledge",
    backstory="Specialist in information retrieval and knowledge management",
    tools=[knowledge_search_tool, document_analyzer],
    llm=llm_instance
)
```

### Crew Configuration

```python
from crewai import Crew, Task

# Create tasks
analysis_task = Task(
    description="Analyze the provided data and identify key trends",
    agent=bi_analyst,
    expected_output="Detailed analysis report with visualizations"
)

knowledge_task = Task(
    description="Find relevant documentation and best practices",
    agent=knowledge_expert,
    expected_output="Curated list of relevant knowledge sources"
)

# Create crew
analysis_crew = Crew(
    agents=[bi_analyst, knowledge_expert],
    tasks=[analysis_task, knowledge_task],
    process="sequential",
    verbose=True
)
```

---

## Storage APIs

### PostgreSQL Storage

**Location**: `golett.memory.storage.PostgresMemoryStorage`

```python
from golett.memory.storage import PostgresMemoryStorage

postgres_storage = PostgresMemoryStorage(
    connection_string="postgresql://user:pass@localhost/golett",
    table_name="golett_memories_long_term"
)

# Save data
postgres_storage.save(
    key="context_123",
    data={"content": "Important information"},
    metadata={"type": "knowledge", "importance": 0.8}
)

# Load data
data = postgres_storage.load("context_123")

# Search data
results = postgres_storage.search(
    query={"metadata.type": "knowledge"},
    limit=10
)

# Delete data
postgres_storage.delete("context_123")

# Reset storage
postgres_storage.reset()
```

### Qdrant Storage

**Location**: `golett.memory.storage.QdrantMemoryStorage`

```python
from golett.memory.storage import QdrantMemoryStorage

qdrant_storage = QdrantMemoryStorage(
    collection_name="golett_vectors_long_term",
    url="http://localhost:6333",
    embedder_name="text-embedding-3-small"
)

# Save with embedding
qdrant_storage.save(
    key="vector_123",
    data="This is important content to be embedded",
    metadata={"type": "knowledge", "source": "document.pdf"}
)

# Search by similarity
results = qdrant_storage.search(
    query="important content",
    limit=5,
    score_threshold=0.7
)
```

---

## RESTful Web APIs

### Session Endpoints

```http
# Create session
POST /api/v1/sessions
Content-Type: application/json

{
    "user_id": "user123",
    "metadata": {
        "preferences": {...},
        "session_type": "crew_enabled"
    }
}

# Response
{
    "session_id": "session_abc123",
    "status": "active",
    "created_at": "2024-01-01T12:00:00Z"
}

# Get session info
GET /api/v1/sessions/{session_id}

# Close session
DELETE /api/v1/sessions/{session_id}
```

### Chat Endpoints

```http
# Send message
POST /api/v1/sessions/{session_id}/messages
Content-Type: application/json

{
    "message": "What are our Q1 sales figures?",
    "use_crew": true,
    "context": {...}
}

# Response
{
    "response": "Based on the analysis...",
    "message_id": "msg_123",
    "crew_used": "bi_analysis",
    "context_retrieved": 5
}

# Get message history
GET /api/v1/sessions/{session_id}/messages?limit=20&offset=0
```

### Knowledge Endpoints

```http
# Add knowledge source
POST /api/v1/knowledge/sources
Content-Type: application/json

{
    "type": "file",
    "file_path": "/path/to/document.pdf",
    "collection_name": "company_docs",
    "metadata": {...}
}

# Search knowledge
POST /api/v1/knowledge/search
Content-Type: application/json

{
    "query": "company policies",
    "limit": 10,
    "strategy": "hybrid",
    "collections": ["company_docs"]
}

# List collections
GET /api/v1/knowledge/collections
```

### Memory Endpoints

```http
# Get layer statistics
GET /api/v1/memory/layers

# Trigger cleanup
POST /api/v1/memory/cleanup
Content-Type: application/json

{
    "layer": "in_session",
    "dry_run": false
}

# Cross-layer search
POST /api/v1/memory/search
Content-Type: application/json

{
    "query": "important decisions",
    "session_id": "session123",
    "limit": 20,
    "include_layers": ["long_term", "short_term"]
}
```

---

## WebSocket APIs

### Real-time Chat

```javascript
// Connect to chat WebSocket
const chatSocket = new WebSocket('ws://localhost:8000/api/v1/sessions/session123/chat');

// Send message
chatSocket.send(JSON.stringify({
    type: 'message',
    content: 'Hello, can you help me?',
    use_crew: true
}));

// Receive response
chatSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Response:', data.response);
    console.log('Crew used:', data.crew_used);
};
```

### Session Status

```javascript
// Connect to status WebSocket
const statusSocket = new WebSocket('ws://localhost:8000/api/v1/sessions/session123/status');

// Receive status updates
statusSocket.onmessage = function(event) {
    const status = JSON.parse(event.data);
    console.log('Session status:', status.type);
    console.log('Details:', status.details);
};
```

---

## Error Handling

### Exception Types

```python
from golett.exceptions import (
    GolettError,
    MemoryError,
    SessionError,
    KnowledgeError,
    CrewError
)

try:
    result = memory_manager.retrieve_context(...)
except MemoryError as e:
    print(f"Memory operation failed: {e}")
except SessionError as e:
    print(f"Session error: {e}")
except GolettError as e:
    print(f"General Golett error: {e}")
```

### HTTP Error Responses

```json
{
    "error": {
        "code": "MEMORY_LAYER_NOT_FOUND",
        "message": "The specified memory layer does not exist",
        "details": {
            "layer": "invalid_layer",
            "available_layers": ["long_term", "short_term", "in_session"]
        }
    },
    "request_id": "req_123456"
}
```

---

## Authentication

### API Key Authentication

```http
# Include API key in headers
Authorization: Bearer your_api_key_here
```

### Session Token Authentication

```http
# Include session token
X-Session-Token: session_token_here
```

### Python Client Authentication

```python
from golett.client import GolettClient

client = GolettClient(
    api_key="your_api_key",
    base_url="https://api.golett.ai"
)

# All subsequent calls will include authentication
session = client.create_session(...)
```

---

## Rate Limiting

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Response

```json
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded. Try again later.",
        "retry_after": 60
    }
}
```

---

*This API reference provides comprehensive documentation for all Golett AI interfaces. For implementation examples and tutorials, refer to the examples directory and technical documentation.* 