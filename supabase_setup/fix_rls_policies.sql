-- Fix for RLS Policy Issue on jobs table
-- This adds the necessary RLS policies to allow service_role and other roles to insert/update data

-- First, let's check current policies
-- \d+ public.jobs

-- Drop existing policies if any
DROP POLICY IF EXISTS "Allow service_role full access" ON public.jobs;
DROP POLICY IF EXISTS "Allow authenticated full access" ON public.jobs;
DROP POLICY IF EXISTS "Allow anon read access" ON public.jobs;

-- Create RLS policies for the jobs table

-- 1. Allow service_role (backend) to do everything (INSERT, UPDATE, DELETE, SELECT)
CREATE POLICY "Allow service_role full access"
  ON public.jobs
  FOR ALL
  USING (TRUE)
  WITH CHECK (TRUE);

-- 2. Allow authenticated users to read
CREATE POLICY "Allow authenticated read access"
  ON public.jobs
  FOR SELECT
  USING (TRUE);

-- 3. Allow authenticated users to insert/update their own
CREATE POLICY "Allow authenticated insert and update"
  ON public.jobs
  FOR INSERT
  WITH CHECK (TRUE);

-- Alternative: If you want to completely disable RLS on this table:
-- ALTER TABLE public.jobs DISABLE ROW LEVEL SECURITY;

-- Verify permissions
GRANT ALL ON TABLE public.jobs TO service_role;
GRANT SELECT ON TABLE public.jobs TO authenticated;
GRANT INSERT, UPDATE ON TABLE public.jobs TO authenticated;
