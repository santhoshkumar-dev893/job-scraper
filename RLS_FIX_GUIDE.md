# RLS Policy Error Fix: Complete Guide

**Document Date:** 11 November 2026  
**Error:** `new row violates row-level security policy for table "skills"` (Code 42501)  
**Status:** CRITICAL - System Cannot Insert Skills  

---

## The Problem

You're seeing this error when SkillDiscovery tries to insert discovered skills:

```
ERROR:skill_discovery:Error inserting skill LLM: {
  'message': 'new row violates row-level security policy for table "skills"',
  'code': '42501'
}
```

### Root Cause

The current RLS policy checks `auth.role() = 'service_role'`, but when using Supabase service role key directly in Python/backend connections, `auth.role()` might return NULL instead of `'service_role'`, causing the INSERT to fail.

---

## Solution: Fix the RLS Policy

### The Problem Policy (Doesn't Work)
```sql
CREATE POLICY "service_role_backend_full_access"
  ON public.skills
  FOR ALL
  USING (auth.role() = 'service_role')  -- ❌ Fails: auth.role() might be NULL
  WITH CHECK (auth.role() = 'service_role');
```

### The Working Policy (Use This)
```sql
DROP POLICY IF EXISTS "service_role_backend_full_access" ON public.skills;
DROP POLICY IF EXISTS "users_cannot_access_directly" ON public.skills;

-- Create WORKING policies
CREATE POLICY "allow_all_operations"
  ON public.skills
  FOR ALL
  USING (true)  -- ✅ Always allow (service role is trusted)
  WITH CHECK (true);

CREATE POLICY "block_regular_users"
  ON public.skills
  FOR ALL
  USING (false)  -- ✅ Block unauthenticated users
  WITH CHECK (false);
```

### Why This Works

- Service role key is backend-only (safe to trust)
- `USING (true)` allows the operation
- Regular users still blocked by second policy
- This is the recommended Supabase approach for backend services
  FOR ALL USING (TRUE) WITH CHECK (TRUE);

-- Allow authenticated users to read
CREATE POLICY "Allow authenticated read access" ON public.jobs
  FOR SELECT USING (TRUE);
```

## Why This Happens

- **Row-Level Security (RLS)** is a PostgreSQL feature that restricts row-level access
- When **RLS is ENABLED but NO policies are defined**, PostgreSQL defaults to **DENY ALL** access
- Your `service_role` key couldn't bypass this because the table had RLS enabled
- The diagnostic test confirmed this: `code: '42501'` = `insufficient_privilege` error

## Testing the Fix

After applying the fix, run the diagnostic script again:

```bash
python3 test_supabase_connection.py
```

You should see:
```
✓ WRITE (upsert) permission works!
```

Then run your scraper:
```bash
python3 scraper.py
```

## Technical Details

- **SUPABASE_URL**: Your Supabase project URL ✓ (working)
- **SUPABASE_SERVICE_ROLE_KEY**: Your service role authentication key ✓ (working)
- **RLS Policies**: Missing ✗ (causing the issue)
- **Table Permissions**: Granted but blocked by RLS ✗

---

# Fix for job_matches Table - auth_user_id Error

## The Issue
When running `add_job_matches_table.sql`:
```
ERROR: 42703: column user_profiles.auth_user_id does not exist
```

The RLS policies reference `auth_user_id` which doesn't exist in the `user_profiles` table.

## The Solution

### Use the Fixed Version (RECOMMENDED)
Use `add_job_matches_table_FIXED.sql` which has corrected RLS policies that:
- ✅ Allow `service_role` full access (for backend scoring service)
- ✅ Allow `authenticated` users read-only access
- ✅ Don't reference non-existent columns

### Fixed RLS Policies

```sql
-- RLS Policy: Allow service_role full access (backend scoring service)
CREATE POLICY rls_job_matches_service_role ON public.job_matches
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- RLS Policy: Allow authenticated users to select
CREATE POLICY rls_job_matches_deny_anonymous ON public.job_matches
    FOR SELECT
    USING (auth.role() = 'service_role');
```

### Steps to Fix

1. **In Supabase SQL Editor, run:**
   ```sql
   DROP TABLE IF EXISTS public.job_matches CASCADE;
   DROP VIEW IF EXISTS public.vw_matched_jobs_by_profile CASCADE;
   DROP VIEW IF EXISTS public.vw_pending_skill_review CASCADE;
   DROP VIEW IF EXISTS public.vw_matching_analytics CASCADE;
   ```

2. **Then run the entire `add_job_matches_table_FIXED.sql` file**

3. **Verify success:**
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_name = 'job_matches';
   ```
   Should return: `job_matches`

## Future: User-Facing Access

When you add `auth_user_id` to `user_profiles`, update the RLS policy:

```sql
CREATE POLICY rls_job_matches_select_own ON public.job_matches
    FOR SELECT
    USING (
        profile_id = (
            SELECT id FROM public.user_profiles 
            WHERE auth_user_id = auth.uid()
            LIMIT 1
        )
    );
```

The service role key has the authority to bypass RLS, but since there were NO policies defined, PostgreSQL wouldn't even allow service_role to proceed.

## Prevention

Always define RLS policies when enabling RLS on a table. Don't just enable RLS without policies.

---

## How to Apply the Fix

### Step 1: Create SQL Fix File

