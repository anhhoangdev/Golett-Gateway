-- Golett Gateway Database Schema
-- This script initializes the Golett database with required tables and indexes

\c golett_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA public;

-- ============================================================================
-- MEMORY MANAGEMENT TABLES
-- ============================================================================

-- Memory storage table for PostgreSQL backend
CREATE TABLE IF NOT EXISTS memory_storage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(key)
);

-- Context storage table
CREATE TABLE IF NOT EXISTS context_storage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    context_type VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    importance DECIMAL(3,2) DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    memory_layer VARCHAR(50) DEFAULT 'short_term',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge storage table
CREATE TABLE IF NOT EXISTS knowledge_storage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    source VARCHAR(255),
    description TEXT,
    tags TEXT[],
    importance DECIMAL(3,2) DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    session_id VARCHAR(255),
    memory_layer VARCHAR(50) DEFAULT 'long_term',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decision storage table
CREATE TABLE IF NOT EXISTS decision_storage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    decision_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    reasoning TEXT,
    confidence DECIMAL(3,2) DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSION MANAGEMENT TABLES
-- ============================================================================

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Memory storage indexes
CREATE INDEX IF NOT EXISTS idx_memory_storage_key ON memory_storage(key);
CREATE INDEX IF NOT EXISTS idx_memory_storage_created_at ON memory_storage(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_storage_expires_at ON memory_storage(expires_at);

-- Context storage indexes
CREATE INDEX IF NOT EXISTS idx_context_storage_session_id ON context_storage(session_id);
CREATE INDEX IF NOT EXISTS idx_context_storage_type ON context_storage(context_type);
CREATE INDEX IF NOT EXISTS idx_context_storage_layer ON context_storage(memory_layer);
CREATE INDEX IF NOT EXISTS idx_context_storage_importance ON context_storage(importance);
CREATE INDEX IF NOT EXISTS idx_context_storage_created_at ON context_storage(created_at);

-- Knowledge storage indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_storage_session_id ON knowledge_storage(session_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_storage_source ON knowledge_storage(source);
CREATE INDEX IF NOT EXISTS idx_knowledge_storage_layer ON knowledge_storage(memory_layer);
CREATE INDEX IF NOT EXISTS idx_knowledge_storage_importance ON knowledge_storage(importance);
CREATE INDEX IF NOT EXISTS idx_knowledge_storage_tags ON knowledge_storage USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_storage_created_at ON knowledge_storage(created_at);

-- Vector similarity search index (if vector extension is available)
-- CREATE INDEX IF NOT EXISTS idx_knowledge_storage_embedding ON knowledge_storage USING ivfflat (embedding vector_cosine_ops);

-- Decision storage indexes
CREATE INDEX IF NOT EXISTS idx_decision_storage_session_id ON decision_storage(session_id);
CREATE INDEX IF NOT EXISTS idx_decision_storage_type ON decision_storage(decision_type);
CREATE INDEX IF NOT EXISTS idx_decision_storage_created_at ON decision_storage(created_at);

-- Chat session indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);

-- Chat message indexes
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_memory_storage_updated_at 
    BEFORE UPDATE ON memory_storage 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_context_storage_updated_at 
    BEFORE UPDATE ON context_storage 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_storage_updated_at 
    BEFORE UPDATE ON knowledge_storage 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default memory layer configurations
INSERT INTO memory_storage (key, data, metadata) VALUES 
('config:memory_layers', 
 '{"short_term": {"ttl": 3600}, "long_term": {"ttl": null}, "in_session": {"ttl": 86400}}',
 '{"description": "Memory layer configuration", "type": "system_config"}')
ON CONFLICT (key) DO NOTHING;

-- Insert default system settings
INSERT INTO memory_storage (key, data, metadata) VALUES 
('config:system_settings', 
 '{"enable_normalized_layers": true, "default_importance": 0.5, "max_context_length": 4000}',
 '{"description": "System configuration settings", "type": "system_config"}')
ON CONFLICT (key) DO NOTHING;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO golett_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO golett_user;

-- Log successful initialization
INSERT INTO memory_storage (key, data, metadata) VALUES 
('system:initialization', 
 '{"status": "completed", "timestamp": "' || CURRENT_TIMESTAMP || '", "version": "1.0"}',
 '{"description": "Golett database initialization status", "type": "system_log"}')
ON CONFLICT (key) DO UPDATE SET 
    data = EXCLUDED.data,
    updated_at = CURRENT_TIMESTAMP; 