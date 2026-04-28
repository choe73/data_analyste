-- ============================================================================
-- SUPABASE SCHEMA MIGRATION - Add missing columns to users table
-- ============================================================================
-- Execute this script in Supabase SQL Editor to fix authentication issues
-- 
-- Steps:
-- 1. Go to https://supabase.com/dashboard/project/[YOUR_PROJECT]/sql/new
-- 2. Copy and paste this entire script
-- 3. Click "Run" button
-- 4. Verify all commands executed successfully
-- ============================================================================

-- Add missing columns to users table (IF NOT EXISTS prevents errors)
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Update existing rows with default values (optional but recommended)
UPDATE public.users SET role = 'user' WHERE role IS NULL;
UPDATE public.users SET is_verified = false WHERE is_verified IS NULL;
UPDATE public.users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;
UPDATE public.users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL;

-- Verify the schema is correct
SELECT 
  column_name, 
  data_type, 
  is_nullable,
  column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
