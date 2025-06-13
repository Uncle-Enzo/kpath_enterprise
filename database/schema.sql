-- KPATH Enterprise Database Schema
-- PostgreSQL 14+
-- Last Updated: December 2024

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search optimization

-- Drop existing tables if they exist (for clean installation)
DROP TABLE IF EXISTS cache_entries CASCADE;
DROP TABLE IF EXISTS feedback_log CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS faiss_index_metadata CASCADE;
DROP TABLE IF EXISTS access_policy CASCADE;
DROP TABLE IF EXISTS service_health CASCADE;
DROP TABLE IF EXISTS service_versions CASCADE;
DROP TABLE IF EXISTS integration_configs CASCADE;
DROP TABLE IF EXISTS query_templates CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS user_selections CASCADE;
DROP TABLE IF EXISTS service_industry CASCADE;
DROP TABLE IF EXISTS interaction_capability CASCADE;
DROP TABLE IF EXISTS service_capability CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Core service registry
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    endpoint TEXT,
    version TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deprecated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service capabilities
CREATE TABLE service_capability (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    capability_desc TEXT NOT NULL,
    capability_name TEXT,
    input_schema JSONB,
    output_schema JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interaction patterns
CREATE TABLE interaction_capability (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    interaction_desc TEXT NOT NULL,
    interaction_type TEXT CHECK (interaction_type IN ('sync', 'async', 'stream', 'batch'))
);

-- Industry/domain classification
CREATE TABLE service_industry (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    domain TEXT NOT NULL,
    UNIQUE(service_id, domain)
);

-- User management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role TEXT CHECK (role IN ('admin', 'editor', 'viewer', 'user')),
    org_id INTEGER,
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Access policies
CREATE TABLE access_policy (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    conditions JSONB NOT NULL,
    type TEXT CHECK (type IN ('RBAC', 'ABAC')),
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FAISS index metadata
CREATE TABLE faiss_index_metadata (
    id SERIAL PRIMARY KEY,
    index_name TEXT,
    last_updated TIMESTAMP,
    embedding_model TEXT,
    total_vectors INTEGER,
    index_params JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logging
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,
    payload JSONB,
    ip_address INET
);

-- Feedback for ranking improvement
CREATE TABLE feedback_log (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    query_embedding_hash TEXT,
    selected_service_id INTEGER REFERENCES services(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    rank_position INTEGER,
    click_through BOOLEAN DEFAULT TRUE
);

-- Cache metadata
CREATE TABLE cache_entries (
    key TEXT PRIMARY KEY,
    value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0
);

-- Service versioning
CREATE TABLE service_versions (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    version TEXT NOT NULL,
    version_tag TEXT CHECK (version_tag IN ('stable', 'beta', 'alpha', 'deprecated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deprecated BOOLEAN DEFAULT FALSE,
    deprecated_at TIMESTAMP,
    sunset_at TIMESTAMP,
    compatible_with TEXT[],
    breaking_changes TEXT[],
    migration_notes TEXT,
    release_notes TEXT,
    UNIQUE(service_id, version)
);

-- Service health monitoring
CREATE TABLE service_health (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    health_status TEXT CHECK (health_status IN ('healthy', 'degraded', 'unhealthy', 'unknown')),
    last_check TIMESTAMP,
    response_time_ms INTEGER,
    error_count INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API key management
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_hash TEXT UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    name TEXT,
    scopes TEXT[],
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Query templates
CREATE TABLE query_templates (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    template TEXT NOT NULL,
    parameters JSONB,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Integration configurations
CREATE TABLE integration_configs (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    config JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(type, name)
);

-- Enhanced feedback tracking
CREATE TABLE user_selections (
    id SERIAL PRIMARY KEY,
    search_id UUID DEFAULT uuid_generate_v4(),
    query TEXT NOT NULL,
    query_embedding_hash TEXT,
    selected_service_id INTEGER REFERENCES services(id),
    result_position INTEGER NOT NULL,
    selection_time_ms INTEGER,
    session_id UUID,
    user_satisfaction BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_services_name ON services(name);
CREATE INDEX idx_services_updated ON services(updated_at);

CREATE INDEX idx_service_capability_service ON service_capability(service_id);
CREATE INDEX idx_service_capability_name ON service_capability(capability_name);

CREATE INDEX idx_interaction_capability_service ON interaction_capability(service_id);
CREATE INDEX idx_interaction_capability_type ON interaction_capability(interaction_type);

CREATE INDEX idx_service_industry_service ON service_industry(service_id);
CREATE INDEX idx_service_industry_domain ON service_industry(domain);

CREATE INDEX idx_feedback_timestamp ON feedback_log(timestamp);
CREATE INDEX idx_feedback_service ON feedback_log(selected_service_id);
CREATE INDEX idx_feedback_user ON feedback_log(user_id);
CREATE INDEX idx_feedback_query_hash ON feedback_log(query_embedding_hash);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);

CREATE INDEX idx_cache_expires ON cache_entries(expires_at);

CREATE INDEX idx_selections_service ON user_selections(selected_service_id);
CREATE INDEX idx_selections_query_hash ON user_selections(query_embedding_hash);
CREATE INDEX idx_selections_timestamp ON user_selections(created_at);

CREATE INDEX idx_service_versions_service ON service_versions(service_id);
CREATE INDEX idx_service_versions_tag ON service_versions(version_tag);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- Create trigger for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE services IS 'Core service registry storing all discoverable services';
COMMENT ON TABLE service_capability IS 'Individual capabilities exposed by each service';
COMMENT ON TABLE users IS 'System users with role-based access control';
COMMENT ON TABLE feedback_log IS 'User feedback for improving search rankings';
COMMENT ON TABLE faiss_index_metadata IS 'Metadata about FAISS vector indexes';
