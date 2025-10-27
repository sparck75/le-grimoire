-- Add authentication columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Create enum type if it doesn't exist
DO $$ BEGIN
    CREATE TYPE userrole AS ENUM ('admin', 'collaborator', 'reader');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

ALTER TABLE users ADD COLUMN IF NOT EXISTS role userrole DEFAULT 'reader';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Make OAuth fields nullable
ALTER TABLE users ALTER COLUMN oauth_provider DROP NOT NULL;
ALTER TABLE users ALTER COLUMN oauth_provider_id DROP NOT NULL;

-- Add unique index on username
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username);
