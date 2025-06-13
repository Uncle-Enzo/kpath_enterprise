-- KPATH Enterprise Service Integration Schema Migration - Part 1
-- Core Service Extensions

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