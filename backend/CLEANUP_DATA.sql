-- Clean up all data to start fresh
-- Run this on Supabase to clear all collected data

-- Delete all data in order (respecting foreign keys)
DELETE FROM analysis_results;
DELETE FROM processed_data;
DELETE FROM raw_data;
DELETE FROM datasets WHERE source_type IN ('api_worldbank', 'api_nasa', 'api_fao');

-- Verify cleanup
SELECT 
  (SELECT COUNT(*) FROM datasets) as total_datasets,
  (SELECT COUNT(*) FROM raw_data) as total_raw_data,
  (SELECT COUNT(*) FROM processed_data) as total_processed_data,
  (SELECT COUNT(*) FROM analysis_results) as total_analysis_results;
