-- SEED SKILLS TABLE FROM SKILL_MASTER (One-time setup)
-- Fixed PostgreSQL array syntax

INSERT INTO public.skills (skill_name, category, source, confidence_score, validation_status, tags)
VALUES
-- PROGRAMMING LANGUAGES
('Java', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend']),
('Python', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend']),
('JavaScript', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'frontend', 'backend']),
('TypeScript', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'frontend', 'backend']),
('Go', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend']),
('C++', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'systems']),
('C#', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend', 'game']),
('PHP', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend']),
('Ruby', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend']),
('Kotlin', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'mobile']),
('Scala', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'backend']),
('Rust', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'systems']),
('Swift', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'mobile']),
('R', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'data_science']),
('Perl', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'scripting']),
('Dart', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'mobile']),
('Shell Scripting', 'core', 'manual', 100, 'validated', ARRAY['programming_language', 'scripting']),

-- BACKEND FRAMEWORKS
('Spring Boot', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'java']),
('Spring Framework', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'java']),
('Django', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'python']),
('FastAPI', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'python']),
('Flask', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'python']),
('Express.js', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'nodejs']),
('Node.js', 'core', 'manual', 100, 'validated', ARRAY['runtime', 'backend', 'javascript']),
('NestJS', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'nodejs']),
('ASP.NET', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'csharp']),
('Ruby on Rails', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'ruby']),
('Laravel', 'core', 'manual', 100, 'validated', ARRAY['framework', 'backend', 'php']),

-- FRONTEND FRAMEWORKS
('React', 'core', 'manual', 100, 'validated', ARRAY['framework', 'frontend', 'javascript']),
('Angular', 'core', 'manual', 100, 'validated', ARRAY['framework', 'frontend', 'typescript']),
('Vue', 'core', 'manual', 100, 'validated', ARRAY['framework', 'frontend', 'javascript']),
('Next.js', 'core', 'manual', 100, 'validated', ARRAY['framework', 'frontend', 'javascript']),
('Svelte', 'core', 'manual', 100, 'validated', ARRAY['framework', 'frontend', 'javascript']),
('Tailwind CSS', 'core', 'manual', 100, 'validated', ARRAY['framework', 'frontend', 'css']),

-- MOBILE
('Android', 'core', 'manual', 100, 'validated', ARRAY['mobile', 'platform']),
('iOS', 'core', 'manual', 100, 'validated', ARRAY['mobile', 'platform']),
('React Native', 'core', 'manual', 100, 'validated', ARRAY['framework', 'mobile', 'javascript']),
('Flutter', 'core', 'manual', 100, 'validated', ARRAY['framework', 'mobile', 'dart']),

-- DATABASES SQL
('PostgreSQL', 'core', 'manual', 100, 'validated', ARRAY['database', 'sql', 'relational']),
('MySQL', 'core', 'manual', 100, 'validated', ARRAY['database', 'sql', 'relational']),
('Oracle Database', 'core', 'manual', 100, 'validated', ARRAY['database', 'sql', 'relational']),
('SQL Server', 'core', 'manual', 100, 'validated', ARRAY['database', 'sql', 'relational']),
('SQLite', 'core', 'manual', 100, 'validated', ARRAY['database', 'sql', 'relational']),

-- DATABASES NOSQL
('MongoDB', 'core', 'manual', 100, 'validated', ARRAY['database', 'nosql', 'document']),
('Redis', 'core', 'manual', 100, 'validated', ARRAY['database', 'nosql', 'cache']),
('Cassandra', 'core', 'manual', 100, 'validated', ARRAY['database', 'nosql', 'distributed']),
('DynamoDB', 'core', 'manual', 100, 'validated', ARRAY['database', 'nosql', 'aws']),
('Elasticsearch', 'core', 'manual', 100, 'validated', ARRAY['database', 'nosql', 'search']),
('Firebase', 'core', 'manual', 100, 'validated', ARRAY['database', 'nosql', 'realtime']),

-- CLOUD
('AWS', 'core', 'manual', 100, 'validated', ARRAY['cloud', 'provider']),
('Azure', 'core', 'manual', 100, 'validated', ARRAY['cloud', 'provider']),
('Google Cloud', 'core', 'manual', 100, 'validated', ARRAY['cloud', 'provider']),
('Docker', 'core', 'manual', 100, 'validated', ARRAY['devops', 'containerization']),
('Kubernetes', 'core', 'manual', 100, 'validated', ARRAY['devops', 'orchestration']),

-- DEVOPS & TOOLS
('Git', 'core', 'manual', 100, 'validated', ARRAY['devops', 'version_control']),
('Jenkins', 'core', 'manual', 100, 'validated', ARRAY['devops', 'ci_cd']),
('GitHub Actions', 'core', 'manual', 100, 'validated', ARRAY['devops', 'ci_cd']),
('GitLab CI', 'core', 'manual', 100, 'validated', ARRAY['devops', 'ci_cd']),
('REST API', 'core', 'manual', 100, 'validated', ARRAY['architecture', 'api']),
('GraphQL', 'core', 'manual', 100, 'validated', ARRAY['api', 'query_language']),
('SQL', 'core', 'manual', 100, 'validated', ARRAY['database', 'language']),
('Linux', 'core', 'manual', 100, 'validated', ARRAY['operating_system']),
('AWS EC2', 'core', 'manual', 100, 'validated', ARRAY['cloud', 'aws', 'infrastructure']),
('AWS S3', 'core', 'manual', 100, 'validated', ARRAY['cloud', 'aws', 'storage']),
('AWS Lambda', 'core', 'manual', 100, 'validated', ARRAY['cloud', 'aws', 'serverless'])
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- Verify insert
-- ============================================================================
SELECT COUNT(*) as total_skills, 
       COUNT(CASE WHEN source = 'manual' THEN 1 END) as core_skills,
       COUNT(CASE WHEN source = 'llm' THEN 1 END) as discovered_skills
FROM public.skills;

-- Expected output:
-- total_skills | core_skills | discovered_skills
--     70       |      70      |         0
