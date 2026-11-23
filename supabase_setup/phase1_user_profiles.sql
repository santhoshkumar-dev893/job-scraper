CREATE TABLE IF NOT EXISTS "public"."user_profiles" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL PRIMARY KEY,
    
    -- Basic Profile Information
    "name" "text" NOT NULL,
    "email" "text",
    "phone" "text",
    "current_location" "text",
    "timezone" "text",
    
    -- Career Preferences
    "target_job_titles" "text"[] DEFAULT '{}'::text[],  -- Array of target job titles
    "target_companies" "text"[] DEFAULT '{}'::text[],   -- Array of preferred companies
    "willing_locations" "text"[] DEFAULT '{}'::text[],  -- Array of acceptable locations
    "willing_remote_level" "text" DEFAULT 'hybrid',     -- remote, hybrid, onsite, any
    
    -- Experience & Level
    "years_of_experience" smallint DEFAULT 0,
    "current_level" "text" DEFAULT 'mid',               -- entry, mid, senior, lead, executive
    "target_level" "text" DEFAULT 'mid',                -- entry, mid, senior, lead, executive
    
    -- Skills & Technologies
    "primary_skills" "text"[] DEFAULT '{}'::text[],     -- Core technical skills
    "secondary_skills" "text"[] DEFAULT '{}'::text[],   -- Nice-to-have skills
    "must_have_skills" "text"[] DEFAULT '{}'::text[],   -- Skills that are required
    "avoid_skills" "text"[] DEFAULT '{}'::text[],       -- Skills to avoid
    
    -- Job Preferences
    "job_type_preference" "text"[] DEFAULT '{Full Time}'::text[],  -- Full Time, Contract, Part-time, etc
    "min_salary" integer DEFAULT 0,                     -- Minimum acceptable salary (0 = no minimum)
    "currency" "text" DEFAULT 'USD',
    
    -- Company Preferences
    "company_size_preference" "text"[] DEFAULT '{}'::text[],  -- Startup, SMB, Enterprise, etc
    "industry_preferences" "text"[] DEFAULT '{}'::text[],     -- Preferred industries
    "avoid_industries" "text"[] DEFAULT '{}'::text[],         -- Industries to avoid
    "exclude_companies" "text"[] DEFAULT '{}'::text[],        -- Companies to exclude
    
    -- Work Style & Benefits
    "work_culture_keywords" "text"[] DEFAULT '{}'::text[],     -- Innovation, Collaboration, etc
    "benefits_importance" "text"[] DEFAULT '{}'::text[],       -- Health insurance, 401k, etc
    "willing_relocation" boolean DEFAULT false,
    "willing_travel" boolean DEFAULT false,
    
    -- Profile Settings
    "is_active" boolean DEFAULT true,
    "auto_filter_enabled" boolean DEFAULT true,         -- Whether to auto-filter jobs using this profile
    "profile_score_threshold" smallint DEFAULT 70,      -- Minimum profile score to match
    
    -- Timestamps
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "last_used_at" timestamp with time zone,
    
    -- Metadata
    "notes" "text",
    "form_stage" "text" DEFAULT 'basic_info'             -- Track where user is in form (for multi-step forms)
);

ALTER TABLE "public"."user_profiles" OWNER TO "postgres";

COMMENT ON TABLE "public"."user_profiles" IS 'Stores user career preferences and profile information for job filtering';
COMMENT ON COLUMN "public"."user_profiles"."target_job_titles" IS 'Array of job titles the user is interested in';
COMMENT ON COLUMN "public"."user_profiles"."willing_remote_level" IS 'Remote work preference: remote, hybrid, onsite, any';
COMMENT ON COLUMN "public"."user_profiles"."current_level" IS 'Current professional level: entry, mid, senior, lead, executive';
COMMENT ON COLUMN "public"."user_profiles"."target_level" IS 'Target professional level for growth';
COMMENT ON COLUMN "public"."user_profiles"."must_have_skills" IS 'Skills that must be present in job description';
COMMENT ON COLUMN "public"."user_profiles"."profile_score_threshold" IS 'Minimum profile match score (0-100) for job recommendations';
COMMENT ON COLUMN "public"."user_profiles"."form_stage" IS 'Current stage in multi-step form: basic_info, experience, skills, preferences, review';

-- =====================================================================
-- 2. ALTER jobs TABLE - ADD PROFILE RELATIONSHIP COLUMNS
-- =====================================================================

-- Add profile_id column (foreign key to user_profiles)
ALTER TABLE "public"."jobs" 
ADD COLUMN IF NOT EXISTS "profile_id" "uuid",
ADD COLUMN IF NOT EXISTS "profile_score" smallint,
ADD COLUMN IF NOT EXISTS "profile_filter_reason" "text",
ADD COLUMN IF NOT EXISTS "profile_filter_timestamp" timestamp with time zone;

-- Add comments for new columns
COMMENT ON COLUMN "public"."jobs"."profile_id" IS 'Foreign key to user_profiles table for profile-based filtering';
COMMENT ON COLUMN "public"."jobs"."profile_score" IS 'Score (0-100) indicating match with user profile, NULL if not evaluated';
COMMENT ON COLUMN "public"."jobs"."profile_filter_reason" IS 'Reason if job was filtered out by profile matching (e.g., "No matching skills", "Location mismatch")';
COMMENT ON COLUMN "public"."jobs"."profile_filter_timestamp" IS 'Timestamp when profile scoring was performed';

