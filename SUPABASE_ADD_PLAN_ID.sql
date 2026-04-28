-- Add plan_id column to subscriptions table
-- Execute this in Supabase SQL Editor

ALTER TABLE public.subscriptions 
ADD COLUMN IF NOT EXISTS plan_id INTEGER REFERENCES public.plans(id);

-- Add missing quota columns if they don't exist
ALTER TABLE public.subscriptions 
ADD COLUMN IF NOT EXISTS datasets_created_this_month INTEGER DEFAULT 0;

ALTER TABLE public.subscriptions 
ADD COLUMN IF NOT EXISTS forms_created_this_month INTEGER DEFAULT 0;

ALTER TABLE public.subscriptions 
ADD COLUMN IF NOT EXISTS gemini_calls_this_month INTEGER DEFAULT 0;

-- Verify the columns were added
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'subscriptions' 
ORDER BY ordinal_position;
