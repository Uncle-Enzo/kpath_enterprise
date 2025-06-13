-- KPATH Enterprise Service Integration Schema Migration
-- Version: 2.0.0
-- Description: Extends service metadata to support full enterprise integration

-- =========================================
-- PHASE 1: Core Service Extensions
-- =========================================

-- Extend the services table with integration metadata
ALTER TABLE services 
ADD COLUMN IF NOT EXISTS tool_type VARCHAR(50) DEFAULT 'API',
ADD COLUMN IF NOT EXISTS interaction_modes TEXT[],
ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'internal',
ADD COLUMN IF NOT EXISTS deprecation_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS deprecation_notice TEXT,
ADD COLUMN IF NOT EXISTS success_criteria JSONB,
ADD COLUMN IF NOT EXISTS default_timeout_ms INTEGER DEFAULT 30000,
ADD COLUMN IF NOT EXISTS default_retry_policy JSONB;

-- Add constraints for tool_type
ALTER TABLE services DROP CONSTRAINT IF EXISTS check_tool_type;
ALTER TABLE services ADD CONSTRAINT check_tool_type 
CHECK (tool_type IN ('InternalAgent', 'ExternalAgent', 'API', 
                     'LegacySystem', 'ESBEndpoint', 'MicroService'));

-- Add constraints for visibility
ALTER TABLE services DROP CONSTRAINT IF EXISTS check_visibility;
ALTER TABLE services ADD CONSTRAINT check_visibility 
CHECK (visibility IN ('internal', 'org-wide', 'public', 'restricted'));

-- Create service integration details table
CREATE TABLE IF NOT EXISTS service_integration_details (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    
    -- Protocol Information
    access_protocol VARCHAR(50) NOT NULL,
    base_endpoint TEXT,
    
    -- Authentication
    auth_method VARCHAR(50),
    auth_config JSONB,
    auth_endpoint TEXT,
    
    -- Rate Limiting & Performance
    rate_limit_requests INTEGER,
    rate_limit_window_seconds INTEGER,
    max_concurrent_requests INTEGER,
    circuit_breaker_config JSONB,
    
    -- Request/Response Configuration
    default_headers JSONB,
    request_content_type VARCHAR(100) DEFAULT 'application/json',
    response_content_type VARCHAR(100) DEFAULT 'application/json',
    request_transform JSONB,
    response_transform JSONB,
    
    -- ESB Specific Fields
    esb_type VARCHAR(50),
    esb_service_name TEXT,
    esb_routing_key TEXT,
    esb_operation TEXT,
    esb_adapter_type VARCHAR(50),
    esb_namespace TEXT,
    esb_version VARCHAR(20),
    
    -- Health Check
    health_check_endpoint TEXT,
    health_check_interval_seconds INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(service_id)
);

-- Create indexes for integration details
CREATE INDEX IF NOT EXISTS idx_integration_protocol 
ON service_integration_details(access_protocol);

CREATE INDEX IF NOT EXISTS idx_integration_esb_type 
ON service_integration_details(esb_type);