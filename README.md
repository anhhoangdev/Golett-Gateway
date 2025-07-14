# 🗿 Golett Gateway: Your BI Insights Portal

**Golett Gateway – "Chat-to-Card" Event-Driven BI Assistant**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com/build) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![crewAI](https://img.shields.io/badge/powered_by-crewAI-blue)](https://github.com/joaomdmoura/crewAI)

Welcome, Data Trainer! **Golett Gateway** is your access point to a powerful system of **Agentic Business Intelligence (BI) Agents**. Built on the `crewAI` framework, this system allows you to pose business questions in plain language and receive insightful answers, all orchestrated by a dedicated crew of AI agents.

Ask a question in natural language → Golett's agent crew generates SQL, spins up a Metabase card, and streams the link right back. Every chat turn publishes events to an in-process **EventBus** so maintenance (TTL pruning, summary promotion) happens instantly—no cron jobs.

---

## ✨ Features

* **Chat-to-Card:** Every chat session corresponds to a Metabase card; pin it to any dashboard with one click.
* **Instant Context Refresh:** Memory writes emit `MemoryWritten` events; the retrieval window rebuilds on the fly (Cursor-style).
* **AdaptiveScheduler (no cron):** EventBus wakes `TTLPruner`, `PromotionWorker`, etc., milliseconds after data changes.
* **Hierarchical Memory Rings:** In-session (1 h TTL) → short-term summaries (7 days) → long-term knowledge (no TTL).
* **crewAI Agent Collaboration:** SQLAgent → DataAgent → WriterAgent pipeline, fully customizable.
* **Pure-Python Core:** Framework-agnostic; bring FastAPI, Flask, or a CLI.

---

## 🧱 System Overview

High-level turn sequence:

1. **User** asks a question via HTTP/WS.
2. `GolettApp.chat()` saves the message and publishes `NewTurn`.
3. **IntentRouter → Orchestrator** spins up `SQLAgent` which generates SQL and calls **MetabaseDAO.create_card()**.
4. Card ID returned → `AgentProduced` event → response streamed back with the card URL.
5. Background workers triggered by `MemoryWritten` keep memory tidy without delaying the user.

## Overview

Golett Gateway provides a system for managing persistent chat sessions with agents capable of analyzing BI-related queries, deciding on data utilization, and responding appropriately. It enhances CrewAI with:

- **Improved Memory Management**: Replace CrewAI's default memory storage with PostgreSQL for structured data and Qdrant for vector-based long-term and short-term memory management.
- **Contextual Awareness**: Maintain context across sessions, allowing agents to reference previous interactions and data points.
- **Specialized BI Capabilities**: Built-in support for business intelligence queries and data integration.

## Architecture

### Architecture Snapshot (July 2025)

* **EventBus** – pub/sub fabric inside the same process (swap for Redis to scale).  
* **AdaptiveScheduler** – dispatches background workers on events.  
* **GolettMemoryCore** – unified memory API (rings, summariser, graph).  
* **SessionContext** – live retrieval window per chat.  
* **Agents:** SQLAgent → WriterAgent (default); plug more via `GolettBuilder.with_crews()`.

For diagrams see `docs/ARCHITECTURE_OVERVIEW.md` & `docs/RUNTIME_FLOW.md`.

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
