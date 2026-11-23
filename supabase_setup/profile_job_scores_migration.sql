ALTER TABLE "public"."jobs"
DROP COLUMN IF EXISTS "profile_id" CASCADE,
DROP COLUMN IF EXISTS "profile_score" CASCADE,
DROP COLUMN IF EXISTS "profile_match_reason" CASCADE,
DROP COLUMN IF EXISTS "scored_at" CASCADE;

-- =========================================================
-- STEP 2: Create profile_job_scores junction table
-- =========================================================
-- This table stores the score of each job for each user profile
-- One row per (profile_id, job_id) pair
CREATE TABLE IF NOT EXISTS "public"."profile_job_scores" (
    -- Foreign Keys
    "profile_id" UUID NOT NULL REFERENCES "public"."user_profiles"("id") ON DELETE CASCADE,
    "job_id" TEXT NOT NULL REFERENCES "public"."jobs"("job_id") ON DELETE CASCADE,
    
    -- Overall Score
    "profile_score" SMALLINT CHECK ("profile_score" >= 0 AND "profile_score" <= 100),
    "profile_match_reason" TEXT,
    
    -- Detailed Scoring Breakdown (each max 20)
    "career_fit" SMALLINT CHECK ("career_fit" >= 0 AND "career_fit" <= 20),
    "skills_fit" SMALLINT CHECK ("skills_fit" >= 0 AND "skills_fit" <= 20),
    "seniority_fit" SMALLINT CHECK ("seniority_fit" >= 0 AND "seniority_fit" <= 20),
    "location_fit" SMALLINT CHECK ("location_fit" >= 0 AND "location_fit" <= 20),
    "culture_fit" SMALLINT CHECK ("culture_fit" >= 0 AND "culture_fit" <= 20),
    
    -- Reasoning Arrays
    "key_positives" TEXT[] DEFAULT '{}',
    "key_concerns" TEXT[] DEFAULT '{}',
    "should_apply" BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    "scored_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Composite Primary Key: (profile_id, job_id)
    -- Ensures only one score per profile per job
    PRIMARY KEY ("profile_id", "job_id")
);

-- Add comments for clarity
COMMENT ON TABLE "public"."profile_job_scores" IS 'Junction table: stores profile-level scores for jobs. Each (profile_id, job_id) pair has exactly one score.';
COMMENT ON COLUMN "public"."profile_job_scores"."profile_id" IS 'Reference to user profile that scored this job';
COMMENT ON COLUMN "public"."profile_job_scores"."job_id" IS 'Reference to the job being scored';
COMMENT ON COLUMN "public"."profile_job_scores"."profile_score" IS 'Overall fit score 0-100 for this job against this profile';
COMMENT ON COLUMN "public"."profile_job_scores"."profile_match_reason" IS 'LLM explanation of why this score was given';
COMMENT ON COLUMN "public"."profile_job_scores"."career_fit" IS 'Career alignment score (0-20): does it align with career goals?';
COMMENT ON COLUMN "public"."profile_job_scores"."skills_fit" IS 'Skills match score (0-20): do they have required/preferred skills?';
COMMENT ON COLUMN "public"."profile_job_scores"."seniority_fit" IS 'Seniority alignment score (0-20): is role appropriate for their level?';
COMMENT ON COLUMN "public"."profile_job_scores"."location_fit" IS 'Location/remote fit score (0-20): matches preferences?';
COMMENT ON COLUMN "public"."profile_job_scores"."culture_fit" IS 'Company culture fit score (0-20): company size, industry, signals?';

-- =========================================================
-- STEP 3: Create indexes for fast queries
-- =========================================================

-- Query 1: "Get top 10 jobs for profile X"
CREATE INDEX IF NOT EXISTS "idx_profile_job_scores_profile_score"
ON "public"."profile_job_scores" ("profile_id", "profile_score" DESC NULLS LAST);

-- Query 2: "Get all profiles that scored job Y"
CREATE INDEX IF NOT EXISTS "idx_profile_job_scores_job_id"
ON "public"."profile_job_scores" ("job_id", "profile_score" DESC NULLS LAST);

-- Query 3: "Has profile X scored job Y?"
CREATE INDEX IF NOT EXISTS "idx_profile_job_scores_lookup"
ON "public"."profile_job_scores" ("profile_id", "job_id");

-- =========================================================
-- STEP 4: Create useful views
-- =========================================================

-- View 1: Top scored jobs for each profile
CREATE OR REPLACE VIEW "public"."v_top_scored_jobs_by_profile" AS
SELECT
    pjs.profile_id,
    up.name as profile_name,
    up.email as profile_email,
    j.job_id,
    j.company,
    j.job_title,
    j.location,
    j.level,
    pjs.profile_score,
    pjs.profile_match_reason,
    pjs.career_fit,
    pjs.skills_fit,
    pjs.seniority_fit,
    pjs.location_fit,
    pjs.culture_fit,
    pjs.should_apply,
    pjs.scored_at,
    up.profile_score_threshold
FROM
    "public"."profile_job_scores" pjs
INNER JOIN
    "public"."user_profiles" up ON pjs.profile_id = up.id
INNER JOIN
    "public"."jobs" j ON pjs.job_id = j.job_id
WHERE
    j.is_active = TRUE
ORDER BY
    pjs.profile_id,
    pjs.profile_score DESC NULLS LAST;

COMMENT ON VIEW "public"."v_top_scored_jobs_by_profile" IS 'Top scored jobs for each profile, sorted by score';

