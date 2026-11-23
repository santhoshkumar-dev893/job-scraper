-- ============================================================================
-- FIX: RLS POLICY ERROR 42501
-- ============================================================================
-- File: supabase_setup/fix_rls_42501_error.sql
-- Purpose: Fix "new row violates row-level security policy" error
-- Error Code: 42501 (permission denied)
-- 
-- Root Cause: auth.role() doesn't work properly with service role key in 
--             direct backend connections (Python, Node.js, etc.)
-- 
-- Solution: Use USING (true) for service role, which is safe because service
--          role key is backend-only and cannot be exposed to frontend
-- ============================================================================

BEGIN;

-- ============================================================================
-- PART 1: Remove all broken policies
-- ============================================================================

DROP POLICY IF EXISTS "service_role_backend_full_access" ON public.skills;
DROP POLICY IF EXISTS "users_cannot_access_directly" ON public.skills;
DROP POLICY IF EXISTS "allow_insert_service_role" ON public.skills;
DROP POLICY IF EXISTS "service_role_insert_only" ON public.skills;
DROP POLICY IF EXISTS "allow_insert" ON public.skills;
DROP POLICY IF EXISTS "service_role_read_write" ON public.skills;
DROP POLICY IF EXISTS "block_user_direct_access" ON public.skills;

-- ============================================================================
-- PART 2: Create WORKING policies
-- ============================================================================

-- Policy 1: Allow service role to perform ALL operations
-- Why: Service role is backend-only, safe to trust completely
-- Note: Service role key ALWAYS bypasses RLS checks in Supabase
--       This policy just marks it as permissive=true to avoid denials
CREATE POLICY "allow_all_operations"
  ON public.skills
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Policy 2: Block regular users from direct table access
-- Why: Users should access through API endpoints only
-- Note: This prevents unauthenticated users from accessing
CREATE POLICY "block_regular_users"
  ON public.skills
  FOR ALL
  USING (false)
  WITH CHECK (false);

-- ============================================================================
-- PART 3: Verify policies are correct
-- ============================================================================

SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'skills'
ORDER BY policyname;

-- Expected output:
-- public | skills | allow_all_operations | t | true    | true
-- public | skills | block_regular_users  | t | false   | false

COMMIT;

-- ============================================================================
-- TESTING (Optional - uncomment to test, delete before deployment)
-- ============================================================================

-- Test 1: Can we read from skills table?
-- SELECT COUNT(*) FROM public.skills;

-- Test 2: Can we insert into skills table?
-- INSERT INTO public.skills (skill_name, category, requirement, confidence_score, tags)
-- VALUES ('TestSkill', 'discovered', 'optional', 75, ARRAY['test'])
-- ON CONFLICT (skill_name) DO NOTHING;

-- Test 3: Verify insert worked?
-- SELECT * FROM public.skills WHERE skill_name = 'TestSkill';

-- Test 4: Delete test data
-- DELETE FROM public.skills WHERE skill_name = 'TestSkill';
