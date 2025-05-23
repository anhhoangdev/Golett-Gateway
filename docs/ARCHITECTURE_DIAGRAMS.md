# Golett AI - Architecture Diagrams

## Overview

This document provides visual representations of Golett AI's architecture, including system diagrams, data flow charts, and component relationships.

## Table of Contents

1. [High-Level System Architecture](#high-level-system-architecture)
2. [Memory Layer Architecture](#memory-layer-architecture)
3. [Knowledge Management Flow](#knowledge-management-flow)
4. [Agent Coordination Flow](#agent-coordination-flow)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Deployment Architecture](#deployment-architecture)
7. [Security Architecture](#security-architecture)
8. [Component Interaction Diagrams](#component-interaction-diagrams)

---

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Interface]
        API_CLIENT[API Client]
        MOBILE[Mobile App]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx Load Balancer]
        AUTH[Authentication Service]
        RATE_LIMIT[Rate Limiting]
    end
    
    subgraph "Golett AI Core"
        API[Golett API Server]
        CHAT_FLOW[Chat Flow Manager]
        CREW_FLOW[Crew Chat Flow Manager]
        SESSION_MGR[Session Manager]
    end
    
    subgraph "Memory System"
        MEMORY_MGR[Memory Manager]
        CONTEXT_MGR[Context Manager]
        LAYER_MGR[Layer Manager]
    end
    
    subgraph "Knowledge System"
        KNOWLEDGE_ADAPTER[Knowledge Adapter]
        FILE_SOURCES[File Sources]
        MEMORY_SOURCES[Memory Sources]
    end
    
    subgraph "Agent System"
        CREW_AI[CrewAI Integration]
        BI_CREW[BI Analysis Crew]
        KNOWLEDGE_CREW[Knowledge Crew]
        SUMMARY_CREW[Summary Crew]
    end
    
    subgraph "Storage Layer"
        POSTGRES[(PostgreSQL)]
        QDRANT[(Qdrant Vector DB)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API]
        EMBEDDING[Embedding Service]
    end
    
    WEB --> NGINX
    API_CLIENT --> NGINX
    MOBILE --> NGINX
    
    NGINX --> AUTH
    AUTH --> RATE_LIMIT
    RATE_LIMIT --> API
    
    API --> CHAT_FLOW
    API --> CREW_FLOW
    API --> SESSION_MGR
    
    CHAT_FLOW --> MEMORY_MGR
    CREW_FLOW --> MEMORY_MGR
    CREW_FLOW --> KNOWLEDGE_ADAPTER
    CREW_FLOW --> CREW_AI
    
    MEMORY_MGR --> CONTEXT_MGR
    MEMORY_MGR --> LAYER_MGR
    
    KNOWLEDGE_ADAPTER --> FILE_SOURCES
    KNOWLEDGE_ADAPTER --> MEMORY_SOURCES
    
    CREW_AI --> BI_CREW
    CREW_AI --> KNOWLEDGE_CREW
    CREW_AI --> SUMMARY_CREW
    
    MEMORY_MGR --> POSTGRES
    MEMORY_MGR --> QDRANT
    SESSION_MGR --> REDIS
    
    CREW_AI --> OPENAI
    MEMORY_MGR --> EMBEDDING
```

---

## Memory Layer Architecture

```mermaid
graph TB
    subgraph "Memory Layer Architecture"
        subgraph "Application Layer"
            APP[Application Code]
            MEMORY_MGR[Memory Manager]
            CONTEXT_MGR[Context Manager]
        end
        
        subgraph "Layer Determination"
            LAYER_LOGIC[Layer Logic]
            IMPORTANCE[Importance Scoring]
            RETENTION[Retention Policies]
        end
        
        subgraph "Long-Term Memory"
            LT_POSTGRES[(PostgreSQL Long-Term)]
            LT_QDRANT[(Qdrant Long-Term)]
            LT_CONFIG[Retention: 365 days<br/>Importance: ≥0.7<br/>Cross-session: Yes]
        end
        
        subgraph "Short-Term Memory"
            ST_POSTGRES[(PostgreSQL Short-Term)]
            ST_QDRANT[(Qdrant Short-Term)]
            ST_CONFIG[Retention: 30 days<br/>Importance: ≥0.5<br/>Cross-session: No]
        end
        
        subgraph "In-Session Memory"
            IS_POSTGRES[(PostgreSQL In-Session)]
            IS_QDRANT[(Qdrant In-Session)]
            IS_CONFIG[Retention: 1 day<br/>Importance: ≥0.3<br/>Cross-session: No]
        end
        
        subgraph "Cross-Layer Operations"
            SEARCH[Cross-Layer Search]
            CLEANUP[Automated Cleanup]
            MIGRATION[Layer Migration]
        end
    end
    
    APP --> MEMORY_MGR
    MEMORY_MGR --> CONTEXT_MGR
    MEMORY_MGR --> LAYER_LOGIC
    
    LAYER_LOGIC --> IMPORTANCE
    LAYER_LOGIC --> RETENTION
    
    LAYER_LOGIC --> LT_POSTGRES
    LAYER_LOGIC --> LT_QDRANT
    LAYER_LOGIC --> ST_POSTGRES
    LAYER_LOGIC --> ST_QDRANT
    LAYER_LOGIC --> IS_POSTGRES
    LAYER_LOGIC --> IS_QDRANT
    
    MEMORY_MGR --> SEARCH
    MEMORY_MGR --> CLEANUP
    MEMORY_MGR --> MIGRATION
    
    SEARCH --> LT_QDRANT
    SEARCH --> ST_QDRANT
    SEARCH --> IS_QDRANT
```

### Layer Key Generation Strategy

```mermaid
graph LR
    subgraph "Key Generation Flow"
        INPUT[Base Key + Session ID + Layer]
        
        subgraph "Layer-Specific Logic"
            LT_KEY[Long-Term: lt:base_key]
            ST_KEY[Short-Term: st:session_id:base_key]
            IS_KEY[In-Session: is:session_id:timestamp:base_key]
        end
        
        OUTPUT[Final Storage Key]
    end
    
    INPUT --> LT_KEY
    INPUT --> ST_KEY
    INPUT --> IS_KEY
    
    LT_KEY --> OUTPUT
    ST_KEY --> OUTPUT
    IS_KEY --> OUTPUT
```

---

## Knowledge Management Flow

```mermaid
graph TB
    subgraph "Knowledge Input Sources"
        FILES[Text Files]
        DOCS[Documents]
        MEMORY[Memory Context]
        EXTERNAL[External APIs]
    end
    
    subgraph "Knowledge Processing"
        CHUNKING[Text Chunking]
        EMBEDDING[Embedding Generation]
        METADATA[Metadata Extraction]
        VERSIONING[Version Control]
    end
    
    subgraph "Knowledge Storage"
        COLLECTIONS[Collection Management]
        INDEXING[Vector Indexing]
        TAGGING[Tag Management]
    end
    
    subgraph "Knowledge Retrieval"
        SEMANTIC[Semantic Search]
        STRUCTURED[Structured Query]
        HYBRID[Hybrid Search]
        RANKING[Result Ranking]
    end
    
    subgraph "Knowledge Adapter"
        ADAPTER[Golett Knowledge Adapter]
        CREWAI_SOURCES[CrewAI Sources]
        GOLETT_SOURCES[Golett Sources]
        MEMORY_SOURCES[Memory Sources]
    end
    
    FILES --> CHUNKING
    DOCS --> CHUNKING
    MEMORY --> METADATA
    EXTERNAL --> EMBEDDING
    
    CHUNKING --> EMBEDDING
    EMBEDDING --> METADATA
    METADATA --> VERSIONING
    
    VERSIONING --> COLLECTIONS
    COLLECTIONS --> INDEXING
    INDEXING --> TAGGING
    
    TAGGING --> SEMANTIC
    TAGGING --> STRUCTURED
    TAGGING --> HYBRID
    
    SEMANTIC --> RANKING
    STRUCTURED --> RANKING
    HYBRID --> RANKING
    
    RANKING --> ADAPTER
    ADAPTER --> CREWAI_SOURCES
    ADAPTER --> GOLETT_SOURCES
    ADAPTER --> MEMORY_SOURCES
```

### Knowledge Retrieval Strategies

```mermaid
graph LR
    subgraph "Retrieval Strategy Selection"
        QUERY[User Query]
        ANALYSIS[Query Analysis]
        
        subgraph "Strategy Types"
            SEMANTIC[Semantic Search<br/>Vector Similarity]
            STRUCTURED[Structured Search<br/>Metadata Filtering]
            HYBRID[Hybrid Search<br/>Combined Approach]
            TEMPORAL[Temporal Search<br/>Time-based Relevance]
            IMPORTANCE[Importance Search<br/>Score-based Ranking]
        end
        
        RESULT[Ranked Results]
    end
    
    QUERY --> ANALYSIS
    ANALYSIS --> SEMANTIC
    ANALYSIS --> STRUCTURED
    ANALYSIS --> HYBRID
    ANALYSIS --> TEMPORAL
    ANALYSIS --> IMPORTANCE
    
    SEMANTIC --> RESULT
    STRUCTURED --> RESULT
    HYBRID --> RESULT
    TEMPORAL --> RESULT
    IMPORTANCE --> RESULT
```

---

## Agent Coordination Flow

```mermaid
graph TB
    subgraph "User Interaction"
        USER[User Message]
        COMPLEXITY[Complexity Analysis]
        ROUTING[Routing Decision]
    end
    
    subgraph "Simple Processing"
        SIMPLE_FLOW[Simple Chat Flow]
        DIRECT_RESPONSE[Direct Response]
    end
    
    subgraph "Complex Processing"
        CREW_FLOW[Crew Chat Flow]
        CONTEXT_ENHANCEMENT[Context Enhancement]
        CREW_SELECTION[Crew Selection]
    end
    
    subgraph "Specialized Crews"
        BI_CREW[BI Analysis Crew]
        KNOWLEDGE_CREW[Knowledge Crew]
        SUMMARY_CREW[Summary Crew]
    end
    
    subgraph "Crew Execution"
        TASK_CREATION[Enhanced Task Creation]
        AGENT_COORDINATION[Agent Coordination]
        RESULT_PROCESSING[Result Processing]
    end
    
    subgraph "Response Generation"
        FORMATTING[Response Formatting]
        CONTEXT_STORAGE[Context Storage]
        FINAL_RESPONSE[Final Response]
    end
    
    USER --> COMPLEXITY
    COMPLEXITY --> ROUTING
    
    ROUTING --> SIMPLE_FLOW
    ROUTING --> CREW_FLOW
    
    SIMPLE_FLOW --> DIRECT_RESPONSE
    
    CREW_FLOW --> CONTEXT_ENHANCEMENT
    CONTEXT_ENHANCEMENT --> CREW_SELECTION
    
    CREW_SELECTION --> BI_CREW
    CREW_SELECTION --> KNOWLEDGE_CREW
    CREW_SELECTION --> SUMMARY_CREW
    
    BI_CREW --> TASK_CREATION
    KNOWLEDGE_CREW --> TASK_CREATION
    SUMMARY_CREW --> TASK_CREATION
    
    TASK_CREATION --> AGENT_COORDINATION
    AGENT_COORDINATION --> RESULT_PROCESSING
    
    RESULT_PROCESSING --> FORMATTING
    DIRECT_RESPONSE --> FORMATTING
    
    FORMATTING --> CONTEXT_STORAGE
    CONTEXT_STORAGE --> FINAL_RESPONSE
```

### Crew Specialization Matrix

```mermaid
graph TB
    subgraph "Crew Specialization"
        subgraph "BI Analysis Crew"
            BI_ANALYST[BI Analyst<br/>Data Analysis & Insights]
            DATA_SCIENTIST[Data Scientist<br/>Statistical Analysis]
            BI_TOOLS[Tools: Query, Visualization]
        end
        
        subgraph "Knowledge Crew"
            KNOWLEDGE_EXPERT[Knowledge Expert<br/>Domain Knowledge]
            CONTEXT_ANALYST[Context Analyst<br/>Conversation Analysis]
            KNOWLEDGE_TOOLS[Tools: Search, Document Analysis]
        end
        
        subgraph "Summary Crew"
            SUMMARIZER[Conversation Summarizer<br/>Content Summarization]
            TOPIC_EXTRACTOR[Topic Extractor<br/>Topic Identification]
            SUMMARY_TOOLS[Tools: NLP, Classification]
        end
    end
    
    subgraph "Use Cases"
        BI_QUERIES[Business Intelligence Queries]
        KNOWLEDGE_QUERIES[Knowledge-Intensive Queries]
        SUMMARIZATION[Conversation Summarization]
    end
    
    BI_QUERIES --> BI_ANALYST
    BI_QUERIES --> DATA_SCIENTIST
    
    KNOWLEDGE_QUERIES --> KNOWLEDGE_EXPERT
    KNOWLEDGE_QUERIES --> CONTEXT_ANALYST
    
    SUMMARIZATION --> SUMMARIZER
    SUMMARIZATION --> TOPIC_EXTRACTOR
```

---

## Data Flow Diagrams

### Message Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant ChatFlow
    participant MemoryMgr
    participant CrewAI
    participant Storage
    
    User->>API: Send Message
    API->>ChatFlow: Process Message
    ChatFlow->>MemoryMgr: Store User Message
    MemoryMgr->>Storage: Save to Appropriate Layer
    
    ChatFlow->>ChatFlow: Analyze Complexity
    
    alt Simple Query
        ChatFlow->>MemoryMgr: Retrieve Context
        MemoryMgr->>Storage: Search Relevant Data
        Storage-->>MemoryMgr: Return Results
        MemoryMgr-->>ChatFlow: Context Data
        ChatFlow->>ChatFlow: Generate Response
    else Complex Query
        ChatFlow->>CrewAI: Create Enhanced Task
        CrewAI->>CrewAI: Execute Crew
        CrewAI-->>ChatFlow: Crew Results
        ChatFlow->>MemoryMgr: Store Crew Results
    end
    
    ChatFlow->>MemoryMgr: Store Assistant Response
    MemoryMgr->>Storage: Save Response
    ChatFlow-->>API: Final Response
    API-->>User: Return Response
```

### Knowledge Retrieval Flow

```mermaid
sequenceDiagram
    participant Query
    participant KnowledgeAdapter
    participant FileSource
    participant MemorySource
    participant VectorDB
    participant Results
    
    Query->>KnowledgeAdapter: Search Request
    KnowledgeAdapter->>KnowledgeAdapter: Determine Strategy
    
    par File Sources
        KnowledgeAdapter->>FileSource: Search Files
        FileSource->>VectorDB: Vector Search
        VectorDB-->>FileSource: File Results
        FileSource-->>KnowledgeAdapter: Ranked Results
    and Memory Sources
        KnowledgeAdapter->>MemorySource: Search Memory
        MemorySource->>VectorDB: Cross-Layer Search
        VectorDB-->>MemorySource: Memory Results
        MemorySource-->>KnowledgeAdapter: Context Results
    end
    
    KnowledgeAdapter->>KnowledgeAdapter: Merge & Rank Results
    KnowledgeAdapter-->>Results: Final Results
```

### Memory Layer Migration Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant MemoryMgr
    participant LayerLogic
    participant LongTerm
    participant ShortTerm
    participant InSession
    
    Scheduler->>MemoryMgr: Trigger Cleanup
    MemoryMgr->>LayerLogic: Analyze Content
    
    LayerLogic->>InSession: Check Expired Content
    InSession-->>LayerLogic: Expired Items
    
    loop For Each Expired Item
        LayerLogic->>LayerLogic: Evaluate Importance
        
        alt High Importance
            LayerLogic->>LongTerm: Migrate to Long-Term
        else Medium Importance
            LayerLogic->>ShortTerm: Migrate to Short-Term
        else Low Importance
            LayerLogic->>LayerLogic: Mark for Deletion
        end
    end
    
    LayerLogic->>MemoryMgr: Cleanup Report
    MemoryMgr-->>Scheduler: Completion Status
```

---

## Deployment Architecture

### Container Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end
    
    subgraph "Application Tier"
        API1[Golett API Instance 1]
        API2[Golett API Instance 2]
        API3[Golett API Instance 3]
    end
    
    subgraph "Database Tier"
        POSTGRES_PRIMARY[(PostgreSQL Primary)]
        POSTGRES_REPLICA[(PostgreSQL Replica)]
        QDRANT_CLUSTER[(Qdrant Cluster)]
        REDIS_CLUSTER[(Redis Cluster)]
    end
    
    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        LOGS[Log Aggregation]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> POSTGRES_PRIMARY
    API2 --> POSTGRES_PRIMARY
    API3 --> POSTGRES_PRIMARY
    
    API1 --> QDRANT_CLUSTER
    API2 --> QDRANT_CLUSTER
    API3 --> QDRANT_CLUSTER
    
    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER
    API3 --> REDIS_CLUSTER
    
    POSTGRES_PRIMARY --> POSTGRES_REPLICA
    
    API1 --> PROMETHEUS
    API2 --> PROMETHEUS
    API3 --> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    API1 --> LOGS
    API2 --> LOGS
    API3 --> LOGS
```

### Kubernetes Deployment

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            INGRESS[Nginx Ingress Controller]
            CERT[Cert Manager]
        end
        
        subgraph "Application Namespace"
            API_DEPLOY[Golett API Deployment]
            API_SVC[API Service]
            API_HPA[Horizontal Pod Autoscaler]
        end
        
        subgraph "Database Namespace"
            POSTGRES_DEPLOY[PostgreSQL Deployment]
            POSTGRES_SVC[PostgreSQL Service]
            POSTGRES_PVC[PostgreSQL PVC]
            
            QDRANT_DEPLOY[Qdrant Deployment]
            QDRANT_SVC[Qdrant Service]
            QDRANT_PVC[Qdrant PVC]
        end
        
        subgraph "Monitoring Namespace"
            PROMETHEUS_DEPLOY[Prometheus]
            GRAFANA_DEPLOY[Grafana]
            ALERT_MANAGER[Alert Manager]
        end
        
        subgraph "Configuration"
            CONFIG_MAP[ConfigMap]
            SECRETS[Secrets]
            NETWORK_POLICY[Network Policies]
        end
    end
    
    INGRESS --> API_SVC
    API_SVC --> API_DEPLOY
    API_HPA --> API_DEPLOY
    
    API_DEPLOY --> POSTGRES_SVC
    API_DEPLOY --> QDRANT_SVC
    
    POSTGRES_SVC --> POSTGRES_DEPLOY
    POSTGRES_DEPLOY --> POSTGRES_PVC
    
    QDRANT_SVC --> QDRANT_DEPLOY
    QDRANT_DEPLOY --> QDRANT_PVC
    
    API_DEPLOY --> CONFIG_MAP
    API_DEPLOY --> SECRETS
    
    PROMETHEUS_DEPLOY --> API_DEPLOY
    GRAFANA_DEPLOY --> PROMETHEUS_DEPLOY
    ALERT_MANAGER --> PROMETHEUS_DEPLOY
    
    NETWORK_POLICY --> API_DEPLOY
    NETWORK_POLICY --> POSTGRES_DEPLOY
    NETWORK_POLICY --> QDRANT_DEPLOY
```

---

## Security Architecture

```mermaid
graph TB
    subgraph "External Access"
        INTERNET[Internet]
        CDN[CDN/WAF]
    end
    
    subgraph "Security Perimeter"
        FIREWALL[Firewall]
        DDoS[DDoS Protection]
        SSL_TERM[SSL Termination]
    end
    
    subgraph "Authentication Layer"
        API_GATEWAY[API Gateway]
        AUTH_SERVICE[Authentication Service]
        RATE_LIMITER[Rate Limiter]
    end
    
    subgraph "Application Security"
        API_SERVER[API Server]
        INPUT_VALIDATION[Input Validation]
        AUTHORIZATION[Authorization]
        AUDIT_LOG[Audit Logging]
    end
    
    subgraph "Data Security"
        ENCRYPTION[Data Encryption]
        KEY_MANAGEMENT[Key Management]
        DATA_MASKING[Data Masking]
    end
    
    subgraph "Network Security"
        VPC[Virtual Private Cloud]
        SUBNETS[Private Subnets]
        SECURITY_GROUPS[Security Groups]
        NETWORK_ACL[Network ACLs]
    end
    
    subgraph "Database Security"
        DB_ENCRYPTION[Database Encryption]
        ACCESS_CONTROL[Access Control]
        BACKUP_ENCRYPTION[Backup Encryption]
    end
    
    INTERNET --> CDN
    CDN --> FIREWALL
    FIREWALL --> DDoS
    DDoS --> SSL_TERM
    
    SSL_TERM --> API_GATEWAY
    API_GATEWAY --> AUTH_SERVICE
    AUTH_SERVICE --> RATE_LIMITER
    
    RATE_LIMITER --> API_SERVER
    API_SERVER --> INPUT_VALIDATION
    INPUT_VALIDATION --> AUTHORIZATION
    AUTHORIZATION --> AUDIT_LOG
    
    API_SERVER --> ENCRYPTION
    ENCRYPTION --> KEY_MANAGEMENT
    ENCRYPTION --> DATA_MASKING
    
    API_SERVER --> VPC
    VPC --> SUBNETS
    SUBNETS --> SECURITY_GROUPS
    SECURITY_GROUPS --> NETWORK_ACL
    
    API_SERVER --> DB_ENCRYPTION
    DB_ENCRYPTION --> ACCESS_CONTROL
    DB_ENCRYPTION --> BACKUP_ENCRYPTION
```

---

## Component Interaction Diagrams

### Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: Create Session
    Created --> Active: Initialize Components
    Active --> Processing: Receive Message
    Processing --> Active: Response Sent
    Processing --> Enhanced: Complex Query
    Enhanced --> CrewExecution: Start Crew
    CrewExecution --> Processing: Crew Complete
    Active --> Summarizing: Auto-summarize Trigger
    Summarizing --> Active: Summary Complete
    Active --> Idle: No Activity
    Idle --> Active: New Message
    Idle --> Closed: Timeout/Manual Close
    Active --> Closed: Manual Close
    Closed --> [*]: Cleanup Complete
```

### Memory Layer State Transitions

```mermaid
stateDiagram-v2
    [*] --> InSession: New Content
    InSession --> ShortTerm: Importance ≥ 0.5
    InSession --> Deleted: Low Importance + Expired
    ShortTerm --> LongTerm: Importance ≥ 0.7
    ShortTerm --> Deleted: Medium Importance + Expired
    LongTerm --> Archived: Very Old + Low Access
    LongTerm --> Deleted: Retention Policy
    Archived --> Deleted: Archive Retention
    Deleted --> [*]: Cleanup Complete
```

### Knowledge Source Integration

```mermaid
graph LR
    subgraph "Knowledge Source Lifecycle"
        REGISTER[Register Source]
        VALIDATE[Validate Source]
        PROCESS[Process Content]
        INDEX[Create Index]
        READY[Ready for Queries]
        UPDATE[Update Content]
        REINDEX[Reindex]
        DEPRECATE[Deprecate]
        REMOVE[Remove]
    end
    
    REGISTER --> VALIDATE
    VALIDATE --> PROCESS
    PROCESS --> INDEX
    INDEX --> READY
    READY --> UPDATE
    UPDATE --> REINDEX
    REINDEX --> READY
    READY --> DEPRECATE
    DEPRECATE --> REMOVE
```

---

## Performance Monitoring Architecture

```mermaid
graph TB
    subgraph "Application Metrics"
        API_METRICS[API Response Times]
        MEMORY_METRICS[Memory Usage]
        CREW_METRICS[Crew Performance]
        KNOWLEDGE_METRICS[Knowledge Retrieval]
    end
    
    subgraph "Infrastructure Metrics"
        CPU_METRICS[CPU Usage]
        DISK_METRICS[Disk I/O]
        NETWORK_METRICS[Network Traffic]
        DB_METRICS[Database Performance]
    end
    
    subgraph "Business Metrics"
        USER_METRICS[User Activity]
        SESSION_METRICS[Session Statistics]
        KNOWLEDGE_USAGE[Knowledge Usage]
        ERROR_RATES[Error Rates]
    end
    
    subgraph "Monitoring Stack"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana Dashboards]
        ALERTMANAGER[Alert Manager]
        LOGS[Log Aggregation]
    end
    
    subgraph "Alerting"
        SLACK[Slack Notifications]
        EMAIL[Email Alerts]
        PAGERDUTY[PagerDuty]
        WEBHOOK[Webhook Alerts]
    end
    
    API_METRICS --> PROMETHEUS
    MEMORY_METRICS --> PROMETHEUS
    CREW_METRICS --> PROMETHEUS
    KNOWLEDGE_METRICS --> PROMETHEUS
    
    CPU_METRICS --> PROMETHEUS
    DISK_METRICS --> PROMETHEUS
    NETWORK_METRICS --> PROMETHEUS
    DB_METRICS --> PROMETHEUS
    
    USER_METRICS --> PROMETHEUS
    SESSION_METRICS --> PROMETHEUS
    KNOWLEDGE_USAGE --> PROMETHEUS
    ERROR_RATES --> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTMANAGER
    PROMETHEUS --> LOGS
    
    ALERTMANAGER --> SLACK
    ALERTMANAGER --> EMAIL
    ALERTMANAGER --> PAGERDUTY
    ALERTMANAGER --> WEBHOOK
```

---

*These architecture diagrams provide comprehensive visual documentation of Golett AI's system design, data flows, and component interactions. They serve as reference materials for development, deployment, and maintenance activities.* 