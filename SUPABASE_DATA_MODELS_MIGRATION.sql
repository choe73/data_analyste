-- ============================================================================
-- SUPABASE SCHEMA MIGRATION - Create data collection tables
-- ============================================================================
-- Execute this script in Supabase SQL Editor to create data collection tables
-- 
-- Steps:
-- 1. Go to https://supabase.com/dashboard/project/[YOUR_PROJECT]/sql/new
-- 2. Copy and paste this entire script
-- 3. Click "Run" button
-- 4. Verify all commands executed successfully
-- ============================================================================

-- Create raw_data table for storing unprocessed API responses
CREATE TABLE IF NOT EXISTS public.raw_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    hash VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for raw_data
CREATE INDEX IF NOT EXISTS idx_raw_data_source ON public.raw_data(source);
CREATE INDEX IF NOT EXISTS idx_raw_data_dataset ON public.raw_data(dataset_name);
CREATE INDEX IF NOT EXISTS idx_raw_data_hash ON public.raw_data(hash);
CREATE INDEX IF NOT EXISTS idx_raw_data_created ON public.raw_data(created_at);

-- Create processed_data table for storing structured data from external sources
CREATE TABLE IF NOT EXISTS public.processed_data (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(50) NOT NULL,
    indicator VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    date_value TIMESTAMP WITH TIME ZONE NOT NULL,
    numeric_value FLOAT,
    text_value TEXT,
    meta_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for processed_data
CREATE INDEX IF NOT EXISTS idx_processed_data_domain ON public.processed_data(domain);
CREATE INDEX IF NOT EXISTS idx_processed_data_indicator ON public.processed_data(indicator);
CREATE INDEX IF NOT EXISTS idx_processed_data_region ON public.processed_data(region);
CREATE INDEX IF NOT EXISTS idx_processed_data_date ON public.processed_data(date_value);
CREATE INDEX IF NOT EXISTS idx_processed_data_created ON public.processed_data(created_at);

-- Verify tables were created
SELECT 
  table_name,
  column_name, 
  data_type, 
  is_nullable
FROM information_schema.columns 
WHERE table_name IN ('raw_data', 'processed_data')
ORDER BY table_name, ordinal_position;
