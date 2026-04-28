-- Initialize plans table with default plans
-- Execute this in Supabase SQL Editor after the plans table is created

-- Create plans table if not exists
CREATE TABLE IF NOT EXISTS public.plans (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    price_xaf INTEGER,
    features JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create payments table if not exists
CREATE TABLE IF NOT EXISTS public.payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    amount_xaf INTEGER NOT NULL,
    currency TEXT DEFAULT 'XAF',
    status TEXT DEFAULT 'pending',
    payment_provider TEXT,
    provider_payment_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Insert default plans
INSERT INTO public.plans (name, price_xaf, features) VALUES
('free', 0, '{"max_analyses": 2, "max_datasets": 3, "max_forms": 2, "gemini": false, "export": false}'),
('standard', 1000, '{"max_analyses": 20, "max_datasets": 50, "max_forms": 20, "gemini": true, "export": true}'),
('advanced', 5000, '{"max_analyses": 100, "max_datasets": 500, "max_forms": 100, "gemini": true, "export": true, "team": false}'),
('enterprise', NULL, '{"custom": true}')
ON CONFLICT (name) DO NOTHING;

-- Verify plans were inserted
SELECT * FROM public.plans ORDER BY price_xaf ASC NULLS LAST;
