# 🗿 Golett Gateway: Your BI Insights Portal

**Golett Gateway: Unearthing Insights with Your Autonomous BI Agent Crew!**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com/build) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![crewAI](https://img.shields.io/badge/powered_by-crewAI-blue)](https://github.com/joaomdmoura/crewAI)

Welcome, Data Trainer! **Golett Gateway** is your access point to a powerful system of **Agentic Business Intelligence (BI) Agents**. Built on the `crewAI` framework, this system allows you to pose business questions in plain language and receive insightful answers, all orchestrated by a dedicated crew of AI agents.

Think of each 'Golett' in your crew as a specialized data assistant: one might be a **Query Golett** digging into databases, another a **Processor Golett** sifting through the findings, and a **Reporter Golett** presenting clear insights. The Gateway is where you issue your 'research quests' and receive their distilled wisdom.

---

## ✨ Features

* **Natural Language Querying:** Ask complex business questions in everyday language.
* **Automated Data Retrieval:** Agents autonomously generate and execute queries (e.g., SQL, API calls) against your configured data sources.
* **Intelligent Data Processing:** Agents can clean, transform, aggregate, and analyze retrieved data.
* **Insight Generation & Summarization:** AI crews collaborate to synthesize findings into understandable reports, visualizations, or direct answers.
* **`crewAI` Powered Collaboration:** Leverages `crewAI` for robust teamwork between specialized BI agents (e.g., Query Agent, Analysis Agent, Reporting Agent).
* **Data Source Connectivity:** Designed to be adaptable to various data sources (databases, APIs, CSV files, etc.).
* **Extensible Agent Skills:** Easily equip your Golett agents with new tools and capabilities for diverse BI tasks.

---

## 🧱 System Overview

Golett Gateway orchestrates a flow for answering your BI questions:

1.  **User Question:** The "Trainer" poses a business question through the Gateway.
2.  **Agent Crew Activation:** A specialized `crewAI` team is activated.
    * **Understanding Agent:** Interprets the natural language question.
    * **Query Planning Agent:** Determines what data is needed and how to get it.
    * **Data Retrieval Agent (Query Golett):** Connects to data sources and executes queries.
    * **Data Processing Agent (Processor Golett):** Cleans, analyzes, and aggregates the data.
    * **Insight Formulation Agent (Reporter Golett):** Synthesizes the information into a coherent answer.
3.  **Data Interaction:** Agents interact with configured databases, APIs, or files.
4.  **Answer Delivery:** The Gateway presents the processed information and insights back to the user.

## Overview

Golett Gateway provides a system for managing persistent chat sessions with agents capable of analyzing BI-related queries, deciding on data utilization, and responding appropriately. It enhances CrewAI with:

- **Improved Memory Management**: Replace CrewAI's default memory storage with PostgreSQL for structured data and Qdrant for vector-based long-term and short-term memory management.
- **Contextual Awareness**: Maintain context across sessions, allowing agents to reference previous interactions and data points.
- **Specialized BI Capabilities**: Built-in support for business intelligence queries and data integration.

## Architecture

The system consists of several key components:

### Memory Management

- **PostgreSQL Storage**: Structured data storage for efficient retrieval of conversation history and metadata
- **Qdrant Storage**: Vector-based storage for semantic search and similarity retrieval
- **Memory Manager**: Unified API for managing both storage backends

### Chat Flow

- **Chat Session**: Manages conversation state and interfaces with memory
- **Chat Flow Manager**: Orchestrates the decision-making process between agents
- **BI Query Analyzer**: Specialized component for analyzing business intelligence queries

### Agents

The system uses specialized agents for different aspects of the conversation:

1. **Query Analyzer**: Determines if a query requires BI data
2. **Response Strategist**: Decides on the optimal response format
3. **Response Generator**: Creates the final response

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Qdrant server (local or cloud)
- OpenAI API key (or other supported LLM provider)

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Set the following environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
export POSTGRES_CONNECTION="postgresql://user:password@localhost:5432/dbname"
export QDRANT_URL="http://localhost:6333"
```

### Basic Usage

```python
from golett import MemoryManager, ChatSession, ChatFlowManager

# Initialize memory manager
memory = MemoryManager(
    postgres_connection="postgresql://user:password@localhost:5432/dbname",
    qdrant_url="http://localhost:6333"
)

# Create chat session
session = ChatSession(memory_manager=memory)

# Initialize chat flow manager
flow = ChatFlowManager(session=session)

# Process a user message
response = flow.process_user_message("Show me the sales data for Q1 2023")
print(response)
```

## Documentation

For detailed documentation, see the `docs/` directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
