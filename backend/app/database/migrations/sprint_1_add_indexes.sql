-- Sprint 1: Add indexes to resources table to optimize query performance

-- Add B-tree index for exact name lookups
CREATE INDEX IF NOT EXISTS ix_resources_name ON resources (name);

-- Add B-tree index for resource_type filtering
CREATE INDEX IF NOT EXISTS ix_resources_type ON resources (resource_type);

-- If using PostgreSQL, create pg_trgm extension and a GIN index for partial (ILIKE) matches
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS ix_resources_name_trgm ON resources USING gin (name gin_trgm_ops);

-- The tags column is stored as Text but parsed as JSON in Python. For true tag indexing:
-- CREATE INDEX IF NOT EXISTS ix_resources_tags_trgm ON resources USING gin (tags gin_trgm_ops);
