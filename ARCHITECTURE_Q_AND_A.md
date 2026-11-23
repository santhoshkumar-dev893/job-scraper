# Two Critical Architecture Questions & Solutions

**Document Date:** 11 November 2026  
**Status:** ANSWERED WITH SOLUTIONS

---

## Question 1: What if Heuristic Has Limited Skills?

### The Problem

**Current Scenario:**
- Spacy heuristic extractor loads skills from `SkillManager` (database)
- If the database has only 100 core skills, only those 100 will be matched
- If job description mentions a skill NOT in database (e.g., "Kubernetes" if not seeded), it won't be found
- Result: Missing skills → Lower match scores → Users miss good job opportunities

**Example Flow:**
```
Job Description: "Require 5+ years Python, Docker, and Kubernetes experience"
Database Skills: [Python, Docker, AWS, Azure, ...]
Missing: Kubernetes

Spacy Extract: [Python, Docker]  ❌ Kubernetes is lost!
LLM Extract: [Python, Docker, Kubernetes]  ✅ But LLM is expensive
```

### Solution 1A: Dual Extraction (Current Best Practice)

**How it works:**

1. **Stage 1: Heuristic Extraction (Fast, Free)**
   - Spacy matches only against database skills
   - Returns matched skills with 100% confidence

2. **Stage 2: Check Match Quality**
   - If match score ≥ threshold → Good match, return results
   - If match score < threshold → Poor match, need fallback

3. **Stage 3: LLM Fallback (Smart Cost Control)**
   - LLM extracts skills from job description
   - Gets both known AND unknown skills
   - Especially good at finding new/emerging technologies

4. **Stage 4: Merge Results**
   - Combine heuristic + LLM skills
   - LLM finds what heuristic missed
   - Score = higher confidence

5. **Stage 5: Discover & Insert New Skills**
   - New skills found by LLM go to database
   - Next job will use them in heuristic extraction
   - Progressive learning: database grows smarter over time

**Code Location:** `job_scorer.py` → `score_job()` method

```python
# Stage 1: Heuristic extraction
heuristic_skills = self.spacy_extractor.extract(cleaned_description)
heuristic_score = self._score_skills(
    heuristic_skills,
    self.profile.skills,
    self.skill_manager
)

# Stage 2: Check if we need LLM fallback
if heuristic_score.match_percentage < DEFAULT_ATS_THRESHOLD:
    # Stage 3: LLM extraction (fallback)
    llm_result = self.llm_extractor.extract(
        cleaned_description,
        known_skills=self.skill_manager.get_all_skills()
    )
    
    if llm_result.status in {"ok", "partial"}:
        # Stage 4: Discover new skills via SkillDiscovery
        discovered_skills = extract_discovered_skills_from_llm_output(llm_result)
        
        if discovered_skills and self.skill_discovery:
            # Stage 5: Insert to database for future use
            discovery_result = self.skill_discovery.discover_skills(
                discovered_skills,
                job_id=job_id
            )
```

### Solution 1B: Continuous Database Growth (Long-term Strategy)

**Strategy:**
- Every new skill discovered by LLM gets inserted into database
- Database starts with ~200 core skills
- After processing 1000 jobs:
  - Database might have 300-500 skills
  - Heuristic extraction becomes more effective
  - LLM fallback needed less frequently
  - Cost reduces over time

**Timeline Example:**
| Jobs | DB Skills | Heuristic Match Rate | LLM Used | Cost Trend |
|------|-----------|----------------------|----------|-----------|
| 0 | 200 | 60% | Always | High |
| 100 | 250 | 65% | Always | High |
| 500 | 350 | 75% | 80% of time | Medium-High |
| 1000 | 450 | 82% | 60% of time | Medium |
| 5000 | 650+ | 90%+ | 20-30% of time | Low |

**Implementation:** Already built into `SkillDiscovery.discover_skills()` and `skill_discovery.py`

---

## Question 2: Database Only Has INSERT Permission (No READ)

### The Problem

**Current RLS Policy:**
```sql
CREATE POLICY "allow_insert_service_role"
  ON skills
  FOR INSERT
  WITH CHECK (auth.uid() = auth.uid() OR auth.role() = 'service_role')
  USING (true);
```

**Issue:** Service role can only INSERT, not SELECT/READ
- SkillManager calls `SELECT * FROM skills` to load cache
- This will FAIL if RLS blocks reads

### Solution 2A: Modify RLS Policy to Allow Both READ + INSERT

**Why it's necessary:**
- SkillManager must READ to load cache at startup
- SkillDiscovery must READ to check if skill exists
- SpacySkillExtractor must READ to get all skills
- These are all internal backend operations, not user-facing

**Recommended RLS Policy:**

