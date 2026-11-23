-- Phase 2: Profile-Level Scoring Only
-- Remove resume-related columns and add profile scoring columns

-- Drop columns that are no longer needed (resume-related)
ALTER TABLE "public"."jobs"
DROP COLUMN IF EXISTS "resume_score" CASCADE,
DROP COLUMN IF EXISTS "resume_score_stage" CASCADE;

-- Add columns for profile-level scoring
ALTER TABLE "public"."jobs"
ADD COLUMN IF NOT EXISTS "profile_id" "uuid" REFERENCES "public"."user_profiles"("id") ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS "profile_score" "smallint" CHECK (profile_score >= 0 AND profile_score <= 100),
ADD COLUMN IF NOT EXISTS "profile_match_reason" "text",
ADD COLUMN IF NOT EXISTS "scored_at" timestamp with time zone;

-- Add comment for clarity
COMMENT ON COLUMN "public"."jobs"."profile_id" IS 'Reference to the user profile this job was scored against';
COMMENT ON COLUMN "public"."jobs"."profile_score" IS 'Score 0-100 indicating how well this job fits the user profile';
COMMENT ON COLUMN "public"."jobs"."profile_match_reason" IS 'Explanation from LLM of why this score was given';
COMMENT ON COLUMN "public"."jobs"."scored_at" IS 'Timestamp when the job was scored against the profile';

-- Create index on profile_score for faster queries
CREATE INDEX IF NOT EXISTS "idx_jobs_profile_score" ON "public"."jobs" ("profile_id", "profile_score" DESC NULLS LAST);

-- Create index on profile_id for faster lookups
CREATE INDEX IF NOT EXISTS "idx_jobs_profile_id" ON "public"."jobs" ("profile_id");

-- Ensure jobs table has proper permissions for profile scoring
GRANT SELECT, UPDATE ON TABLE "public"."jobs" TO "service_role";

-- Optional: Create a view for top scored jobs
CREATE OR REPLACE VIEW "public"."v_top_profile_scored_jobs" AS
SELECT
    j.job_id,
    j.profile_id,
    j.company,
    j.job_title,
    j.location,
    j.level,
    j.profile_score,
    j.profile_match_reason,
    j.scraped_at,
    j.scored_at,
    up.profile_score_threshold
FROM
    jobs j
INNER JOIN
    user_profiles up ON j.profile_id = up.id
WHERE
    j.profile_score IS NOT NULL
    AND j.is_active = TRUE
ORDER BY
    j.profile_id,
    j.profile_score DESC NULLS LAST;

-- Create a summary stats view
CREATE OR REPLACE VIEW "public"."v_profile_scoring_stats" AS
SELECT
    up.id as profile_id,
    up.name,
    COUNT(j.job_id) as total_jobs,
    COUNT(CASE WHEN j.profile_score IS NOT NULL THEN 1 END) as scored_jobs,
    COUNT(CASE WHEN j.profile_score IS NULL THEN 1 END) as unscored_jobs,
    ROUND(AVG(j.profile_score)::numeric, 2) as avg_score,
    MAX(j.profile_score) as highest_score,
    MIN(j.profile_score) as lowest_score,
    COUNT(CASE WHEN j.profile_score >= up.profile_score_threshold THEN 1 END) as above_threshold,
    MAX(j.scored_at) as last_scored_at
FROM
    user_profiles up
LEFT JOIN
    jobs j ON up.id = j.profile_id AND j.is_active = TRUE
GROUP BY
    up.id,
    up.name,
    up.profile_score_threshold;

-- Grant permissions on views
GRANT SELECT ON "public"."v_top_profile_scored_jobs" TO "authenticated";
GRANT SELECT ON "public"."v_top_profile_scored_jobs" TO "service_role";
GRANT SELECT ON "public"."v_profile_scoring_stats" TO "authenticated";
GRANT SELECT ON "public"."v_profile_scoring_stats" TO "service_role";

-- Optional: Backup old data if needed
-- You can uncomment this if you want to keep resume_score data before dropping
-- ALTER TABLE "public"."jobs" RENAME COLUMN "resume_score" TO "resume_score_backup";
-- ALTER TABLE "public"."jobs" RENAME COLUMN "resume_score_stage" TO "resume_score_stage_backup";

-- Update user_profiles table to ensure we have career goals fields
ALTER TABLE "public"."user_profiles"
ADD COLUMN IF NOT EXISTS "career_goals" "text" DEFAULT 'Professional growth and skill development',
ADD COLUMN IF NOT EXISTS "preferred_company_size" "text" DEFAULT 'Any',
ADD COLUMN IF NOT EXISTS "red_flag_keywords" "text[]" DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "min_skill_match_percentage" "integer" DEFAULT 60 CHECK (min_skill_match_percentage >= 0 AND min_skill_match_percentage <= 100);

COMMENT ON COLUMN "public"."user_profiles"."career_goals" IS 'User''s career objectives and goals for next role';
COMMENT ON COLUMN "public"."user_profiles"."preferred_company_size" IS 'Preferred company size: Startup, SMB, Mid-size, Enterprise, Any';
COMMENT ON COLUMN "public"."user_profiles"."red_flag_keywords" IS 'Job description keywords to avoid (e.g., unpaid, equity only)';
COMMENT ON COLUMN "public"."user_profiles"."min_skill_match_percentage" IS 'Minimum percentage of preferred skills that should match (0-100)';
