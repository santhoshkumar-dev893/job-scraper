-- ============================================================================
-- EXTRA 150+ SKILLS: COMPREHENSIVE DATABASE INSERT
-- ============================================================================
-- File: supabase_setup/add_extra_skills.sql
-- Purpose: Add 150+ additional skills covering Frontend, Backend, ML/AI, DevOps, etc.
-- Status: Ready to execute - copy/paste all SQL into Supabase SQL Editor
-- 
-- IMPORTANT: This script inserts skills into the correct table schema:
--   • skill_name (text, unique)
--   • category (text: 'core' or 'discovered')
--   • source (text: 'manual' or 'llm')
--   • confidence_score (smallint: 0-100)
--   • tags (text array)
--   • description (text)
--   • validation_status (text: 'pending', 'validated', 'rejected')
-- 
-- Skills Categories:
--   • Frontend: React, Vue, Angular, CSS, HTML, UI/UX, etc.
--   • Backend: Node.js, Express, Django, FastAPI, Flask, Spring, etc.
--   • ML/AI: TensorFlow, PyTorch, Scikit-learn, NLP, Computer Vision, etc.
--   • DevOps: Kubernetes, Docker, CI/CD, Terraform, Ansible, etc.
--   • Database: PostgreSQL, MongoDB, Redis, Elasticsearch, etc.
--   • Cloud: AWS, Google Cloud, Azure services
--   • Mobile: React Native, Flutter, Swift, Kotlin
--   • Data: Spark, Hadoop, Kafka, ETL, Big Data
--   • Testing & QA: Jest, Pytest, Selenium, Cypress
--   • Soft Skills: Communication, Leadership, Project Management

BEGIN;

