-- FIX RLS READ PERMISSION FOR SERVICE ROLE
-- File: supabase_setup/fix_rls_read_permission.sql
-- Purpose: Allow service role to SELECT from skills table (needed by SkillManager)
-- Status: REQUIRED - System won't work without this fix
-- Applied: [Your Date]

BEGIN;

-- ============================================================================
-- PART 1: Remove broken policies (INSERT-only)
-- ============================================================================

DROP POLICY IF EXISTS "allow_insert_service_role" ON public.skills;
DROP POLICY IF EXISTS "service_role_insert_only" ON public.skills;
DROP POLICY IF EXISTS "allow_insert" ON public.skills;

-- ============================================================================
-- PART 2: Create new policies
-- ============================================================================

-- Policy 1: Service role can perform ALL operations (backend use only)
-- Used by: SkillManager (SELECT), SkillDiscovery (SELECT + INSERT)
CREATE POLICY "service_role_backend_full_access"
  ON public.skills
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Policy 2: Regular users cannot access skills table directly
-- Users must access through API endpoints (which add auth layer)
CREATE POLICY "users_cannot_access_directly"
  ON public.skills
  FOR ALL
  USING (false)
  WITH CHECK (false);

SELECT 
    policyname,
    permissive,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'skills'
ORDER BY policyname;

COMMIT;
