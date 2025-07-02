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
GRANT ALL PRIVILEGES ON SCHEMA golett TO golett;
GRANT ALL PRIVILEGES ON SCHEMA memory TO golett;
GRANT ALL PRIVILEGES ON SCHEMA sessions TO golett;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA golett TO golett;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA memory TO golett;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sessions TO golett;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA golett TO golett;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA memory TO golett;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sessions TO golett;
