-- Fix Row Level Security (RLS) for categories table
-- Run this in your Supabase SQL Editor

-- Option 1: Disable RLS on categories table (simpler, good for development)
ALTER TABLE categories DISABLE ROW LEVEL SECURITY;

-- Option 2: Add permissive policy (better for production)
-- ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow all operations on categories" ON categories FOR ALL USING (true);

-- Also disable RLS on other tables for easier development
ALTER TABLE resumes DISABLE ROW LEVEL SECURITY;
ALTER TABLE resume_analysis DISABLE ROW LEVEL SECURITY;
ALTER TABLE skills DISABLE ROW LEVEL SECURITY;
ALTER TABLE resume_skills DISABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions DISABLE ROW LEVEL SECURITY;
ALTER TABLE resume_jd_matches DISABLE ROW LEVEL SECURITY;
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Note: For production, you should use proper RLS policies instead of disabling
