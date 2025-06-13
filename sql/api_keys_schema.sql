-- API Keys Schema for KPath Enterprise
-- This schema supports multiple API keys per user

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL, -- Store hashed version of API key
    key_prefix VARCHAR(8) NOT NULL, -- First 8 chars for identification
    name VARCHAR(255), -- Optional name for the key (e.g., "Production Server", "Mobile App")
    permissions JSONB DEFAULT '{"search": true}', -- Extensible permissions
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP, -- Optional expiration
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_count INTEGER DEFAULT 0, -- Track usage
    rate_limit INTEGER DEFAULT 1000, -- Requests per hour
    CONSTRAINT unique_user_key_name UNIQUE(user_id, name)
);

-- Create index for faster lookups
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_expires_at ON api_keys(expires_at) WHERE expires_at IS NOT NULL AND is_active = TRUE;

-- Create api_key_logs table for tracking usage
CREATE TABLE IF NOT EXISTS api_key_logs (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL, -- GET, POST, etc.
    ip_address INET,
    user_agent TEXT,
    request_data JSONB, -- Store search parameters
    response_status INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for log lookups
CREATE INDEX idx_api_key_logs_api_key_id ON api_key_logs(api_key_id);
CREATE INDEX idx_api_key_logs_created_at ON api_key_logs(created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing (commented out - uncomment to use)
/*
-- Insert test user
INSERT INTO users (username, email) VALUES ('test_user', 'test@example.com');

-- Note: In production, you would generate a secure random API key and hash it
-- This is just an example - the actual key would be hashed before storage
INSERT INTO api_keys (user_id, key_hash, key_prefix, name, permissions)
VALUES (
    1,
    'hashed_api_key_here', -- In practice, use SHA256 or similar
    'kpe_test', -- Key prefix for identification
    'Test API Key',
    '{"search": true, "admin": false}'::jsonb
);
*/