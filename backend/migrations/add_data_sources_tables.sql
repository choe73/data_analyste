-- Migration: Add data_sources and collection_logs tables for generic data collection

-- Create data_sources table
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Identity
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100),
    country VARCHAR(100),
    
    -- API Configuration
    url VARCHAR(500) NOT NULL,
    api_type VARCHAR(50) NOT NULL DEFAULT 'rest',
    api_version VARCHAR(50),
    
    -- Authentication
    auth_type VARCHAR(50) NOT NULL DEFAULT 'none',
    auth_credentials JSONB,
    
    -- Schema and mapping
    schema_mapping JSONB,
    data_format VARCHAR(50),
    
    -- Collection
    collection_frequency VARCHAR(100),
    last_collected TIMESTAMP,
    next_collection TIMESTAMP,
    
    -- Pagination
    supports_pagination BOOLEAN DEFAULT TRUE,
    pagination_type VARCHAR(50),
    pagination_param VARCHAR(100),
    page_size INTEGER DEFAULT 100,
    
    -- Rate limiting
    rate_limit INTEGER,
    rate_limit_window INTEGER DEFAULT 60,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'testing',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    total_records INTEGER DEFAULT 0,
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at),
    INDEX idx_category (category),
    INDEX idx_country (country)
);

-- Create collection_logs table
CREATE TABLE IF NOT EXISTS collection_logs (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Results
    status VARCHAR(50),
    records_fetched INTEGER DEFAULT 0,
    records_stored INTEGER DEFAULT 0,
    
    -- Details
    error_message TEXT,
    execution_time INTEGER,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_data_source_id (data_source_id),
    INDEX idx_started_at (started_at)
);

-- Create indexes for better query performance
CREATE INDEX idx_data_sources_user_status ON data_sources(user_id, status);
CREATE INDEX idx_data_sources_next_collection ON data_sources(next_collection) WHERE is_active = TRUE;
CREATE INDEX idx_collection_logs_data_source_started ON collection_logs(data_source_id, started_at DESC);
