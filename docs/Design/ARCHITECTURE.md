## Golett Gateway – Reference Architecture (CrewAI Edition)

> **Version:** 2024-07-29
> **Status:** DRAFT

---

### 1. Purpose
This document describes the lean, production-ready architecture for **Golett Gateway**, a modular framework for building and deploying agentic chat applications powered by **CrewAI**. The system is designed for extensibility, clear data lineage, and operational simplicity, enabling developers to build sophisticated, multi-agent conversational experiences.

The core of this architecture is the `golett_core` package, a self-contained library that handles session management, knowledge context, and crew execution. It is designed to be easily integrated into any backend framework (e.g., FastAPI, Flask) or used as a standalone service.

---

### 2. High-level diagram
```
              ┌────────────┐   
              │  Knowledge │
              │   Store    │
              │  (Qdrant)  │
              └─────▲──────┘
                    │
┌──────────────┐    │        ┌──────────────────────────┐
│  Backend API │◀───┼────────▶       golett_core         │
│  (FastAPI)   │    │        │  (CrewAI Framework)      │
└──────────────┘    │        │  • Session Manager       │
                    │        │  • Knowledge Handler     │
                    │        │  • Crew Executor         │
                    │        └─────────▲────────────────┘
                    │                  │
                    │                  │
              PostgreSQL             │
           (for session metadata)      │
                    │                  │
                    ▼                  │
           ┌──────────────────┐        │
           │  Session Store   │        │
           │    (Redis)       │        │
           └────────▲─────────┘        │
                    │                  │
                    ▼                  │
            ┌──────────────────┐       │
            │  Chat History    │◀──────┘
            │  (PostgreSQL)    │
            └──────────────────┘
```

---

### 3. Repository & package layout
A clean separation of concerns keeps development velocity high and ops cost low. The project is organised into a primary `golett_core` package, with Pydantic models used for clear data contracts.

```text
Golett-Gateway/
├── golett_core/        # Pure Python domain logic for the CrewAI framework
│   ├── __init__.py
│   ├── agent/          # Agent definitions and configurations
│   ├── crew/           # Crew definitions, tasks, and process orchestration
│   ├── memory/         # Long-term memory and knowledge handling
│   │   ├── __init__.py
│   │   ├── knowledge_base.py # Handles interaction with the vector store
│   │   └── search.py         # Search and retrieval logic
│   ├── schemas/        # SHARED, cross-layer Pydantic data contracts
│   │   ├── __init__.py
│   │   ├── chat.py     # e.g., ChatMessage, ChatResponse
│   │   └── session.py  # e.g., Session
│   ├── session/        # Chat session management
│   │   ├── __init__.py
│   │   ├── history.py      # Manages conversation history
│   │   └── manager.py      # Handles session lifecycle
│   ├── tools/          # Agent tools and utilities
│   └── utils/          # Common utilities and helpers
│
├── examples/           # Example implementations using golett_core
│   └── fast_api_app/   # An example of integrating golett_core with FastAPI
│
├── infra/              # Docker-compose, Helm charts, Terraform
├── tests/              # Pytest suites mirror the package tree
└── refined_docs/       # Refined design docs (this folder)

```

**Key guidelines**
1. **`golett_core` is Framework-Agnostic**: It contains zero web framework imports (e.g., FastAPI, Flask). This ensures it can be used as a library in any Python application.
2. **Pydantic for Data Contracts**: All data transfer objects (DTOs) are defined using Pydantic in `golett_core/schemas`. This provides clear, validated data structures throughout the application.
3. **Dependency Injection**: Dependencies like database connections or external services should be injected into `golett_core` services. This promotes loose coupling and high testability.
4. **Extensible by Default**: The architecture is designed to be extensible. New agents, crews, and tools can be added with minimal friction.

---

### 4. Core Components & Responsibilities

| Component | Responsibility | Key Technologies |
|---|---|---|
| **Session Manager** | Manages the lifecycle of chat sessions. Creates, retrieves, and updates session state. | PostgreSQL (for metadata), Redis (for caching) |
| **Chat History** | Persists the full conversation history for each session. | PostgreSQL |
| **Knowledge Handler** | Manages the knowledge base. Handles file uploads, document processing, embedding, and retrieval. | Qdrant, LangChain (for document processing) |
| **Crew Executor** | Executes CrewAI crews to process user requests. Manages the interaction between agents and tools. | CrewAI |
| **Agents** | Individual autonomous units that perform specific tasks. | CrewAI, LangChain Models |
| **Tools** | Functions and utilities that agents can use to perform actions (e.g., web search, database queries). | Custom Python functions, LangChain Tools |

---

### 5. Chat & Session Management

#### 5.1 Session Lifecycle
1. **Creation**: A new session is created when a user starts a new conversation. A unique `session_id` is generated and returned to the client. Session metadata is stored in PostgreSQL.
2. **State Management**: The `SessionManager` tracks the state of each session, including the current crew, active tasks, and conversation history.
3. **Termination**: Sessions can be explicitly closed by the user or automatically terminated after a period of inactivity.

#### 5.2 Chat Message Flow (Happy Path)
1. **Client sends a message**: The client sends a `POST /chat` request with `session_id` and the user's message.
2. **Session validation**: The `SessionManager` validates the `session_id`.
3. **Context retrieval**: The `KnowledgeHandler` retrieves relevant context from the knowledge base based on the user's message and conversation history.
4. **Crew execution**: The `CrewExecutor` assembles the necessary context and passes the request to the appropriate CrewAI crew.
5. **Agent collaboration**: Agents within the crew collaborate, using their tools to process the request and generate a response.
6. **Response generation**: The final response is returned from the crew.
7. **History update**: The user's message and the agent's response are saved to the chat history in PostgreSQL.
8. **Response to client**: The final response is sent back to the client.

---

### 6. Knowledge Handler

The `KnowledgeHandler` is responsible for providing the agents with relevant information to complete their tasks. This includes both long-term memory and context from user-provided files.

#### 6.1 File Upload and Processing
1. **File upload**: Users can upload files (e.g., PDF, TXT, DOCX) via a dedicated endpoint.
2. **Document parsing**: The uploaded file is parsed and split into smaller chunks of text.
3. **Embedding**: Each text chunk is converted into a vector embedding using a pre-trained language model.
4. **Storage**: The embeddings and the original text chunks are stored in a Qdrant collection, linked to the user's session or profile.

#### 6.2 Information Retrieval
1. **Query generation**: When an agent needs information, it formulates a query.
2. **Semantic search**: The `KnowledgeHandler` converts the query into an embedding and performs a semantic search against the Qdrant collection to find the most relevant text chunks.
3. **Context augmentation**: The retrieved text chunks are provided to the agent as context to help it generate a more informed response.

---

### 7. Dev & Deploy
* **Local**: Docker-compose spins up PostgreSQL, Qdrant, and Redis.
* **CI**: `pytest`, `mypy`, and `ruff` are run for all pushes.
* **Prod**: Kubernetes Helm charts are provided for easy deployment.

---

*End of document.* 