```sql
-- Drop old policy (insert-only)
DROP POLICY IF EXISTS "allow_insert_service_role" ON skills;

-- New policy: Allow service role to read AND insert (backend operations)
CREATE POLICY "service_role_full_access"
  ON skills
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Optional: Restrict user SELECT (if you want users to read through API endpoint)
CREATE POLICY "users_cannot_access"
  ON skills
  FOR ALL
  USING (auth.uid() = 'system-user-only-placeholder')
  WITH CHECK (auth.uid() = 'system-user-only-placeholder');
```

**What this does:**
- Service role: Full access (READ, INSERT, UPDATE, DELETE)
- Regular users: No direct access (must go through API endpoints)
- Audit trail: All changes tracked via `created_at`, `updated_at`, `source_job_id`

**Apply this with:**
```bash
psql -h <PROJECT_ID>.supabase.co -U postgres -d postgres -f update_skills_rls.sql
```

### Solution 2B: If You MUST Keep INSERT-Only RLS

**If your security requirements absolutely forbid READ on service role:**

**Alternative: Create a dedicated SERVICE ROLE table**

```sql
-- Separate cache table that service role can read
CREATE TABLE skills_cache (
    skill_name TEXT PRIMARY KEY,
    skill_id UUID,
    requirement TEXT,
    tags TEXT[],
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Service role can read this table
CREATE POLICY "service_role_read_cache"
  ON skills_cache
  FOR SELECT
  USING (auth.role() = 'service_role');

-- Separate table for writes (original)
CREATE POLICY "service_role_write_skills"
  ON skills
  FOR INSERT
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Trigger: When skill is inserted, update cache
CREATE OR REPLACE FUNCTION sync_skills_to_cache()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO skills_cache (skill_name, skill_id, requirement, tags)
    VALUES (NEW.skill_name, NEW.id, NEW.requirement, NEW.tags)
    ON CONFLICT (skill_name) DO UPDATE SET
        skill_id = EXCLUDED.skill_id,
        requirement = EXCLUDED.requirement,
        tags = EXCLUDED.tags,
        last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_skill_insert
AFTER INSERT ON skills
FOR EACH ROW
EXECUTE FUNCTION sync_skills_to_cache();
```

**Pros:**
- Maintains strict INSERT-only on original table
- Service role can read cache for internal operations
- Audit trail still on original table
- Separate concerns: writes vs reads

**Cons:**
- More complex (requires trigger maintenance)
- Extra table = extra storage
- Slight delay before cache is synced

### Solution 2C: Use Materialized View (Recommended Middle Ground)

**Best compromise: Secure yet practical**

```sql
-- Materialized view: Read-only snapshot for internal use
CREATE MATERIALIZED VIEW skills_for_service_role AS
SELECT 
    id,
    skill_name,
    requirement,
    tags,
    confidence_score,
    created_at
FROM skills
WHERE 1=1;  -- All records, but read-only

-- Index for performance
CREATE INDEX idx_skills_view_name ON skills_for_service_role(skill_name);

-- Service role can select from materialized view
CREATE POLICY "service_role_read_view"
  ON skills_for_service_role
  FOR SELECT
  USING (auth.role() = 'service_role');

-- Original table: insert-only
CREATE POLICY "service_role_write_skills"
  ON skills
  FOR INSERT
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Refresh view after inserts
CREATE OR REPLACE FUNCTION refresh_skills_view()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY skills_for_service_role;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_skill_insert_refresh
AFTER INSERT ON skills
FOR EACH ROW
EXECUTE FUNCTION refresh_skills_view();
```

