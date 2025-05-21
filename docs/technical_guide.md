# Golett Technical Documentation

## Overview

Golett is a modular, long-term conversational agent framework built on top of CrewAI with enhanced memory and business intelligence capabilities. It provides a robust system for creating persistent chat sessions with agents capable of analyzing complex queries, making decisions about data utilization, and responding appropriately through collaboration with specialized crews.

Key features include:
- Persistent memory architecture with both structured and vector storage
- Modular conversational agent system with CrewAI integration
- Business intelligence capabilities via Cube.js
- Enhanced context management and session state persistence
- Automatic conversation summarization
- Specialized knowledge retrieval and integration

## Architecture

Golett's architecture consists of several layered components:

1. **Memory Layer**: Provides persistent storage for conversations, context and session data
2. **Agent Layer**: Manages the creation and execution of specialized agents and crews
3. **Chat Layer**: Handles conversation flow, decision-making, and response generation
4. **BI Layer**: Integrates with Cube.js for business intelligence capabilities
5. **Knowledge Layer**: Manages retrieval and integration of domain knowledge

## Core Components

### Memory System

Golett's memory system uses a dual-storage approach:

- **PostgreSQL**: For structured data storage (messages, session metadata, decisions)
- **Qdrant**: For vector-based semantic search (enabling similarity-based retrieval)

The memory system is managed by three primary components:

1. `MemoryManager`: Central coordinator for all memory operations
2. `ContextManager`: Specialized manager for contextual information
3. `SessionManager`: Handles session state, metadata, and lifecycle

### Chat System

The chat system handles conversation flow and user interactions:

1. `ChatSession`: Base class for managing conversation state
2. `CrewChatSession`: Enhanced session with CrewAI capabilities
3. `ChatFlowManager`: Manages conversation flow and decision-making
4. `CrewChatFlowManager`: Extended flow manager with crew orchestration

### Agent System

Golett leverages CrewAI for collaborative agent execution:

1. `BiQueryAgent`: Specialized agent for BI queries
2. Various CrewAI agents are created dynamically for specific tasks

### Knowledge Integration

Knowledge retrieval is handled through specialized components:

1. `GolettKnowledgeAdapter`: Bridges CrewAI's knowledge system with Golett's memory
2. CrewAI's knowledge sources (document, API, database)

## Setup and Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Qdrant vector database
- OpenAI API or compatible LLM provider
- (Optional) Cube.js server for BI capabilities

### Installation

```bash
pip install golett  # Coming soon to PyPI
```

Or from source:

```bash
git clone https://github.com/yourusername/golett.git
cd golett
pip install -e .
```

### Configuration

Set up environment variables:

```bash
# Required
export POSTGRES_CONNECTION="postgresql://user:password@localhost:5432/db_name"
export QDRANT_URL="http://localhost:6333"
export OPENAI_API_KEY="your-api-key"

# Optional
export CUBEJS_API_URL="http://localhost:4000/cubejs-api/v1"
export CUBEJS_API_TOKEN="your-cubejs-token"
export CUBEJS_SCHEMAS_PATH="path/to/schemas"
```

## Usage Guide

### Creating a Basic Chat Session

```python
from golett import MemoryManager, ChatSession, ChatFlowManager

# Initialize memory
memory = MemoryManager(
    postgres_connection="postgresql://user:password@localhost:5432/db_name",
    qdrant_url="http://localhost:6333"
)

# Create a chat session
session = ChatSession(
    memory_manager=memory,
    metadata={"user_id": "user123", "session_type": "standard"}
)

# Set up flow manager
flow = ChatFlowManager(
    session=session,
    llm_model="gpt-4o"
)

# Add a system message
session.add_system_message(
    "You are a helpful assistant that provides concise, accurate information."
)

# Process a user message
response = flow.process_user_message("Hello, can you help me understand how Golett works?")
print(f"Assistant: {response}")

# Close the session
session.close()
```

### Creating a Crew-Enabled Session

```python
from golett import (
    MemoryManager, 
    GolettKnowledgeAdapter,
    CrewChatSession, 
    CrewChatFlowManager
)
from crewai.knowledge.source import TextFileKnowledgeSource

# Initialize memory
memory = MemoryManager(
    postgres_connection="postgresql://user:password@localhost:5432/db_name",
    qdrant_url="http://localhost:6333"
)

# Set up knowledge adapter
knowledge_adapter = GolettKnowledgeAdapter(memory)

# Create knowledge sources
knowledge_sources = [
    TextFileKnowledgeSource(file_path="docs/knowledge_base.txt")
]

# Initialize knowledge
knowledge = knowledge_adapter.create_crew_knowledge(
    collection_name="product_knowledge",
    sources=knowledge_sources
)

# Create a crew-enabled session
session = CrewChatSession(
    memory_manager=memory,
    knowledge_adapter=knowledge_adapter,
    user_id="user123",
    metadata={
        "session_type": "crew_enabled",
        "preferences": {"auto_summarize": True}
    }
)

# Set up crew flow manager
flow = CrewChatFlowManager(
    session=session,
    llm_model="gpt-4o",
    use_crew_for_complex=True,
    auto_summarize=True
)

# Process a complex query
response = flow.process_user_message("Can you analyze our Q3 sales trends compared to last year?")
print(f"Assistant: {response}")

# Close the session
session.close()
```

