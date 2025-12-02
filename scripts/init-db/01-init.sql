-- HR Management PostgreSQL Initialization Script
-- This script runs when the container is first created

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hrmanagement_db TO hrm_user;

-- Set timezone
SET timezone = 'Asia/Seoul';

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'HR Management database initialized at %', NOW();
END
$$;
