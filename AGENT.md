# 🤖 AI Agent Documentation
## Job Scraper - Intelligent Automation System

This document provides comprehensive information for AI agents (like GitHub Copilot, Claude, ChatGPT, etc.) working with this codebase.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Key Components](#-key-components)
- [Data Flow](#-data-flow)
- [Common Tasks](#-common-tasks)
- [Code Patterns](#-code-patterns)
- [Testing Guidelines](#-testing-guidelines)
- [Troubleshooting](#-troubleshooting)
- [Best Practices](#-best-practices)

---

## 🎯 Project Overview

### Purpose
An intelligent job scraping and matching system that automates the job hunting process using AI-powered skill extraction, matching, and resume customization.

### Key Technologies
- **Language**: Python 3.13+
- **Database**: Supabase (PostgreSQL)
- **NLP**: spaCy
- **LLM**: LiteLLM (Fireworks AI, OpenAI, Gemini, etc.)
- **Web Scraping**: BeautifulSoup, Requests
- **PDF**: ReportLab, pdfplumber
- **CI/CD**: GitHub Actions

### Main Entry Points
1. **`scraper.py`**: Main job scraping orchestrator
2. **`scoring_orchestrator.py`**: Job scoring and matching
3. **`custom_resume_generator.py`**: Resume customization
4. **`.github/workflows/daily-scraper.yml`**: Automated daily execution

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Cron)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      scraper.py                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Skill Extraction Pipeline                │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │   spaCy    │→ │    LLM     │→ │  Skill     │     │  │
│  │  │ Extractor  │  │ Extractor  │  │ Discovery  │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Job Scoring Pipeline                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Profile   │→ │    Job     │→ │   Match    │     │  │
│  │  │  Scorer    │  │   Scorer   │  │  Analyzer  │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Supabase Database                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Jobs   │  │  Skills  │  │ Profiles │  │ Matches  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
scraper.py
    ↓
SkillManager (skills_manager.py)
    ↓
SpacySkillExtractor (spacy_extractor.py)
    ↓
LLMSkillExtractor (llm_skill_extractor.py)
    ↓
SkillExtractionService (skill_extraction_service.py)
    ↓
Supabase (supabase_utils.py)
```

---

## 🔑 Key Components

### 1. Skill Extraction System

#### **SkillManager** (`skills_manager.py`)
- **Purpose**: Manages skills database with in-memory caching
- **Key Methods**:
  - `get_all_skills()`: Returns flat list of skill names
  - `build_canonical_lookup()`: Builds skill name → (canonical, category) mapping
  - `refresh_cache()`: Reloads skills from database
  - `should_refresh()`: Determines if cache needs refresh

**Usage Example**:
```python
from skills_manager import SkillManager
import supabase_utils

skill_manager = SkillManager(supabase_utils.supabase)
skills = skill_manager.get_all_skills()  # ['java', 'python', ...]
lookup = skill_manager.build_canonical_lookup()  # {'java': ('Java', 'core'), ...}
```

#### **SpacySkillExtractor** (`spacy_extractor.py`)
- **Purpose**: Fast, deterministic skill matching using spaCy PhraseMatcher
- **Input**: Flat list of skill names (strings)
- **Output**: List of `SkillMatch` objects

**Usage Example**:
```python
from spacy_extractor import SpacySkillExtractor

extractor = SpacySkillExtractor(['Java', 'Python', 'Django'])
matches = extractor.extract("I have experience with Java and Python")
# Returns: [SkillMatch(name='Java', ...), SkillMatch(name='Python', ...)]
```

#### **LLMSkillExtractor** (`llm_skill_extractor.py`)
- **Purpose**: AI-powered skill extraction with requirement levels
- **Features**: Prompt caching, retry logic, structured output
- **Output**: `SkillExtraction` object with skills, levels, and evidence

**Usage Example**:
```python
from llm_skill_extractor import LLMSkillExtractor

llm = LLMSkillExtractor()
result = llm.extract(
    description="Looking for Python developer with Django experience",
    known_skills=['Python']
)
# Returns: SkillExtraction(skills=[...], status='ok', ...)
```

#### **SkillExtractionService** (`skill_extraction_service.py`)
- **Purpose**: Orchestrates spaCy + LLM extraction
- **Features**: Merges results, handles failures gracefully

**Usage Example**:
```python
from skill_extraction_service import SkillExtractionService

service = SkillExtractionService(
    spacy_extractor=spacy_extractor,
    canonical_lookup=canonical_lookup,
    llm_extractor=llm_extractor
)
result = service.extract_skills(job_description)
# Returns: SkillExtractionResult(skills=[...], llm_status='ok', ...)
```

### 2. Job Scoring System

#### **JobScorer** (`job_scorer.py`)
- **Purpose**: Scores jobs against user profiles
- **Scoring Factors**:
  - Skill match (40%)
  - Experience match (30%)
  - Education match (15%)
  - Location match (10%)
  - Salary match (5%)

**Usage Example**:
```python
from job_scorer import JobScorer

scorer = JobScorer()
match_result = scorer.score_job(
    job=job_data,
    profile=user_profile,
    extracted_skills=skills
)
# Returns: MatchResult(score=85.5, skill_matches=[...], ...)
```

#### **ProfileJobScorer** (`profile_scorer.py`)
- **Purpose**: Scores jobs for multiple profiles
- **Features**: Batch processing, parallel scoring

**Usage Example**:
```python
from profile_scorer import ProfileJobScorer

scorer = ProfileJobScorer()
results = scorer.score_jobs_for_profile(
    profile_id=user_id,
    jobs=job_list
)
```

### 3. Database Layer

#### **Supabase Utils** (`supabase_utils.py`)
- **Purpose**: Database operations and utilities
- **Key Functions**:
  - `get_existing_jobs_from_supabase()`: Fetch existing job IDs
  - `save_jobs_to_supabase()`: Save/update jobs
  - `filter_new_candidates()`: Filter out existing jobs
  - `save_job_matches()`: Save match results

**Usage Example**:
```python
import supabase_utils

# Get existing jobs
existing_ids, existing_pairs = supabase_utils.get_existing_jobs_from_supabase()

# Save new jobs
supabase_utils.save_jobs_to_supabase(jobs_data)

# Filter new candidates
new_jobs = supabase_utils.filter_new_candidates(
    candidate_jobs=jobs,
    existing_ids=existing_ids,
    existing_company_title_keys=existing_pairs
)
```

### 4. LLM Client

#### **Universal LLM Client** (`llm_client.py`)
- **Purpose**: Unified interface for 400+ LLM providers
- **Features**: Rate limiting, retry logic, budget tracking

**Usage Example**:
```python
from llm_client import primary_client

response = primary_client.generate_content(
    prompt="Extract skills from this job description",
    system_prompt="You are a skill extraction expert",
    temperature=0.2,
    response_format=SkillExtraction  # Pydantic model
)
```

### 5. Caching System

#### **PromptCacheManager** (`cache_manager.py`)
- **Purpose**: Reduces LLM costs by caching prompts
- **Features**: TTL-based expiration, hit rate tracking

**Usage Example**:
```python
from cache_manager import PromptCacheManager

cache = PromptCacheManager(enabled=True, ttl_hours=24)
cached_response = cache.get(prompt_hash)
if cached_response:
    return cached_response
else:
    response = llm.generate(prompt)
    cache.set(prompt_hash, response)
```

---

## 🔄 Data Flow

### Job Scraping Flow

```
1. scraper.py starts
   ↓
2. Initialize SkillManager (loads skills from DB)
   ↓
3. Initialize SpacySkillExtractor (with flat skill list)
   ↓
4. Initialize LLMSkillExtractor (with caching)
   ↓
5. Initialize SkillExtractionService (combines spaCy + LLM)
   ↓
6. Fetch jobs from LinkedIn/CareersFuture
   ↓
7. For each job:
   - Convert HTML to Markdown
   - Extract skills (spaCy + LLM)
   - Discover new skills
   - Save to Supabase
   ↓
8. Update skill cache if needed
   ↓
9. Log statistics and exit
```

### Job Scoring Flow

```
1. scoring_orchestrator.py starts
   ↓
2. Load user profiles from Supabase
   ↓
3. Load unscored jobs from Supabase
   ↓
4. For each profile:
   - Parse resume
   - Extract skills
   - For each job:
     - Extract job skills
     - Calculate match score
     - Save match result
   ↓
5. Generate customized resumes for top matches
   ↓
6. Upload PDFs to Supabase Storage
   ↓
7. Log statistics and exit
```

---

## 🛠️ Common Tasks

### Task 1: Add a New Job Source

**Steps**:
1. Create scraper function in `scraper.py`
2. Add source to `config.SCRAPING_SOURCES`
3. Implement job parsing logic
4. Add tests in `test_scraper.py`

**Example**:
```python
def scrape_indeed_jobs(query: str, location: str) -> list[dict]:
    """Scrape jobs from Indeed"""
    # Implementation
    return jobs

# Add to main()
if source == "indeed":
    jobs = scrape_indeed_jobs(query, location)
```

### Task 2: Add a New Skill Category

**Steps**:
1. Add category to database:
   ```sql
   INSERT INTO skills (skill_name, category, source)
   VALUES ('New Skill', 'new_category', 'manual');
   ```
2. Refresh skill cache:
   ```python
   skill_manager.refresh_cache()
   ```

### Task 3: Modify Scoring Algorithm

**Steps**:
1. Edit `job_scorer.py`
2. Update scoring weights in `SCORING_WEIGHTS`
3. Add new scoring factors
4. Update tests in `test_job_scorer.py`

**Example**:
```python
SCORING_WEIGHTS = {
    'skill_match': 0.40,
    'experience_match': 0.30,
    'education_match': 0.15,
    'location_match': 0.10,
    'salary_match': 0.05,
    'new_factor': 0.10,  # Add new factor
}
```

### Task 4: Add a New LLM Provider

**Steps**:
1. Add API key to `.env`:
   ```env
   NEW_PROVIDER_API_KEY=your_key_here
   ```
2. Update `config.py`:
   ```python
   LLM_API_KEY = (
       os.environ.get("LLM_API_KEY")
       or os.environ.get("NEW_PROVIDER_API_KEY")
       or ...
   )
   ```
3. Update `LLM_MODEL`:
   ```python
   LLM_MODEL = "new_provider/model-name"
   ```

### Task 5: Debug Skill Extraction

**Steps**:
1. Enable debug logging:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```
2. Test spaCy extraction:
   ```python
   extractor = SpacySkillExtractor(['Java', 'Python'])
   matches = extractor.extract("I know Java")
   print(matches)
   ```
3. Test LLM extraction:
   ```python
   llm = LLMSkillExtractor()
   result = llm.extract("Job description", known_skills=[])
   print(result)
   ```

---

## 📝 Code Patterns

### Pattern 1: Database Operations

**Always use try-except**:
```python
try:
    response = supabase.table("jobs").insert(data).execute()
    logger.info(f"Saved {len(data)} jobs")
except Exception as e:
    logger.error(f"Failed to save jobs: {e}")
    raise
```

### Pattern 2: LLM Calls

**Always use retry logic**:
```python
from llm_client import primary_client

try:
    response = primary_client.generate_content(
        prompt=prompt,
        temperature=0.2,
        max_retries=3
    )
except Exception as e:
    logger.error(f"LLM call failed: {e}")
    # Fallback to default behavior
```

### Pattern 3: Skill Extraction

**Always combine spaCy + LLM**:
```python
# Step 1: spaCy (fast, deterministic)
spacy_matches = spacy_extractor.extract(text)

# Step 2: LLM (slow, intelligent)
llm_result = llm_extractor.extract(text, known_skills=[m.name for m in spacy_matches])

# Step 3: Merge results
merged_skills = merge_skills(spacy_matches, llm_result.skills)
```

### Pattern 4: Error Handling

**Always log and continue**:
```python
for job in jobs:
    try:
        process_job(job)
    except Exception as e:
        logger.error(f"Failed to process job {job['id']}: {e}")
        continue  # Don't stop the entire process
```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_skills_migration.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Writing Tests

**Test Structure**:
```python
def test_feature_name():
    """Test description"""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result.status == 'ok'
    assert len(result.skills) > 0
```

**Example Test**:
```python
def test_spacy_extractor():
    """Test spaCy skill extraction"""
    extractor = SpacySkillExtractor(['Java', 'Python'])
    matches = extractor.extract("I have experience with Java")
    
    assert len(matches) == 1
    assert matches[0].name == 'Java'
```

---

## 🔍 Troubleshooting

### Issue 1: Skill Extraction Not Working

**Symptoms**: No skills extracted from job descriptions

**Debug Steps**:
1. Check if skills are loaded:
   ```python
   print(f"Loaded {len(skill_manager.get_all_skills())} skills")
   ```
2. Test spaCy extractor:
   ```python
   matches = spacy_extractor.extract("Java Python Django")
   print(f"Found {len(matches)} matches")
   ```
3. Check LLM status:
   ```python
   print(f"LLM status: {result.llm_status}")
   ```

### Issue 2: Database Connection Failed

**Symptoms**: `ConnectionError` or `AuthenticationError`

**Debug Steps**:
1. Verify environment variables:
   ```python
   print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
   print(f"SUPABASE_KEY: {os.environ.get('SUPABASE_SERVICE_ROLE_KEY')[:20]}...")
   ```
2. Test connection:
   ```python
   python test_supabase_connection.py
   ```

### Issue 3: LLM Rate Limit Exceeded

**Symptoms**: `RateLimitError` or `429 Too Many Requests`

**Solutions**:
1. Enable prompt caching:
   ```python
   cache = PromptCacheManager(enabled=True)
   ```
2. Reduce request frequency:
   ```python
   time.sleep(2)  # Add delay between requests
   ```
3. Use fallback to spaCy only:
   ```python
   llm_extractor = None  # Disable LLM
   ```

---

## 💡 Best Practices

### 1. Always Use Type Hints

```python
def extract_skills(text: str) -> list[SkillMatch]:
    """Extract skills from text"""
    ...
```

### 2. Always Log Important Events

```python
logger.info(f"Processing job {job_id}")
logger.warning(f"Skill not found: {skill_name}")
logger.error(f"Failed to save job: {e}")
```

### 3. Always Handle Errors Gracefully

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    result = fallback_operation()
```

### 4. Always Use Context Managers

```python
with open('file.txt', 'r') as f:
    data = f.read()
```

### 5. Always Validate Input

```python
def process_job(job: dict) -> None:
    if not job.get('job_id'):
        raise ValueError("Job ID is required")
    ...
```

---

## 📚 Additional Resources

- **Main README**: [README.md](README.md)
- **GitHub Actions Setup**: [GITHUB_ACTIONS_STEP_BY_STEP.md](GITHUB_ACTIONS_STEP_BY_STEP.md)
- **Architecture Q&A**: [ARCHITECTURE_Q_AND_A.md](ARCHITECTURE_Q_AND_A.md)
- **Scoring Engine**: [scoring_engine.md](scoring_engine.md)

---

## 🤝 Contributing

When contributing to this project:

1. **Follow code patterns** described in this document
2. **Add tests** for new features
3. **Update documentation** when changing behavior
4. **Use type hints** for all functions
5. **Log important events** for debugging

---

**Last Updated**: November 23, 2026  
**Version**: 1.0.0  
**Maintained by**: AI Agents & Human Developers