### Working with Context and Session State

```python
from golett import MemoryManager
from golett.memory.contextual import ContextManager
from golett.memory.session import SessionManager

# Initialize managers
memory_mgr = MemoryManager(
    postgres_connection="postgresql://user:password@localhost:5432/db_name",
    qdrant_url="http://localhost:6333"
)
context_mgr = ContextManager(memory_mgr)
session_mgr = SessionManager(memory_mgr)

# Create a session
session_id = session_mgr.create_session(
    user_id="user123",
    session_type="knowledge_base",
    preferences={"theme": "dark", "notification": True}
)

# Store knowledge context
context_mgr.store_knowledge_context(
    session_id=session_id,
    content="Golett is a framework for creating conversational agents with persistent memory.",
    source="documentation",
    description="Framework description",
    tags=["overview", "introduction"]
)

# Update session state
session_mgr.update_session_state(
    session_id=session_id,
    state={"current_module": "product_catalog"}
)

# Retrieve session information
session_info = session_mgr.get_session_info(session_id)
print(f"Session state: {session_info['state']}")
print(f"User preferences: {session_info['metadata']['preferences']}")

# Close the session
session_mgr.close_session(session_id)
```

## Memory System Details

### MemoryManager

The `MemoryManager` is the central component for all memory operations, providing unified access to both structured and vector storage.

Key methods:
- `create_session(metadata)`: Create a new chat session
- `store_message(session_id, role, content, metadata)`: Store a message in the session
- `get_session_history(session_id, limit)`: Get message history for a session
- `search_message_history(query, session_id, limit, semantic)`: Search through messages
- `store_context(session_id, context_type, data, importance, metadata)`: Store contextual information
- `retrieve_context(session_id, query, context_types, limit)`: Retrieve relevant context
- `store_decision(session_id, decision_type, description, reasoning)`: Store an agent's decision
- `get_recent_decisions(session_id, decision_type, limit)`: Get recent decisions

### ContextManager

The `ContextManager` provides specialized methods for storing and retrieving different types of contextual information.

Key methods:
- `store_knowledge_context(session_id, content, source, description, tags, metadata)`: Store knowledge
- `store_crew_context(session_id, crew_id, context_type, data, importance, metadata)`: Store crew-specific context
- `retrieve_knowledge_for_query(session_id, query, tags, sources, limit)`: Retrieve knowledge
- `retrieve_crew_context(session_id, crew_id, context_type, query, limit)`: Get crew context
- `store_conversation_summary(session_id, summary, start_time, end_time, topics)`: Store a summary
- `retrieve_conversation_summaries(session_id, topic, query, limit)`: Get summaries

### SessionManager

The `SessionManager` handles session lifecycle, state, and metadata.

Key methods:
- `create_session(user_id, session_type, preferences, metadata)`: Create a new session
- `get_session_info(session_id)`: Get comprehensive session information
- `update_session_state(session_id, state)`: Update session state
- `register_crew_with_session(session_id, crew_id, crew_name, agent_count, process_type)`: Register a crew
- `update_crew_task_count(session_id, crew_id, increment)`: Update task count
- `get_active_sessions(user_id, inactive_threshold_hours)`: Get active sessions
- `close_session(session_id)`: Close a session
- `store_session_preferences(session_id, preferences)`: Store user preferences
- `get_session_preferences(session_id)`: Get user preferences

## Chat System Details

### ChatSession

The `ChatSession` manages a conversation between a user and the agent system.

Key methods:
- `add_user_message(content, metadata)`: Add a user message
- `add_assistant_message(content, metadata)`: Add an assistant message
- `add_system_message(content, metadata)`: Add a system message
- `get_message_history(limit)`: Get message history
- `search_messages(query, semantic, limit)`: Search through messages
- `get_context_for_query(query, context_types, limit)`: Get context for a query
- `close()`: Close the session

### CrewChatSession

The `CrewChatSession` extends `ChatSession` with CrewAI capabilities.

Additional methods:
- `create_crew(crew_id, agents, tasks, process, verbose)`: Create a CrewAI crew
- `execute_crew_task(crew_id, task_description, inputs)`: Execute a task with a crew
- `get_crew(crew_id)`: Get a crew by ID
- `get_crew_results(crew_id, limit)`: Get previous crew results
- `store_conversation_summary(summary, topics, start_message_index, end_message_index)`: Store a summary

### ChatFlowManager

The `ChatFlowManager` orchestrates the conversation flow and decision-making process.

Key methods:
- `process_user_message(message)`: Process a user message
- `_analyze_data_needs(message)`: Analyze if the message needs BI data
- `_determine_response_mode(message, should_use_data)`: Determine response mode
- `_generate_response(message, should_use_data, response_mode)`: Generate a response