**Advantages:**
- Clear security boundary
- Read-only for service role (can't accidentally update)
- Trigger keeps it fresh
- Performance: indexed materialized view

---

## Recommended Architecture Decision

### Current State (Minimum Change)
**Update RLS to allow READ:**
- Simplest solution
- Only 2 policies needed
- No extra tables/views
- Service role is internal backend → safe to allow READ
- **Time to implement:** 5 minutes

```sql
-- Single policy for service role
CREATE POLICY "service_role_backend_operations"
  ON skills
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
```

### Best Practice (Production Recommendation)
**Use Materialized View + Triggers:**
- Clear separation: INSERT on table, SELECT on view
- Audit trail on original table
- Reduced risk of accidental writes
- Performance optimized
- **Time to implement:** 15 minutes

---

## Implementation Checklist

### Step 1: Choose Your Approach

```
Option A: Modify RLS Policy (RECOMMENDED - Minimum)
  ☐ Remove INSERT-only RLS
  ☐ Add policy allowing READ + INSERT for service role
  ☐ Test: SkillManager.refresh_cache() works
  ☐ Test: SkillDiscovery.has_skill() works
  ☐ Time: 5 min
  
Option B: Materialized View (RECOMMENDED - Production)
  ☐ Create materialized view
  ☐ Create trigger for refresh
  ☐ Update SkillManager to query view
  ☐ Test all operations
  ☐ Time: 15 min

Option C: Separate Cache Table (Complex)
  ☐ Create new table
  ☐ Create trigger to sync
  ☐ Update SkillManager
  ☐ Manage cache eviction
  ☐ Time: 20+ min
```

### Step 2: Update Code if Needed

If using materialized view:

```python
# In skills_manager.py, change query:

# Before:
response = self.supabase.table("skills").select(...)

# After (if using view):
response = self.supabase.table("skills_for_service_role").select(...)
```

### Step 3: Test

```python
# Test script
from skills_manager import SkillManager
from supabase import create_client

supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

manager = SkillManager(supabase)
print(f"✅ Loaded {len(manager.get_all_skills())} skills")

# Should not error if RLS is correct
assert manager.has_skill("python")
assert manager.has_skill("docker")
print("✅ All RLS permissions working correctly")
```

---

## Complete Flow with Proper RLS

```
┌──────────────────────────────────────────────────────────────┐
│ Startup: Initialize SkillManager                             │
│  - Creates Supabase client with SERVICE_ROLE_KEY             │
│  - Calls refresh_cache()                                     │
│  - RLS check: auth.role() = 'service_role' ✅ ALLOWS SELECT  │
│  - Loads 200+ skills into memory cache                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ Processing Job #1                                            │
│  - Spacy extracts skills using cached list                   │
│  - Score matches, returns results ✅                         │
│  - No LLM needed                                             │
└────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ Processing Job #2 (New Skill Found)                          │
│  - Spacy finds Python, Docker                               │
│  - Score too low, triggers LLM fallback                      │
│  - LLM finds: Python, Docker, Kubernetes (NEW!)              │
│  - SkillDiscovery.discover_skills([Kubernetes])              │
│    - Calls has_skill("kubernetes")                           │
│    - RLS check: auth.role() = 'service_role' ✅ SELECT OK    │
│    - Skill not found in cache                               │
│    - Inserts into database                                   │
│    - RLS check: auth.role() = 'service_role' ✅ INSERT OK    │
│    - Updates SkillManager cache                              │
└────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ Next Cycle (~100 jobs later)                                 │
│  - Calls refresh_cache()                                     │
│  - Kubernetes now in database ✅                             │
│  - Spacy can match it in future jobs                         │
│  - Cost savings: LLM used less frequently                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Security Notes

### Why This is Safe

1. **Service Role is Internal Backend Only**
   - Not exposed to frontend
   - Not in environment of users
   - Only used server-side during job processing

2. **RLS Policies Protect Data**
   - Users still cannot access skills table directly
   - They access through API endpoints only
   - API layer can add additional validation

3. **Audit Trail is Maintained**
   - `source_job_id`, `created_at`, `updated_at` track changes
   - Admins can see where each skill came from
   - Can revert or flag suspicious entries

### Multi-Tenant Isolation (If Needed)

If you have multiple users/orgs:

```sql
ALTER TABLE skills ADD COLUMN organization_id UUID;

-- RLS policy: Users only see their org's skills
CREATE POLICY "users_see_own_org_skills"
  ON skills
  FOR SELECT
  USING (
    organization_id = (
      SELECT organization_id FROM profiles 
      WHERE id = auth.uid()
    )
  );

-- Service role can insert for any org
CREATE POLICY "service_role_insert_any_org"
  ON skills
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');
```

---

## Final Recommendation

**Do this NOW (takes 5 minutes):**

```sql
-- Update to allow READ for service role
DROP POLICY IF EXISTS "allow_insert_service_role" ON skills;

CREATE POLICY "service_role_read_write"
  ON skills
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Regular users: no direct access
CREATE POLICY "block_user_direct_access"
  ON skills
  FOR ALL
  USING (false);
```

**Test immediately:**

```bash
cd /Users/santhosh-16982/my_job_agent/job-scraper
python -c "
from skills_manager import SkillManager
from supabase import create_client
import os

client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)
manager = SkillManager(client)
print(f'✅ Loaded {len(manager.get_all_skills())} skills')
"
```

If this works, your RLS is correct! If not, check the SQL and reapply policies.

---

## References

- **SkillManager:** `/skills_manager.py` (uses SELECT)
- **SkillDiscovery:** `/skill_discovery.py` (uses SELECT + INSERT)
- **SpacyExtractor:** `/spacy_extractor.py` (uses cache from SkillManager)
- **Current RLS:** `/supabase_setup/create_skills_table.sql`
- **Job Scorer:** `/job_scorer.py` (orchestrates everything)

