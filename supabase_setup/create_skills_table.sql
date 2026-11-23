-- ============================================================================
-- MIGRATION: Create Skills Table for Automated Skill Discovery
-- ============================================================================
-- Purpose: Single source of truth for all skills with write-only automation
-- Created: November 12, 2026
-- Status: Ready for deployment to Supabase
-- ============================================================================

-- Create skills table with RLS policies for write-only automation
CREATE TABLE IF NOT EXISTS public.skills (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Fields
    skill_name text NOT NULL UNIQUE,
    category text NOT NULL DEFAULT 'discovered',  -- 'core' | 'discovered'
    source text NOT NULL DEFAULT 'llm',           -- 'manual' | 'llm'
    
    -- Quality Metrics
    confidence_score smallint DEFAULT 80,         -- 0-100
    validation_status text DEFAULT 'pending',     -- 'pending' | 'validated' | 'rejected'
    
    -- Context
    discovered_from_job_id text,                  -- Which job discovered this
    description text,                             -- Optional skill description
    tags text[] DEFAULT '{}',                     -- Category tags (e.g., ['backend', 'cloud'])
    
    -- Tracking
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    -- Constraints
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 100),
    CONSTRAINT valid_category CHECK (category IN ('core', 'discovered')),
    CONSTRAINT valid_source CHECK (source IN ('manual', 'llm')),
    CONSTRAINT valid_status CHECK (validation_status IN ('pending', 'validated', 'rejected'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_skills_name ON public.skills(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON public.skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_source ON public.skills(source);
CREATE INDEX IF NOT EXISTS idx_skills_validation ON public.skills(validation_status);
CREATE INDEX IF NOT EXISTS idx_skills_confidence ON public.skills(confidence_score DESC);

-- Enable Row Level Security
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;

-- RLS Policy 1: Service role can INSERT only (write-only automation protection)
DROP POLICY IF EXISTS "service_role_insert_only" ON public.skills;
CREATE POLICY "service_role_insert_only" ON public.skills
    FOR INSERT
    WITH CHECK (true)
    TO service_role;

-- RLS Policy 2: Service role CANNOT UPDATE
DROP POLICY IF EXISTS "service_role_deny_update" ON public.skills;
CREATE POLICY "service_role_deny_update" ON public.skills
    FOR UPDATE
    USING (false)
    TO service_role;

-- RLS Policy 3: Service role CANNOT DELETE
DROP POLICY IF EXISTS "service_role_deny_delete" ON public.skills;
CREATE POLICY "service_role_deny_delete" ON public.skills
    FOR DELETE
    USING (false)
    TO service_role;

-- RLS Policy 4: Everyone can SELECT (read-only access to all)
DROP POLICY IF EXISTS "allow_select_all" ON public.skills;
CREATE POLICY "allow_select_all" ON public.skills
    FOR SELECT
    USING (true);

-- RLS Policy 5: Admin role can do everything (future skill curation)
-- Note: This assumes admin_users table exists with user_id column
-- For initial setup, can comment this out and add later
DROP POLICY IF EXISTS "admin_full_access" ON public.skills;
CREATE POLICY "admin_full_access" ON public.skills
    FOR ALL
    USING (
        auth.jwt() ->> 'role' = 'admin'
    );

-- ============================================================================
-- Optional: Seed with Core Skills (can be done later via application)
-- ============================================================================
-- Uncomment and modify if you want to seed initial core skills
-- 
-- INSERT INTO public.skills (skill_name, category, source, confidence_score, validation_status)
-- VALUES
--     ('Python', 'core', 'manual', 100, 'validated'),
--     ('JavaScript', 'core', 'manual', 100, 'validated'),
--     ('React', 'core', 'manual', 100, 'validated'),
--     ('TypeScript', 'core', 'manual', 100, 'validated'),
--     ('PostgreSQL', 'core', 'manual', 100, 'validated'),
--     ('AWS', 'core', 'manual', 100, 'validated'),
--     ('Docker', 'core', 'manual', 100, 'validated'),
--     ('Kubernetes', 'core', 'manual', 100, 'validated'),
--     ('SQL', 'core', 'manual', 100, 'validated'),
--     ('REST API', 'core', 'manual', 100, 'validated')
-- ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- Views for Monitoring Skill Discovery
-- ============================================================================

-- View: Recently discovered skills
CREATE OR REPLACE VIEW public.vw_recently_discovered_skills AS
SELECT 
    skill_name,
    category,
    source,
    confidence_score,
    validation_status,
    discovered_from_job_id,
    created_at
FROM public.skills
WHERE source = 'llm' AND category = 'discovered'
ORDER BY created_at DESC
LIMIT 50;

-- View: Skills by validation status
CREATE OR REPLACE VIEW public.vw_skills_by_status AS
SELECT 
    validation_status,
    category,
    source,
    COUNT(*) as count,
    MIN(created_at) as oldest_date,
    MAX(created_at) as newest_date,
    ROUND(AVG(confidence_score)) as avg_confidence
FROM public.skills
GROUP BY validation_status, category, source
ORDER BY validation_status, category, source;

-- View: Low confidence discovered skills
CREATE OR REPLACE VIEW public.vw_low_confidence_skills AS
SELECT 
    skill_name,
    confidence_score,
    source,
    category,
    discovered_from_job_id,
    created_at
FROM public.skills
WHERE source = 'llm' AND confidence_score < 70 AND category = 'discovered'
ORDER BY confidence_score ASC, created_at DESC;

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- Run these to verify the setup:
--
-- 1. Check table exists:
--    SELECT * FROM public.skills LIMIT 5;
--
-- 2. Check RLS policies:
--    SELECT * FROM pg_policies WHERE tablename = 'skills';
--
-- 3. Check indexes:
--    SELECT * FROM pg_indexes WHERE tablename = 'skills';
--
-- 4. Check views:
--    SELECT * FROM public.vw_recently_discovered_skills;
--    SELECT * FROM public.vw_skills_by_status;
-- ============================================================================