### CrewChatFlowManager

The `CrewChatFlowManager` extends `ChatFlowManager` with crew orchestration.

Additional methods:
- `_initialize_crews()`: Initialize specialized crews
- `_analyze_complexity(message)`: Analyze if a message is complex
- `_process_with_crew(message)`: Process a message with a crew
- `_select_appropriate_crew(message)`: Select the appropriate crew
- `_create_enhanced_task(message, crew_id)`: Create an enhanced task
- `_create_conversation_summary()`: Create a conversation summary

## Business Intelligence Integration

### Cube.js Client

The `CubeJsClient` handles interaction with the Cube.js REST API.

Key methods:
- `load(query)`: Execute a query and load data
- `sql(query)`: Execute a SQL query
- `meta()`: Get metadata for available cubes
- `dry_run(query)`: Preview a query without executing it
- `build_query(measures, dimensions, filters, time_dimensions, limit, offset, order)`: Build a query

### BI Query Agent

The `BiQueryAgent` specializes in handling BI queries using Cube.js.

Key methods:
- `query(question)`: Execute a BI query based on a natural language question
- `analyze_trend(metric, time_period, dimensions)`: Analyze trends for a metric
- `compare_metrics(metrics, filters)`: Compare multiple metrics
- `generate_dashboard_data(dashboard_name, metrics)`: Generate dashboard data

## Knowledge Integration

### GolettKnowledgeAdapter

The `GolettKnowledgeAdapter` bridges CrewAI's knowledge system with Golett's memory.

Key methods:
- `create_crew_knowledge(collection_name, sources, embedder)`: Create a CrewAI knowledge object
- `retrieve_for_query(query, session_id, collection_name, crew_limit, memory_limit)`: Retrieve information

## Best Practices

1. **Memory Management**:
   - Close sessions when they're no longer needed
   - Use context types to organize different types of information
   - Set appropriate importance scores for context items

2. **Crew Management**:
   - Create specialized crews for different tasks
   - Use the appropriate process type (sequential, hierarchical)
   - Provide clear task descriptions with relevant context

3. **User Experience**:
   - Store user preferences in session metadata
   - Use conversation summaries to maintain context
   - Provide feedback on complex operations

4. **Performance**:
   - Limit the number of results returned from searches
   - Use semantic search only when necessary
   - Leverage structured queries for known patterns

## Advanced Topics

### Custom Crews

You can create custom crews for specialized tasks:

```python
from crewai import Agent, Task

# Create specialized agents
research_agent = Agent(
    name="Research Specialist",
    role="Market Research Expert",
    goal="Find and analyze market trends",
    backstory="You are an expert in analyzing market data and identifying trends.",
    llm_model="gpt-4o"
)

analytics_agent = Agent(
    name="Analytics Expert",
    role="Data Analytics Specialist",
    goal="Analyze data and extract insights",
    backstory="You excel at statistical analysis and insight generation.",
    llm_model="gpt-4o"
)

# Create a market analysis crew
market_crew = session.create_crew(
    crew_id="market_analysis",
    crew_name="Market Analysis Team",
    agents=[research_agent, analytics_agent],
    process="sequential"
)

# Execute a task
result = session.execute_crew_task(
    crew_id="market_analysis",
    task_description="Analyze emerging trends in renewable energy sector"
)
```

### Custom Knowledge Sources

You can create and integrate custom knowledge sources:

```python
from crewai.knowledge.source import BaseKnowledgeSource

class CustomAPIKnowledgeSource(BaseKnowledgeSource):
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        
    def load(self):
        # Implement loading data from API
        pass
        
    def add(self):
        # Implement adding to storage
        pass

# Create and use custom knowledge source
api_source = CustomAPIKnowledgeSource(
    api_url="https://api.example.com/knowledge",
    api_key="your-api-key"
)

knowledge = knowledge_adapter.create_crew_knowledge(
    collection_name="api_knowledge",
    sources=[api_source]
)
```

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Ensure PostgreSQL and Qdrant are running
   - Check connection strings and credentials
   - Verify network connectivity

2. **Memory Problems**:
   - Check for missing session IDs
   - Ensure context types are correct
   - Verify that metadata is properly formatted

3. **CrewAI Issues**:
   - Ensure proper agent roles and goals
   - Check for task clarity
   - Verify LLM availability

### Logging

Golett uses Python's logging system. Enable debug logging for more information:

```python
import logging
from golett.utils import setup_file_logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
setup_file_logging("golett.log", logging.DEBUG)
```

## API Reference

Please refer to the docstrings in each module for detailed API reference. Key modules include:

- `golett.memory.memory_manager`
- `golett.memory.contextual.context_manager`
- `golett.memory.session.session_manager`
- `golett.chat.session`
- `golett.chat.flow`
- `golett.chat.crew`
- `golett.chat.crew_session`
- `golett.chat.crew_flow`
- `golett.tools.cube.client`
- `golett.agents.bi.bi_agent`

## License

Golett is licensed under MIT License. See the LICENSE file for details.