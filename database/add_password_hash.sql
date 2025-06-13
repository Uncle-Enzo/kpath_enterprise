-- Add password_hash column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Update existing users with a default hash (for testing)
-- This is the hash for 'password123'
UPDATE users 
SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN4/X5.EaJmqMSsU5xGKy'
WHERE password_hash IS NULL;
