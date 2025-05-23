-- Golett Gateway PostgreSQL Initialization Script
-- This script sets up the initial database schema and configurations

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS golett;
CREATE SCHEMA IF NOT EXISTS memory;
CREATE SCHEMA IF NOT EXISTS sessions;

-- Set search path
SET search_path TO golett, memory, sessions, public;

-- Grant permissions to golett_user
GRANT ALL PRIVILEGES ON SCHEMA golett TO golett_user;
GRANT ALL PRIVILEGES ON SCHEMA memory TO golett_user;
GRANT ALL PRIVILEGES ON SCHEMA sessions TO golett_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA golett TO golett_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA memory TO golett_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sessions TO golett_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA golett TO golett_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA memory TO golett_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sessions TO golett_user;

-- Create tables for memory management
CREATE TABLE IF NOT EXISTS memory.chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    session_type VARCHAR(100) DEFAULT 'standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    state JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES memory.chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    importance_score FLOAT DEFAULT 0.5,
    message_index INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS memory.context_storage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES memory.chat_sessions(id) ON DELETE CASCADE,
    context_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    importance FLOAT DEFAULT 0.5,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT ARRAY[]::TEXT[]
);

CREATE TABLE IF NOT EXISTS memory.decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES memory.chat_sessions(id) ON DELETE CASCADE,
    decision_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    reasoning TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS sessions.crew_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES memory.chat_sessions(id) ON DELETE CASCADE,
    crew_id VARCHAR(255) NOT NULL,
    crew_name VARCHAR(255) NOT NULL,
    agent_count INTEGER DEFAULT 0,
    process_type VARCHAR(100) DEFAULT 'sequential',
    task_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON memory.chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_active ON memory.chat_sessions(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON memory.chat_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON memory.messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON memory.messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_role ON memory.messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_content_gin ON memory.messages USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS idx_context_session_id ON memory.context_storage(session_id);
CREATE INDEX IF NOT EXISTS idx_context_type ON memory.context_storage(context_type);
CREATE INDEX IF NOT EXISTS idx_context_timestamp ON memory.context_storage(timestamp);
CREATE INDEX IF NOT EXISTS idx_context_importance ON memory.context_storage(importance);
CREATE INDEX IF NOT EXISTS idx_context_tags ON memory.context_storage USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_context_content_gin ON memory.context_storage USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS idx_decisions_session_id ON memory.decisions(session_id);
CREATE INDEX IF NOT EXISTS idx_decisions_type ON memory.decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON memory.decisions(timestamp);

CREATE INDEX IF NOT EXISTS idx_crew_registrations_session_id ON sessions.crew_registrations(session_id);
CREATE INDEX IF NOT EXISTS idx_crew_registrations_crew_id ON sessions.crew_registrations(crew_id);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON memory.chat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function to clean up old inactive sessions
CREATE OR REPLACE FUNCTION cleanup_old_sessions(days_threshold INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM memory.chat_sessions 
    WHERE is_active = FALSE 
    AND closed_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_threshold;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION update_updated_at_column() TO golett_user;
GRANT EXECUTE ON FUNCTION cleanup_old_sessions(INTEGER) TO golett_user;

-- Insert some sample data for testing (optional)
INSERT INTO memory.chat_sessions (user_id, session_type, metadata) 
VALUES 
    ('demo_user', 'demo', '{"created_by": "init_script", "purpose": "demonstration"}')
ON CONFLICT DO NOTHING;

-- Create a view for active sessions with message counts
CREATE OR REPLACE VIEW sessions.active_sessions_summary AS
SELECT 
    cs.id,
    cs.user_id,
    cs.session_type,
    cs.created_at,
    cs.updated_at,
    cs.metadata,
    cs.state,
    COUNT(m.id) as message_count,
    MAX(m.timestamp) as last_message_at
FROM memory.chat_sessions cs
LEFT JOIN memory.messages m ON cs.id = m.session_id
WHERE cs.is_active = TRUE
GROUP BY cs.id, cs.user_id, cs.session_type, cs.created_at, cs.updated_at, cs.metadata, cs.state;

-- Grant permissions on the view
GRANT SELECT ON sessions.active_sessions_summary TO golett_user;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Golett Gateway database initialization completed successfully!';
END $$; 