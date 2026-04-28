-- Add missing columns to forms table in Supabase
-- These columns are defined in the SQLAlchemy Form model but missing from the actual table

ALTER TABLE public.forms ADD COLUMN IF NOT EXISTS max_responses INTEGER;
ALTER TABLE public.forms ADD COLUMN IF NOT EXISTS response_count INTEGER DEFAULT 0;
ALTER TABLE public.forms ADD COLUMN IF NOT EXISTS closes_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.forms ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE public.forms ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Verify the columns exist
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'forms' 
ORDER BY ordinal_position;