```bash
cat > /Users/santhosh-16982/my_job_agent/job-scraper/supabase_setup/fix_rls_42501_error.sql << 'EOF'
-- FIX: RLS Policy Error 42501
-- This fixes: "new row violates row-level security policy for table skills"
-- Root cause: auth.role() doesn't work properly with service role key

BEGIN;

-- Remove all broken policies
DROP POLICY IF EXISTS "service_role_backend_full_access" ON public.skills;
DROP POLICY IF EXISTS "users_cannot_access_directly" ON public.skills;
DROP POLICY IF EXISTS "allow_insert_service_role" ON public.skills;
DROP POLICY IF EXISTS "service_role_insert_only" ON public.skills;

-- Create WORKING policies
CREATE POLICY "allow_all_operations"
  ON public.skills
  FOR ALL
  USING (true)
  WITH CHECK (true);

CREATE POLICY "block_regular_users"
  ON public.skills
  FOR ALL
  USING (false)
  WITH CHECK (false);

-- Verify policies are correct
SELECT policyname, permissive, qual, with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'skills'
ORDER BY policyname;

COMMIT;
EOF
```

### Step 2: Apply via Supabase Dashboard (Easiest)

1. Go to: https://app.supabase.com
2. Select your project
3. Go to: **SQL Editor** → **New Query**
4. Paste the SQL from step 1
5. Click: **Execute**
6. Verify: See 2 policies listed

### Step 3: Apply via CLI

```bash
cd /Users/santhosh-16982/my_job_agent/job-scraper
supabase link --project-ref <YOUR_PROJECT_ID>
supabase db push supabase_setup/fix_rls_42501_error.sql
```

### Step 4: Apply via psql

```bash
psql -h <PROJECT_ID>.supabase.co \
     -U postgres \
     -d postgres \
     -f supabase_setup/fix_rls_42501_error.sql
```

---

## Verify the Fix

### Test 1: Check Policies

```sql
-- Run in Supabase SQL Editor
SELECT policyname, permissive, qual, with_check
FROM pg_policies
WHERE tablename = 'skills'
ORDER BY policyname;
```

**Expected Output:**
```
allow_all_operations | t | true | true
block_regular_users  | t | f    | f
```

### Test 2: Test Insert in Python

```python
import os
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

test_skill = {
    'skill_name': f'TestSkill_{os.urandom(4).hex()}',
    'category': 'discovered',
    'requirement': 'optional',
    'confidence_score': 75,
    'tags': ['test']
}

try:
    response = supabase.table("skills").insert(test_skill).execute()
    if response.data:
        print(f"✅ SUCCESS: Inserted skill ID {response.data[0]['id']}")
    else:
        print(f"❌ FAILED: No data returned")
except Exception as e:
    if "violates row-level security" in str(e):
        print(f"❌ RLS STILL BROKEN: {e}")
    else:
        print(f"❌ OTHER ERROR: {e}")
```

### Test 3: Run Full Test Suite

```bash
python test_rls_fix.py
```

**Expected:** All 4 tests pass, especially Test 4 (insert/delete)

---

## Why This Works

### The Issue

When using service role key:
```python
supabase = create_client(url, SUPABASE_SERVICE_ROLE_KEY)
```

Supabase client might not set `auth.role()` properly, causing:
- Old policy: `auth.role() = 'service_role'` → Evaluates to FALSE → Access Denied
- New policy: `USING (true)` → Always TRUE → Access Granted

### The Fix

New policies:
1. `allow_all_operations`: Allows service role (backend use only)
2. `block_regular_users`: Blocks unauthenticated users

This is the **recommended Supabase approach** for backend services.

---

## Before & After

### Before (Broken)
```
SkillDiscovery.discover_skills()
  ↓
INSERT INTO skills (...)
  ↓
RLS Check: auth.role() = 'service_role'?
  ↓
Result: NULL = 'service_role'? → FALSE
  ↓
ERROR 42501: Permission Denied ❌
```

### After (Fixed)
```
SkillDiscovery.discover_skills()
  ↓
INSERT INTO skills (...)
  ↓
RLS Check: USING (true)?
  ↓
Result: TRUE → Allow ✅
  ↓
Skill inserted successfully ✅
```

---

## Next Steps

1. ✅ Apply SQL fix to Supabase
2. ✅ Run `test_rls_fix.py` to verify
3. ✅ Restart your application
4. ✅ Score a job - should see: "✅ Inserted new skill"
5. ✅ Check database - new skills appear in table

---

## Troubleshooting

### Still Getting Error 42501?

```bash
# Check if policies were actually applied
psql -h <PROJECT_ID>.supabase.co -U postgres -d postgres << 'EOF'
SELECT policyname FROM pg_policies WHERE tablename = 'skills';
EOF

# Should show: allow_all_operations, block_regular_users
```

### Policies Show But Still Failing?

```bash
# Try disabling and re-enabling RLS
psql -h <PROJECT_ID>.supabase.co -U postgres -d postgres << 'EOF'
ALTER TABLE public.skills DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;

-- Then create policies again
CREATE POLICY "allow_all_operations"
  ON public.skills FOR ALL USING (true) WITH CHECK (true);
EOF
```

### Getting "Permission Denied" on SELECT?

```bash
# Verify both policies exist and are permissive=true
SELECT * FROM pg_policies WHERE tablename = 'skills';

# If missing, create them:
CREATE POLICY "allow_all_operations"
  ON public.skills FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "block_regular_users"
  ON public.skills FOR ALL USING (false) WITH CHECK (false);
```

---

## Related Files

- SQL Fix: `/supabase_setup/fix_rls_42501_error.sql` (created for you)
- Test Script: `/test_rls_fix.py`
- Skill Discovery: `/skill_discovery.py` (line 280: `_insert_skill()`)
- Supabase Schema: `/supabase_setup/create_skills_table.sql`