-- ============================================================================
-- FRONTEND SKILLS (18 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('React', 'core', 'manual', 90, ARRAY['frontend', 'javascript'], 'React.js library for building user interfaces', 'validated'),
  ('React Hooks', 'core', 'manual', 80, ARRAY['frontend', 'react'], 'React functional components with hooks', 'validated'),
  ('Vue.js', 'core', 'manual', 75, ARRAY['frontend', 'javascript'], 'Vue.js progressive JavaScript framework', 'validated'),
  ('Angular', 'core', 'manual', 75, ARRAY['frontend', 'typescript'], 'Angular TypeScript framework', 'validated'),
  ('TypeScript', 'core', 'manual', 85, ARRAY['frontend', 'backend', 'language'], 'TypeScript programming language', 'validated'),
  ('CSS', 'core', 'manual', 90, ARRAY['frontend', 'web'], 'Cascading Style Sheets', 'validated'),
  ('SCSS/SASS', 'core', 'manual', 75, ARRAY['frontend', 'css'], 'Sass preprocessor for CSS', 'validated'),
  ('Tailwind CSS', 'core', 'manual', 75, ARRAY['frontend', 'css'], 'Utility-first CSS framework', 'validated'),
  ('Material-UI', 'core', 'manual', 70, ARRAY['frontend', 'react'], 'Material Design component library', 'validated'),
  ('HTML5', 'core', 'manual', 90, ARRAY['frontend', 'web'], 'HTML5 markup language', 'validated'),
  ('JavaScript', 'core', 'manual', 95, ARRAY['frontend', 'backend', 'language'], 'JavaScript programming language', 'validated'),
  ('Webpack', 'core', 'manual', 70, ARRAY['frontend', 'build-tools'], 'JavaScript module bundler', 'validated'),
  ('Babel', 'core', 'manual', 70, ARRAY['frontend', 'build-tools'], 'JavaScript compiler', 'validated'),
  ('ESLint', 'core', 'manual', 70, ARRAY['frontend', 'linting'], 'JavaScript linter', 'validated'),
  ('UI/UX Design', 'core', 'manual', 75, ARRAY['frontend', 'design'], 'User interface and user experience design', 'validated'),
  ('Responsive Design', 'core', 'manual', 80, ARRAY['frontend', 'web'], 'Mobile-first responsive web design', 'validated'),
  ('GraphQL', 'core', 'manual', 75, ARRAY['frontend', 'backend', 'api'], 'GraphQL query language', 'validated'),
  ('REST API', 'core', 'manual', 85, ARRAY['frontend', 'backend', 'api'], 'RESTful API design and consumption', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- BACKEND SKILLS (25 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Node.js', 'core', 'manual', 85, ARRAY['backend', 'javascript'], 'Node.js runtime environment', 'validated'),
  ('Express', 'core', 'manual', 80, ARRAY['backend', 'nodejs', 'framework'], 'Express.js web framework', 'validated'),
  ('Python', 'core', 'manual', 90, ARRAY['backend', 'language', 'ml', 'ai'], 'Python programming language', 'validated'),
  ('Django', 'core', 'manual', 80, ARRAY['backend', 'python', 'framework'], 'Django web framework', 'validated'),
  ('Flask', 'core', 'manual', 75, ARRAY['backend', 'python', 'framework'], 'Flask lightweight web framework', 'validated'),
  ('FastAPI', 'core', 'manual', 75, ARRAY['backend', 'python', 'framework', 'api'], 'FastAPI modern Python web framework', 'validated'),
  ('Java', 'core', 'manual', 85, ARRAY['backend', 'language'], 'Java programming language', 'validated'),
  ('Spring Boot', 'core', 'manual', 80, ARRAY['backend', 'java', 'framework'], 'Spring Boot Java framework', 'validated'),
  ('Spring Framework', 'core', 'manual', 75, ARRAY['backend', 'java', 'framework'], 'Spring Framework', 'validated'),
  ('C#', 'core', 'manual', 75, ARRAY['backend', 'language'], 'C# programming language', 'validated'),
  ('.NET', 'core', 'manual', 75, ARRAY['backend', 'csharp', 'framework'], '.NET framework', 'validated'),
  ('ASP.NET', 'core', 'manual', 75, ARRAY['backend', 'csharp', 'framework'], 'ASP.NET web framework', 'validated'),
  ('Go', 'core', 'manual', 70, ARRAY['backend', 'language'], 'Go programming language', 'validated'),
  ('Rust', 'core', 'manual', 70, ARRAY['backend', 'language'], 'Rust systems programming language', 'validated'),
  ('PHP', 'core', 'manual', 70, ARRAY['backend', 'language'], 'PHP server-side language', 'validated'),
  ('Laravel', 'core', 'manual', 70, ARRAY['backend', 'php', 'framework'], 'Laravel PHP framework', 'validated'),
  ('Symfony', 'core', 'manual', 70, ARRAY['backend', 'php', 'framework'], 'Symfony PHP framework', 'validated'),
  ('Ruby', 'core', 'manual', 70, ARRAY['backend', 'language'], 'Ruby programming language', 'validated'),
  ('Ruby on Rails', 'core', 'manual', 70, ARRAY['backend', 'ruby', 'framework'], 'Ruby on Rails framework', 'validated'),
  ('Middleware', 'core', 'manual', 70, ARRAY['backend', 'architecture'], 'Middleware design patterns', 'validated'),
  ('Authentication', 'core', 'manual', 85, ARRAY['backend', 'security'], 'Authentication mechanisms (JWT, OAuth)', 'validated'),
  ('Authorization', 'core', 'manual', 80, ARRAY['backend', 'security'], 'Authorization and access control', 'validated'),
  ('API Design', 'core', 'manual', 80, ARRAY['backend', 'api', 'architecture'], 'RESTful API design principles', 'validated'),
  ('Database Design', 'core', 'manual', 85, ARRAY['backend', 'database'], 'Database schema design', 'validated'),
  ('Microservices', 'core', 'manual', 80, ARRAY['backend', 'architecture'], 'Microservices architecture pattern', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- MACHINE LEARNING & AI SKILLS (30 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Machine Learning', 'core', 'manual', 85, ARRAY['ml', 'ai'], 'General machine learning', 'validated'),
  ('Deep Learning', 'core', 'manual', 80, ARRAY['ml', 'ai', 'neural-networks'], 'Deep neural networks', 'validated'),
  ('TensorFlow', 'core', 'manual', 85, ARRAY['ml', 'ai', 'framework'], 'TensorFlow machine learning framework', 'validated'),
  ('PyTorch', 'core', 'manual', 85, ARRAY['ml', 'ai', 'framework'], 'PyTorch deep learning framework', 'validated'),
  ('Keras', 'core', 'manual', 75, ARRAY['ml', 'ai', 'tensorflow'], 'Keras neural network library', 'validated'),
  ('Scikit-learn', 'core', 'manual', 80, ARRAY['ml', 'ai', 'python'], 'Scikit-learn machine learning library', 'validated'),
  ('Natural Language Processing', 'core', 'manual', 80, ARRAY['ml', 'ai', 'nlp'], 'NLP text processing', 'validated'),
  ('Computer Vision', 'core', 'manual', 80, ARRAY['ml', 'ai', 'cv'], 'Computer vision and image processing', 'validated'),
  ('OpenCV', 'core', 'manual', 75, ARRAY['ml', 'ai', 'cv'], 'OpenCV computer vision library', 'validated'),
  ('NLTK', 'core', 'manual', 70, ARRAY['ml', 'ai', 'nlp'], 'NLTK natural language toolkit', 'validated'),
  ('Spacy', 'core', 'manual', 75, ARRAY['ml', 'ai', 'nlp'], 'Spacy NLP library', 'validated'),
  ('Transformers', 'core', 'manual', 75, ARRAY['ml', 'ai', 'nlp'], 'Transformer models (BERT, GPT)', 'validated'),
  ('BERT', 'core', 'manual', 75, ARRAY['ml', 'ai', 'nlp', 'transformer'], 'BERT language model', 'validated'),
  ('GPT', 'core', 'manual', 75, ARRAY['ml', 'ai', 'nlp', 'generative'], 'GPT generative language model', 'validated'),
  ('LLM', 'core', 'manual', 75, ARRAY['ml', 'ai', 'generative'], 'Large Language Models', 'validated'),
  ('LangChain', 'core', 'manual', 70, ARRAY['ml', 'ai', 'llm'], 'LangChain LLM framework', 'validated'),
  ('Pandas', 'core', 'manual', 85, ARRAY['ml', 'ai', 'data', 'python'], 'Pandas data analysis library', 'validated'),
  ('NumPy', 'core', 'manual', 85, ARRAY['ml', 'ai', 'data', 'python'], 'NumPy numerical computing', 'validated'),
  ('Matplotlib', 'core', 'manual', 80, ARRAY['ml', 'ai', 'visualization', 'python'], 'Matplotlib data visualization', 'validated'),
  ('Seaborn', 'core', 'manual', 75, ARRAY['ml', 'ai', 'visualization', 'python'], 'Seaborn statistical visualization', 'validated'),
  ('Plotly', 'core', 'manual', 70, ARRAY['ml', 'ai', 'visualization'], 'Plotly interactive visualization', 'validated'),
  ('Statistical Analysis', 'core', 'manual', 80, ARRAY['ml', 'ai', 'data'], 'Statistical analysis and modeling', 'validated'),
  ('Linear Regression', 'core', 'manual', 75, ARRAY['ml', 'ai', 'algorithm'], 'Linear regression algorithms', 'validated'),
  ('Classification', 'core', 'manual', 75, ARRAY['ml', 'ai', 'algorithm'], 'Classification algorithms', 'validated'),
  ('Clustering', 'core', 'manual', 75, ARRAY['ml', 'ai', 'algorithm'], 'Clustering algorithms', 'validated'),
  ('Feature Engineering', 'core', 'manual', 80, ARRAY['ml', 'ai', 'data'], 'Feature engineering techniques', 'validated'),
  ('Model Evaluation', 'core', 'manual', 80, ARRAY['ml', 'ai', 'testing'], 'Model evaluation and validation', 'validated'),
  ('Hyperparameter Tuning', 'core', 'manual', 75, ARRAY['ml', 'ai', 'optimization'], 'Hyperparameter tuning and optimization', 'validated'),
  ('Reinforcement Learning', 'core', 'manual', 70, ARRAY['ml', 'ai', 'algorithm'], 'Reinforcement learning', 'validated'),
  ('Prompt Engineering', 'core', 'manual', 75, ARRAY['ml', 'ai', 'llm'], 'Prompt engineering for LLMs', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- DATABASE SKILLS (15 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('SQL', 'core', 'manual', 90, ARRAY['database', 'language'], 'SQL query language', 'validated'),
  ('PostgreSQL', 'core', 'manual', 85, ARRAY['database', 'sql'], 'PostgreSQL relational database', 'validated'),
  ('MySQL', 'core', 'manual', 75, ARRAY['database', 'sql'], 'MySQL relational database', 'validated'),
  ('MongoDB', 'core', 'manual', 80, ARRAY['database', 'nosql'], 'MongoDB NoSQL database', 'validated'),
  ('Firebase', 'core', 'manual', 75, ARRAY['database', 'backend-as-service'], 'Firebase real-time database', 'validated'),
  ('Redis', 'core', 'manual', 80, ARRAY['database', 'cache', 'nosql'], 'Redis in-memory data store', 'validated'),
  ('Elasticsearch', 'core', 'manual', 75, ARRAY['database', 'search', 'nosql'], 'Elasticsearch search engine', 'validated'),
  ('DynamoDB', 'core', 'manual', 70, ARRAY['database', 'aws', 'nosql'], 'AWS DynamoDB database', 'validated'),
  ('Cassandra', 'core', 'manual', 70, ARRAY['database', 'nosql', 'distributed'], 'Apache Cassandra distributed database', 'validated'),
  ('Database Optimization', 'core', 'manual', 80, ARRAY['database', 'performance'], 'Database query optimization', 'validated'),
  ('Indexing', 'core', 'manual', 80, ARRAY['database', 'optimization'], 'Database indexing strategies', 'validated'),
  ('ORM', 'core', 'manual', 80, ARRAY['database', 'backend'], 'Object-Relational Mapping', 'validated'),
  ('SQLAlchemy', 'core', 'manual', 75, ARRAY['database', 'orm', 'python'], 'SQLAlchemy Python ORM', 'validated'),
  ('Hibernation', 'core', 'manual', 70, ARRAY['database', 'orm', 'java'], 'Hibernate ORM for Java', 'validated'),
  ('Database Migration', 'core', 'manual', 80, ARRAY['database', 'devops'], 'Database schema migrations', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- DEVOPS & CLOUD SKILLS (20 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Docker', 'core', 'manual', 90, ARRAY['devops', 'containerization'], 'Docker containerization', 'validated'),
  ('Kubernetes', 'core', 'manual', 85, ARRAY['devops', 'orchestration'], 'Kubernetes container orchestration', 'validated'),
  ('AWS', 'core', 'manual', 85, ARRAY['cloud', 'aws'], 'Amazon Web Services', 'validated'),
  ('Google Cloud', 'core', 'manual', 75, ARRAY['cloud', 'gcp'], 'Google Cloud Platform', 'validated'),
  ('Azure', 'core', 'manual', 75, ARRAY['cloud', 'microsoft'], 'Microsoft Azure cloud', 'validated'),
  ('EC2', 'core', 'manual', 75, ARRAY['cloud', 'aws'], 'AWS EC2 virtual machines', 'validated'),
  ('S3', 'core', 'manual', 75, ARRAY['cloud', 'aws', 'storage'], 'AWS S3 object storage', 'validated'),
  ('Lambda', 'core', 'manual', 75, ARRAY['cloud', 'aws', 'serverless'], 'AWS Lambda serverless compute', 'validated'),
  ('Terraform', 'core', 'manual', 80, ARRAY['devops', 'infrastructure-as-code'], 'Terraform infrastructure automation', 'validated'),
  ('Ansible', 'core', 'manual', 75, ARRAY['devops', 'configuration-management'], 'Ansible configuration management', 'validated'),
  ('CI/CD', 'core', 'manual', 85, ARRAY['devops', 'automation'], 'Continuous Integration/Continuous Deployment', 'validated'),
  ('Jenkins', 'core', 'manual', 75, ARRAY['devops', 'ci-cd'], 'Jenkins CI/CD server', 'validated'),
  ('GitHub Actions', 'core', 'manual', 80, ARRAY['devops', 'ci-cd', 'github'], 'GitHub Actions CI/CD', 'validated'),
  ('GitLab CI', 'core', 'manual', 75, ARRAY['devops', 'ci-cd', 'gitlab'], 'GitLab CI/CD', 'validated'),
  ('Linux', 'core', 'manual', 85, ARRAY['devops', 'os'], 'Linux operating system', 'validated'),
  ('Bash', 'core', 'manual', 80, ARRAY['devops', 'scripting', 'shell'], 'Bash shell scripting', 'validated'),
  ('Git', 'core', 'manual', 90, ARRAY['devops', 'version-control'], 'Git version control', 'validated'),
  ('GitHub', 'core', 'manual', 85, ARRAY['devops', 'version-control'], 'GitHub platform', 'validated'),
  ('Monitoring', 'core', 'manual', 75, ARRAY['devops', 'operations'], 'System and application monitoring', 'validated'),
  ('Logging', 'core', 'manual', 75, ARRAY['devops', 'operations'], 'Application logging and analysis', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- MOBILE & CROSS-PLATFORM SKILLS (10 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('React Native', 'core', 'manual', 75, ARRAY['mobile', 'cross-platform', 'javascript'], 'React Native mobile framework', 'validated'),
  ('Flutter', 'core', 'manual', 75, ARRAY['mobile', 'cross-platform', 'dart'], 'Flutter mobile framework', 'validated'),
  ('iOS', 'core', 'manual', 75, ARRAY['mobile', 'apple'], 'iOS mobile development', 'validated'),
  ('Swift', 'core', 'manual', 75, ARRAY['mobile', 'ios', 'language'], 'Swift programming language', 'validated'),
  ('Objective-C', 'core', 'manual', 70, ARRAY['mobile', 'ios', 'language'], 'Objective-C programming language', 'validated'),
  ('Android', 'core', 'manual', 75, ARRAY['mobile', 'google'], 'Android mobile development', 'validated'),
  ('Kotlin', 'core', 'manual', 75, ARRAY['mobile', 'android', 'language'], 'Kotlin programming language', 'validated'),
  ('Java (Mobile)', 'core', 'manual', 75, ARRAY['mobile', 'android'], 'Java for Android development', 'validated'),
  ('Dart', 'core', 'manual', 70, ARRAY['mobile', 'flutter', 'language'], 'Dart programming language', 'validated'),
  ('Mobile UI/UX', 'core', 'manual', 75, ARRAY['mobile', 'design'], 'Mobile user interface and experience design', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- DATA ENGINEERING & BIG DATA SKILLS (15 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Apache Spark', 'core', 'manual', 80, ARRAY['data', 'big-data', 'distributed'], 'Apache Spark distributed computing', 'validated'),
  ('Hadoop', 'core', 'manual', 75, ARRAY['data', 'big-data', 'distributed'], 'Apache Hadoop distributed computing', 'validated'),
  ('Apache Kafka', 'core', 'manual', 80, ARRAY['data', 'streaming', 'message-queue'], 'Apache Kafka message streaming', 'validated'),
  ('Data Pipeline', 'core', 'manual', 75, ARRAY['data', 'etl'], 'Data pipeline design and implementation', 'validated'),
  ('ETL', 'core', 'manual', 75, ARRAY['data', 'etl'], 'Extract, Transform, Load processes', 'validated'),
  ('Apache Airflow', 'core', 'manual', 75, ARRAY['data', 'workflow', 'orchestration'], 'Apache Airflow workflow orchestration', 'validated'),
  ('Data Warehouse', 'core', 'manual', 75, ARRAY['data', 'analytics'], 'Data warehouse design and management', 'validated'),
  ('BigQuery', 'core', 'manual', 75, ARRAY['data', 'gcp', 'analytics'], 'Google BigQuery data warehouse', 'validated'),
  ('Snowflake', 'core', 'manual', 75, ARRAY['data', 'analytics'], 'Snowflake cloud data warehouse', 'validated'),
  ('Apache Hive', 'core', 'manual', 70, ARRAY['data', 'hadoop', 'sql'], 'Apache Hive data warehouse', 'validated'),
  ('Presto', 'core', 'manual', 70, ARRAY['data', 'query', 'sql'], 'Presto distributed SQL query', 'validated'),
  ('Data Quality', 'core', 'manual', 70, ARRAY['data', 'testing'], 'Data quality assurance and validation', 'validated'),
  ('Streaming', 'core', 'manual', 75, ARRAY['data', 'streaming', 'real-time'], 'Real-time data streaming', 'validated'),
  ('Data Visualization', 'core', 'manual', 75, ARRAY['data', 'analytics'], 'Data visualization and dashboards', 'validated'),
  ('Tableau', 'core', 'manual', 70, ARRAY['data', 'visualization'], 'Tableau data visualization tool', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- TESTING, QA & QUALITY ASSURANCE SKILLS (12 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Unit Testing', 'core', 'manual', 85, ARRAY['testing', 'qa'], 'Unit testing and test frameworks', 'validated'),
  ('Jest', 'core', 'manual', 80, ARRAY['testing', 'javascript'], 'Jest JavaScript testing framework', 'validated'),
  ('Pytest', 'core', 'manual', 80, ARRAY['testing', 'python'], 'Pytest Python testing framework', 'validated'),
  ('Integration Testing', 'core', 'manual', 80, ARRAY['testing', 'qa'], 'Integration testing', 'validated'),
  ('E2E Testing', 'core', 'manual', 75, ARRAY['testing', 'qa'], 'End-to-end testing', 'validated'),
  ('Cypress', 'core', 'manual', 80, ARRAY['testing', 'e2e'], 'Cypress E2E testing framework', 'validated'),
  ('Selenium', 'core', 'manual', 75, ARRAY['testing', 'e2e'], 'Selenium browser automation', 'validated'),
  ('Test Coverage', 'core', 'manual', 80, ARRAY['testing', 'qa'], 'Test coverage analysis', 'validated'),
  ('Performance Testing', 'core', 'manual', 75, ARRAY['testing', 'qa', 'performance'], 'Performance and load testing', 'validated'),
  ('Security Testing', 'core', 'manual', 75, ARRAY['testing', 'qa', 'security'], 'Security vulnerability testing', 'validated'),
  ('API Testing', 'core', 'manual', 80, ARRAY['testing', 'api'], 'API testing and validation', 'validated'),
  ('Quality Assurance', 'core', 'manual', 80, ARRAY['qa', 'testing'], 'General quality assurance practices', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- SECURITY & COMPLIANCE SKILLS (10 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Security', 'core', 'manual', 85, ARRAY['security', 'devops'], 'General cybersecurity', 'validated'),
  ('SSL/TLS', 'core', 'manual', 80, ARRAY['security', 'encryption'], 'SSL/TLS encryption protocols', 'validated'),
  ('Encryption', 'core', 'manual', 80, ARRAY['security', 'cryptography'], 'Data encryption techniques', 'validated'),
  ('OAuth', 'core', 'manual', 80, ARRAY['security', 'authentication'], 'OAuth authentication protocol', 'validated'),
  ('JWT', 'core', 'manual', 80, ARRAY['security', 'authentication'], 'JSON Web Token authentication', 'validated'),
  ('OWASP', 'core', 'manual', 75, ARRAY['security', 'compliance'], 'OWASP security guidelines', 'validated'),
  ('Penetration Testing', 'core', 'manual', 70, ARRAY['security', 'testing'], 'Penetration testing security', 'validated'),
  ('GDPR', 'core', 'manual', 70, ARRAY['security', 'compliance'], 'GDPR compliance', 'validated'),
  ('Data Privacy', 'core', 'manual', 80, ARRAY['security', 'compliance'], 'Data privacy and protection', 'validated'),
  ('Secure Coding', 'core', 'manual', 80, ARRAY['security', 'best-practices'], 'Secure coding practices', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- SOFT SKILLS & METHODOLOGIES (12 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Communication', 'core', 'manual', 85, ARRAY['soft-skills'], 'Effective communication skills', 'validated'),
  ('Leadership', 'core', 'manual', 75, ARRAY['soft-skills', 'management'], 'Technical and team leadership', 'validated'),
  ('Project Management', 'core', 'manual', 75, ARRAY['soft-skills', 'management'], 'Project management and planning', 'validated'),
  ('Problem Solving', 'core', 'manual', 85, ARRAY['soft-skills'], 'Analytical problem-solving', 'validated'),
  ('Agile', 'core', 'manual', 85, ARRAY['methodology', 'agile'], 'Agile development methodology', 'validated'),
  ('Scrum', 'core', 'manual', 80, ARRAY['methodology', 'agile'], 'Scrum framework', 'validated'),
  ('Kanban', 'core', 'manual', 70, ARRAY['methodology', 'agile'], 'Kanban methodology', 'validated'),
  ('System Design', 'core', 'manual', 80, ARRAY['architecture', 'design'], 'System design and architecture', 'validated'),
  ('Software Architecture', 'core', 'manual', 80, ARRAY['architecture', 'design'], 'Software architecture patterns', 'validated'),
  ('Design Patterns', 'core', 'manual', 80, ARRAY['architecture', 'design'], 'Software design patterns', 'validated'),
  ('Code Review', 'core', 'manual', 80, ARRAY['best-practices', 'collaboration'], 'Code review practices', 'validated'),
  ('Refactoring', 'core', 'manual', 80, ARRAY['best-practices', 'development'], 'Code refactoring techniques', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- SPECIALIZED & EMERGING SKILLS (12 skills)
-- ============================================================================

INSERT INTO public.skills (skill_name, category, source, confidence_score, tags, description, validation_status)
VALUES
  ('Blockchain', 'core', 'manual', 70, ARRAY['emerging', 'web3'], 'Blockchain and distributed ledger', 'validated'),
  ('Web3', 'core', 'manual', 70, ARRAY['emerging', 'blockchain'], 'Web3 and decentralized applications', 'validated'),
  ('Smart Contracts', 'core', 'manual', 70, ARRAY['emerging', 'blockchain'], 'Smart contract development', 'validated'),
  ('Solidity', 'core', 'manual', 70, ARRAY['emerging', 'blockchain', 'language'], 'Solidity smart contract language', 'validated'),
  ('Edge Computing', 'core', 'manual', 70, ARRAY['emerging', 'iot'], 'Edge computing and IoT', 'validated'),
  ('IoT', 'core', 'manual', 70, ARRAY['emerging', 'hardware'], 'Internet of Things development', 'validated'),
  ('WebAssembly', 'core', 'manual', 70, ARRAY['emerging', 'web'], 'WebAssembly binary format', 'validated'),
  ('Serverless', 'core', 'manual', 75, ARRAY['cloud', 'architecture'], 'Serverless architecture', 'validated'),
  ('GraphQL Federation', 'core', 'manual', 70, ARRAY['graphql', 'advanced'], 'GraphQL federation patterns', 'validated'),
  ('Event Sourcing', 'core', 'manual', 70, ARRAY['architecture', 'advanced'], 'Event sourcing architecture', 'validated'),
  ('CQRS', 'core', 'manual', 70, ARRAY['architecture', 'advanced'], 'Command Query Responsibility Segregation', 'validated'),
  ('gRPC', 'core', 'manual', 70, ARRAY['api', 'rpc'], 'gRPC high-performance RPC framework', 'validated')
ON CONFLICT (skill_name) DO NOTHING;

-- ============================================================================
-- COMMIT TRANSACTION
-- ============================================================================

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check total skills added
SELECT COUNT(*) as total_skills FROM public.skills;

-- Check skills by category
SELECT category, COUNT(*) as skill_count FROM public.skills GROUP BY category ORDER BY skill_count DESC;

-- List all skills alphabetically
SELECT skill_name, category, requirement, confidence_score FROM public.skills ORDER BY skill_name;

-- Check for duplicates
SELECT skill_name, COUNT(*) FROM public.skills GROUP BY skill_name HAVING COUNT(*) > 1;
