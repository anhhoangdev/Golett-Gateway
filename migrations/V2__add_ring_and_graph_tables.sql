-- -----------------------------------------------------------------------------
-- V2  •  Expand memory model + add basic graph storage tables
-- -----------------------------------------------------------------------------
-- 0. Ensure `memory_items` table exists (was not part of V1 baseline)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS memory_items (
    id               UUID PRIMARY KEY,
    source_id        UUID,
    session_id       UUID,
    type             TEXT,
    content          TEXT,
    importance       NUMERIC,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata         JSONB,
    ring             TEXT NOT NULL DEFAULT 'in_session'
);

-- Helpful indexes if the table was just created
CREATE INDEX IF NOT EXISTS idx_memory_items_session ON memory_items (session_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_type    ON memory_items (type);

-- 1. Add `ring` column to `memory_items` to distinguish logical storage tiers
--    (in_session, short_term, long_term) explicitly.
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    ALTER TABLE memory_items
        ADD CONSTRAINT chk_memory_items_ring
        CHECK (ring IN ('in_session', 'short_term', 'long_term'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END$$;

-- Optional: back-fill existing rows that should live in the other rings
-- (only runs if you already have data from before this migration)
UPDATE memory_items
   SET ring = 'short_term'
 WHERE ring = 'in_session'            -- default value
   AND type = 'summary'
   AND session_id IS NULL;

UPDATE memory_items
   SET ring = 'long_term'
 WHERE ring = 'in_session'
   AND type IN ('fact', 'procedure', 'entity')
   AND session_id IS NULL;

-- Helpful index for ring-based look-ups
CREATE INDEX IF NOT EXISTS idx_memory_items_ring ON memory_items (ring);

-- -----------------------------------------------------------------------------
-- 2. Knowledge-graph backing tables (PostgresGraphStore)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graph_nodes (
    id         UUID PRIMARY KEY,
    label      TEXT,
    properties JSONB
);

CREATE TABLE IF NOT EXISTS graph_edges (
    src      UUID REFERENCES graph_nodes (id),
    dst      UUID REFERENCES graph_nodes (id),
    type     TEXT,
    metadata JSONB,
    PRIMARY KEY (src, dst, type)
);

-- Basic indexes to speed up neighbourhood queries
CREATE INDEX IF NOT EXISTS idx_graph_edges_src ON graph_edges (src);
CREATE INDEX IF NOT EXISTS idx_graph_edges_dst ON graph_edges (dst); 