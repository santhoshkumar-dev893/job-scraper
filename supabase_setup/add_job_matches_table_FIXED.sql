-- ============================================================================
-- MIGRATION: Add Job Matches Table for Improved Workflow
-- ============================================================================
-- Purpose: Store detailed job matching results for each profile
-- Created: November 6, 2026
-- Status: Ready for deployment to Supabase
-- ============================================================================

-- Create job_matches table
CREATE TABLE IF NOT EXISTS public.job_matches (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    job_id text NOT NULL,
    profile_id uuid NOT NULL,
    
    -- Scoring Results
    ats_score smallint NOT NULL CHECK (ats_score >= 0 AND ats_score <= 100),
    gate_passed boolean NOT NULL DEFAULT false,
    confidence_score smallint CHECK (confidence_score >= 0 AND confidence_score <= 100),
    
    -- Intermediate Scores
    heuristic_score smallint CHECK (heuristic_score >= 0 AND heuristic_score <= 100),
    llm_score smallint CHECK (llm_score >= 0 AND llm_score <= 100),
    
    -- Skill Details (JSONB for flexibility)
    matched_skills jsonb DEFAULT '[]'::jsonb,        -- Array of skill names
    missing_skills jsonb DEFAULT '[]'::jsonb,        -- Array of skill names
    mandatory_missing jsonb DEFAULT '[]'::jsonb,     -- Array of skill names
    
    -- New Skills for Human Review
    new_skills jsonb DEFAULT '[]'::jsonb,            -- Array of {name, requirement, evidence}
    
    -- Pipeline metadata
    path text NOT NULL,                              -- heuristic_only | llm_rescored | llm_failed | llm_disabled
    data_quality text NOT NULL DEFAULT 'low',        -- high | low
    warnings jsonb DEFAULT '[]'::jsonb,              -- Array of warning strings
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    -- Constraints
    FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES public.user_profiles(id) ON DELETE CASCADE
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_job_matches_profile_id ON public.job_matches(profile_id);
CREATE INDEX IF NOT EXISTS idx_job_matches_job_id ON public.job_matches(job_id);
CREATE INDEX IF NOT EXISTS idx_job_matches_gate_passed ON public.job_matches(gate_passed);
CREATE INDEX IF NOT EXISTS idx_job_matches_path ON public.job_matches(path);
CREATE INDEX IF NOT EXISTS idx_job_matches_created_at ON public.job_matches(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_job_matches_profile_gate ON public.job_matches(profile_id, gate_passed);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_job_matches_profile_pass_score 
ON public.job_matches(profile_id, gate_passed, ats_score DESC);

-- Enable Row Level Security
ALTER TABLE public.job_matches ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Allow service_role full access (backend scoring service)
CREATE POLICY rls_job_matches_service_role ON public.job_matches
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- RLS Policy: Allow authenticated users to select their own matches
-- Note: This requires auth_user_id column in user_profiles for user-facing access
-- For now, restricting to service_role only
CREATE POLICY rls_job_matches_deny_anonymous ON public.job_matches
    FOR SELECT
    USING (auth.role() = 'service_role');

-- Create view: Jobs that passed the gate for a profile
CREATE OR REPLACE VIEW public.vw_matched_jobs_by_profile AS
SELECT 
    jm.profile_id,
    jm.job_id,
    jm.ats_score,
    jm.confidence_score,
    jm.path,
    jm.matched_skills,
    jm.missing_skills,
    jm.mandatory_missing,
    j.company,
    j.job_title,
    j.location,
    j.provider,
    j.posted_at,
    jm.created_at
FROM public.job_matches jm
INNER JOIN public.jobs j ON jm.job_id = j.job_id
WHERE jm.gate_passed = true
ORDER BY jm.ats_score DESC, jm.created_at DESC;

-- Create view: Jobs that need attention (gate failed but have new skills)
CREATE OR REPLACE VIEW public.vw_pending_skill_review AS
SELECT 
    jm.profile_id,
    jm.job_id,
    jm.ats_score,
    jm.new_skills,
    j.company,
    j.job_title,
    j.location,
    jm.created_at
FROM public.job_matches jm
INNER JOIN public.jobs j ON jm.job_id = j.job_id
WHERE jm.gate_passed = false 
  AND jsonb_array_length(jm.new_skills) > 0
ORDER BY jm.created_at DESC;

-- Create view: Pipeline analytics
CREATE OR REPLACE VIEW public.vw_matching_analytics AS
SELECT 
    profile_id,
    COUNT(*) as total_jobs_evaluated,
    SUM(CASE WHEN gate_passed THEN 1 ELSE 0 END) as jobs_passed,
    SUM(CASE WHEN NOT gate_passed THEN 1 ELSE 0 END) as jobs_failed,
    ROUND(AVG(ats_score)::numeric, 2) as avg_ats_score,
    MAX(ats_score) as best_match_score,
    MIN(ats_score) as worst_match_score,
    COUNT(DISTINCT path) as paths_used,
    SUM(CASE WHEN path = 'llm_rescored' THEN 1 ELSE 0 END) as jobs_needing_llm,
    ROUND(
        100.0 * SUM(CASE WHEN path = 'llm_rescored' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) as llm_fallback_rate
FROM public.job_matches
GROUP BY profile_id;

-- Add comments
COMMENT ON TABLE public.job_matches IS 'Detailed job matching results from improved workflow';
COMMENT ON COLUMN public.job_matches.ats_score IS 'ATS match score (0-100)';
COMMENT ON COLUMN public.job_matches.gate_passed IS 'Whether the profile fits this job';
COMMENT ON COLUMN public.job_matches.path IS 'Pipeline path taken: heuristic_only, llm_rescored, llm_failed, llm_disabled';
COMMENT ON COLUMN public.job_matches.matched_skills IS 'JSON array of skills found in profile';
COMMENT ON COLUMN public.job_matches.missing_skills IS 'JSON array of skills not in profile';
COMMENT ON COLUMN public.job_matches.mandatory_missing IS 'JSON array of mandatory skills not in profile';
COMMENT ON COLUMN public.job_matches.new_skills IS 'JSON array of new skills discovered by LLM pending human review';
COMMENT ON COLUMN public.job_matches.confidence_score IS 'Overall confidence in the match (0-100)';
COMMENT ON VIEW public.vw_matched_jobs_by_profile IS 'Jobs where profile passed the gate, sorted by match quality';
COMMENT ON VIEW public.vw_pending_skill_review IS 'Jobs with new skills pending human vocabulary review';
COMMENT ON VIEW public.vw_matching_analytics IS 'Analytics about matching pipeline performance per profile';

-- Grant permissions to service_role (backend service)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.job_matches TO service_role;
GRANT SELECT ON public.vw_matched_jobs_by_profile TO service_role;
GRANT SELECT ON public.vw_pending_skill_review TO service_role;
GRANT SELECT ON public.vw_matching_analytics TO service_role;

-- Grant permissions to authenticated users (read-only for now)
GRANT SELECT ON public.job_matches TO authenticated;
GRANT SELECT ON public.vw_matched_jobs_by_profile TO authenticated;
GRANT SELECT ON public.vw_pending_skill_review TO authenticated;
GRANT SELECT ON public.vw_matching_analytics TO authenticated;

COMMIT;