-- Add foreign key constraint
ALTER TABLE "public"."jobs"
ADD CONSTRAINT "jobs_profile_id_fkey" 
FOREIGN KEY ("profile_id") 
REFERENCES "public"."user_profiles"("id") 
ON UPDATE CASCADE 
ON DELETE SET NULL;

-- =====================================================================
-- 3. CREATE INDEXES FOR PERFORMANCE
-- =====================================================================

-- Index on user_profiles for common queries
CREATE INDEX IF NOT EXISTS "idx_user_profiles_active" ON "public"."user_profiles"("is_active", "created_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_user_profiles_email" ON "public"."user_profiles"("email");

-- Index on jobs for profile-based queries
CREATE INDEX IF NOT EXISTS "idx_jobs_profile_id" ON "public"."jobs"("profile_id");
CREATE INDEX IF NOT EXISTS "idx_jobs_profile_score" ON "public"."jobs"("profile_id", "profile_score" DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS "idx_jobs_profile_filter" ON "public"."jobs"("profile_id", "profile_filter_reason");

-- =====================================================================
-- 4. CREATE AUTO-UPDATE TRIGGER FOR user_profiles.updated_at
-- =====================================================================

CREATE OR REPLACE FUNCTION "public"."update_user_profiles_updated_at"()
RETURNS "trigger" AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE "plpgsql";

ALTER FUNCTION "public"."update_user_profiles_updated_at"() OWNER TO "postgres";

CREATE OR REPLACE TRIGGER "update_user_profiles_updated_at_trigger"
BEFORE UPDATE ON "public"."user_profiles"
FOR EACH ROW
EXECUTE FUNCTION "public"."update_user_profiles_updated_at"();

-- =====================================================================
-- 5. ENABLE RLS & GRANT PERMISSIONS
-- =====================================================================

ALTER TABLE "public"."user_profiles" ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Allow service_role full access
CREATE POLICY "Allow service_role full access on user_profiles" ON "public"."user_profiles"
    FOR ALL USING (TRUE) WITH CHECK (TRUE);

-- Grant permissions
GRANT ALL ON TABLE "public"."user_profiles" TO "anon";
GRANT ALL ON TABLE "public"."user_profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."user_profiles" TO "service_role";

-- =====================================================================
-- 6. CREATE HELPER FUNCTIONS
-- =====================================================================

-- Function to get user profile by email
CREATE OR REPLACE FUNCTION "public"."get_user_profile_by_email"(p_email "text")
RETURNS TABLE (
    "id" "uuid",
    "name" "text",
    "target_job_titles" "text"[],
    "target_companies" "text"[],
    "willing_locations" "text"[],
    "willing_remote_level" "text",
    "primary_skills" "text"[],
    "must_have_skills" "text"[],
    "current_level" "text",
    "target_level" "text",
    "years_of_experience" smallint,
    "exclude_companies" "text"[],
    "avoid_industries" "text"[],
    "avoid_skills" "text"[],
    "profile_score_threshold" smallint,
    "auto_filter_enabled" boolean
)
LANGUAGE "plpgsql"
AS $$
BEGIN
    RETURN QUERY
    SELECT
        up.id,
        up.name,
        up.target_job_titles,
        up.target_companies,
        up.willing_locations,
        up.willing_remote_level,
        up.primary_skills,
        up.must_have_skills,
        up.current_level,
        up.target_level,
        up.years_of_experience,
        up.exclude_companies,
        up.avoid_industries,
        up.avoid_skills,
        up.profile_score_threshold,
        up.auto_filter_enabled
    FROM
        "public"."user_profiles" up
    WHERE
        up.email = p_email
        AND up.is_active = TRUE
    LIMIT 1;
END;
$$;

ALTER FUNCTION "public"."get_user_profile_by_email"(p_email "text") OWNER TO "postgres";

-- =====================================================================
-- 7. SAMPLE DATA (Optional - For Testing)
-- =====================================================================
-- Uncomment to insert sample profile for testing
/*
INSERT INTO "public"."user_profiles" (
    name,
    email,
    current_location,
    target_job_titles,
    target_companies,
    willing_locations,
    willing_remote_level,
    years_of_experience,
    current_level,
    target_level,
    primary_skills,
    must_have_skills,
    job_type_preference,
    industry_preferences,
    profile_score_threshold,
    auto_filter_enabled
) VALUES (
    'John Doe',
    'john@example.com',
    'India',
    ARRAY['Software Engineer', 'Senior Software Engineer', 'Full Stack Engineer'],
    ARRAY['Google', 'Microsoft', 'Amazon', 'Meta'],
    ARRAY['India', 'Singapore', 'USA'],
    'hybrid',
    5,
    'mid',
    'senior',
    ARRAY['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS'],
    ARRAY['Python', 'JavaScript'],
    ARRAY['Full Time'],
    ARRAY['Technology', 'SaaS', 'FinTech'],
    70,
    true
);
*/

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON FUNCTION "public"."get_user_profile_by_email"("text") TO "anon";
GRANT ALL ON FUNCTION "public"."get_user_profile_by_email"("text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_user_profile_by_email"("text") TO "service_role";
