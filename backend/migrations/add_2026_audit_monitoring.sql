-- Migration: Add 2026 audit, monitoring, and trust verification tables
-- Non-breaking: All new tables, no modifications to existing tables

-- ============ DATA AUDIT TABLE ============
CREATE TABLE IF NOT EXISTS data_audit (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    collection_log_id INTEGER REFERENCES collection_logs(id) ON DELETE SET NULL,
    
    -- Data integrity
    data_hash VARCHAR(256) UNIQUE,
    record_count INTEGER DEFAULT 0,
    
    -- Trust & Quality Scores (0-100)
    trust_score FLOAT DEFAULT 0.0,
    authenticity_score FLOAT DEFAULT 0.0,
    consistency_score FLOAT DEFAULT 0.0,
    freshness_score FLOAT DEFAULT 0.0,
    source_reputation_score FLOAT DEFAULT 0.0,
    
    -- AI Detection
    ai_generated_count INTEGER DEFAULT 0,
    ai_generated_percentage FLOAT DEFAULT 0.0,
    
    -- Cross-verification
    cross_verified BOOLEAN DEFAULT FALSE,
    cross_verified_sources INTEGER DEFAULT 0,
    verification_status VARCHAR(50),
    
    -- Data Quality Metrics
    completeness FLOAT DEFAULT 0.0,
    validity FLOAT DEFAULT 0.0,
    uniqueness FLOAT DEFAULT 0.0,
    
    -- Anomalies
    anomalies_detected JSONB,
    suspicious_records INTEGER DEFAULT 0,
    extreme_values JSONB,
    
    -- Timestamps
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_data_source_id (data_source_id),
    INDEX idx_collected_at (collected_at),
    INDEX idx_trust_score (trust_score),
    INDEX idx_data_hash (data_hash)
);

-- ============ DETAILED COLLECTION LOGS ============
CREATE TABLE IF NOT EXISTS collection_logs_detailed (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Collection Status
    status VARCHAR(50),
    records_fetched INTEGER DEFAULT 0,
    records_stored INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    
    -- Performance Metrics (milliseconds)
    execution_time_ms INTEGER,
    fetch_time_ms INTEGER,
    transform_time_ms INTEGER,
    validation_time_ms INTEGER,
    storage_time_ms INTEGER,
    
    -- Network Metrics
    http_status_code INTEGER,
    retries_count INTEGER DEFAULT 0,
    timeout_count INTEGER DEFAULT 0,
    
    -- Error Tracking
    error_message TEXT,
    error_type VARCHAR(100),
    error_stack TEXT,
    
    -- Quality Metrics
    quality_score FLOAT DEFAULT 0.0,
    trust_score FLOAT DEFAULT 0.0,
    
    -- Pagination
    pages_fetched INTEGER DEFAULT 1,
    total_pages INTEGER,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_data_source_id (data_source_id),
    INDEX idx_started_at (started_at),
    INDEX idx_status (status),
    INDEX idx_quality_score (quality_score)
);

-- ============ SOURCE REPUTATION ============
CREATE TABLE IF NOT EXISTS source_reputation (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL UNIQUE REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Reputation Scores (0-100)
    overall_score FLOAT DEFAULT 50.0,
    reliability_score FLOAT DEFAULT 50.0,
    data_quality_score FLOAT DEFAULT 50.0,
    consistency_score FLOAT DEFAULT 50.0,
    freshness_score FLOAT DEFAULT 50.0,
    
    -- History
    total_collections INTEGER DEFAULT 0,
    successful_collections INTEGER DEFAULT 0,
    failed_collections INTEGER DEFAULT 0,
    avg_quality_score FLOAT DEFAULT 0.0,
    
    -- Flags
    is_trusted BOOLEAN DEFAULT FALSE,
    is_deprecated BOOLEAN DEFAULT FALSE,
    is_under_review BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_data_source_id (data_source_id),
    INDEX idx_overall_score (overall_score),
    INDEX idx_is_trusted (is_trusted)
);

-- ============ INDEXES FOR PERFORMANCE ============
CREATE INDEX idx_data_audit_trust_score ON data_audit(trust_score DESC);
CREATE INDEX idx_data_audit_ai_generated ON data_audit(ai_generated_count DESC);
CREATE INDEX idx_collection_logs_detailed_quality ON collection_logs_detailed(quality_score DESC);
CREATE INDEX idx_source_reputation_overall ON source_reputation(overall_score DESC);

-- ============ OPTIONAL: Add columns to existing data_sources table ============
-- These are optional and non-breaking
ALTER TABLE data_sources ADD COLUMN IF NOT EXISTS data_quality_score FLOAT DEFAULT 0.0;
ALTER TABLE data_sources ADD COLUMN IF NOT EXISTS trust_score FLOAT DEFAULT 0.0;
ALTER TABLE data_sources ADD COLUMN IF NOT EXISTS last_trust_verification TIMESTAMP;
ALTER TABLE data_sources ADD COLUMN IF NOT EXISTS ai_detection_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE data_sources ADD COLUMN IF NOT EXISTS cross_verification_enabled BOOLEAN DEFAULT FALSE;

-- ============ COMMENTS FOR DOCUMENTATION ============
COMMENT ON TABLE data_audit IS 'Immutable audit trail for data integrity and compliance (blockchain-like)';
COMMENT ON TABLE collection_logs_detailed IS 'Detailed collection metrics for performance monitoring and debugging';
COMMENT ON TABLE source_reputation IS 'Dynamic source reputation scoring based on collection history';
COMMENT ON COLUMN data_audit.data_hash IS 'SHA-256 hash of collected data for integrity verification';
COMMENT ON COLUMN data_audit.trust_score IS 'Overall trust score (0-100) combining authenticity, consistency, freshness';
COMMENT ON COLUMN collection_logs_detailed.execution_time_ms IS 'Total collection execution time in milliseconds';
COMMENT ON COLUMN source_reputation.overall_score IS 'Dynamic reputation score (0-100), starts at 50 for new sources';