-- View 2: Scoring statistics per profile
CREATE OR REPLACE VIEW "public"."v_profile_scoring_stats" AS
SELECT
    up.id as profile_id,
    up.name as profile_name,
    up.email as profile_email,
    COUNT(DISTINCT pjs.job_id) as total_scored_jobs,
    COUNT(DISTINCT CASE WHEN pjs.profile_score >= up.profile_score_threshold THEN pjs.job_id END) as above_threshold_jobs,
    COUNT(DISTINCT CASE WHEN pjs.should_apply THEN pjs.job_id END) as recommended_jobs,
    ROUND(AVG(pjs.profile_score)::numeric, 2) as avg_score,
    MAX(pjs.profile_score) as highest_score,
    MIN(pjs.profile_score) as lowest_score,
    MAX(pjs.scored_at) as last_scored_at
FROM
    "public"."user_profiles" up
LEFT JOIN
    "public"."profile_job_scores" pjs ON up.id = pjs.profile_id
WHERE
    up.is_active = TRUE
GROUP BY
    up.id,
    up.name,
    up.email,
    up.profile_score_threshold;

COMMENT ON VIEW "public"."v_profile_scoring_stats" IS 'Scoring statistics for each user profile (avg, max, min scores, etc)';

-- View 3: Jobs with scores from all profiles (for analytics)
CREATE OR REPLACE VIEW "public"."v_job_scoring_across_profiles" AS
SELECT
    j.job_id,
    j.company,
    j.job_title,
    j.location,
    COUNT(DISTINCT pjs.profile_id) as num_profiles_scored,
    COUNT(DISTINCT CASE WHEN pjs.should_apply THEN pjs.profile_id END) as num_should_apply,
    ROUND(AVG(pjs.profile_score)::numeric, 2) as avg_score_all_profiles,
    MAX(pjs.profile_score) as highest_score,
    MIN(pjs.profile_score) as lowest_score,
    MAX(pjs.scored_at) as last_scored_at
FROM
    "public"."jobs" j
LEFT JOIN
    "public"."profile_job_scores" pjs ON j.job_id = pjs.job_id
WHERE
    j.is_active = TRUE
GROUP BY
    j.job_id,
    j.company,
    j.job_title,
    j.location;

COMMENT ON VIEW "public"."v_job_scoring_across_profiles" IS 'How each job performed across all profiles (useful for analytics)';

-- =========================================================
-- STEP 5: Grant permissions
-- =========================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON "public"."profile_job_scores" TO "authenticated";
GRANT SELECT, INSERT, UPDATE, DELETE ON "public"."profile_job_scores" TO "service_role";

GRANT SELECT ON "public"."v_top_scored_jobs_by_profile" TO "authenticated";
GRANT SELECT ON "public"."v_top_scored_jobs_by_profile" TO "service_role";

GRANT SELECT ON "public"."v_profile_scoring_stats" TO "authenticated";
GRANT SELECT ON "public"."v_profile_scoring_stats" TO "service_role";

GRANT SELECT ON "public"."v_job_scoring_across_profiles" TO "authenticated";
GRANT SELECT ON "public"."v_job_scoring_across_profiles" TO "service_role";

-- =========================================================
-- STEP 6: Ensure user_profiles has required fields
-- =========================================================
ALTER TABLE "public"."user_profiles"
ADD COLUMN IF NOT EXISTS "career_goals" TEXT DEFAULT 'Professional growth and skill development',
ADD COLUMN IF NOT EXISTS "preferred_company_size" TEXT DEFAULT 'Any',
ADD COLUMN IF NOT EXISTS "red_flag_keywords" TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "min_skill_match_percentage" INTEGER DEFAULT 60 CHECK (min_skill_match_percentage >= 0 AND min_skill_match_percentage <= 100),
ADD COLUMN IF NOT EXISTS "profile_score_threshold" INTEGER DEFAULT 70 CHECK (profile_score_threshold >= 0 AND profile_score_threshold <= 100);

COMMENT ON COLUMN "public"."user_profiles"."career_goals" IS 'User''s career objectives and goals for next role';
COMMENT ON COLUMN "public"."user_profiles"."preferred_company_size" IS 'Preferred company size: Startup, SMB, Mid-size, Enterprise, Any';
COMMENT ON COLUMN "public"."user_profiles"."red_flag_keywords" IS 'Job description keywords to avoid (e.g., unpaid, equity only)';
COMMENT ON COLUMN "public"."user_profiles"."min_skill_match_percentage" IS 'Minimum percentage of preferred skills that should match (0-100)';
COMMENT ON COLUMN "public"."user_profiles"."profile_score_threshold" IS 'Minimum profile score to recommend a job (0-100)';

-- =========================================================
-- STEP 7: Add RLS (Row Level Security) policies
-- =========================================================

-- Enable RLS on profile_job_scores
ALTER TABLE "public"."profile_job_scores" ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see scores for their own profile
-- Policy 1: Users can view their own profile job scores
DROP POLICY IF EXISTS "Users can view their own profile job scores"
ON "public"."profile_job_scores";

CREATE POLICY "Users can view their own profile job scores"
ON "public"."profile_job_scores"
FOR SELECT
USING (
    auth.uid()::text = profile_id::text
    OR EXISTS (
        SELECT 1 FROM "public"."user_profiles"
        WHERE id = profile_id AND auth.uid()::text = id::text
    )
);

-- Policy 2: Service role can manage all scores
DROP POLICY IF EXISTS "Service role can manage all profile job scores"
ON "public"."profile_job_scores";

CREATE POLICY "Service role can manage all profile job scores"
ON "public"."profile_job_scores"
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');


