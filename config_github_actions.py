"""
GitHub Actions-optimized configuration for job scraping.
Use this for faster CI/CD runs with reduced job limits.

To use this config:
  export PYTHONPATH=/path/to/job-scraper:$PYTHONPATH
  python -c "import config_github_actions as config; ..." 
  
Or modify scraper.py to detect GitHub Actions environment and load this config.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- CORE SYSTEM CONFIGURATION ---
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_TABLE_NAME: str = "jobs"
SUPABASE_CUSTOMIZED_RESUMES_TABLE_NAME = "customized_resumes"
SUPABASE_STORAGE_BUCKET = "personalized_resumes"
SUPABASE_RESUME_STORAGE_BUCKET = "resumes"
SUPABASE_BASE_RESUME_TABLE_NAME = "base_resume"
SUPABASE_RESUME_STYLE_TABLE_NAME = "resume_style_settings"
BASE_RESUME_PATH = "resume.json"

# API keys
LLM_API_KEY = (
    os.environ.get("LLM_API_KEY")
    or os.environ.get("FIREWORKS_API_KEY")
    or os.environ.get("FIREWORKS_AI_API_KEY")
    or os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GEMINI_FIRST_API_KEY")
)

# --- OPTIMIZED FOR GITHUB ACTIONS (Reduced load) ---
LLM_MODEL = os.environ.get("LLM_MODEL") or "fireworks_ai/accounts/fireworks/models/glm-5p3-flash"

# Reduced queries for faster runs
LINKEDIN_SEARCH_QUERIES = ["AI Engineer", "Software Engineer"]  # Reduced from 3
LINKEDIN_LOCATION = "India"
LINKEDIN_GEO_ID = 102713980
LINKEDIN_JOB_TYPE = "F"
LINKEDIN_JOB_POSTING_DATE = "r86400"
LINKEDIN_F_WT = "1,2,3"

CAREERS_FUTURE_SEARCH_QUERIES = ["IT Support", "Full Stack Web Developer", "Application Support"]  # Reduced from 5
CAREERS_FUTURE_SEARCH_CATEGORIES = ["Information Technology"]
CAREERS_FUTURE_SEARCH_EMPLOYMENT_TYPES = ["Full Time"]

# Reduced job limits per search
SCRAPING_SOURCES = ["linkedin", "careers_future"]
JOBS_TO_SCORE_PER_RUN = 5
JOBS_TO_CUSTOMIZE_PER_RUN = 1
MAX_JOBS_PER_SEARCH = {
    "linkedin": 5,         # Reduced from 10
    "careers_future": 10,  # Reduced from 20
}

# --- PERFORMANCE OPTIMIZATION ---
LLM_MAX_RPM = 10
LLM_MAX_RETRIES = 2       # Reduced from 3
LLM_RETRY_BASE_DELAY = 5  # Reduced from 10
LLM_DAILY_REQUEST_BUDGET = 0
LLM_REQUEST_DELAY_SECONDS = 5  # Reduced from 8

LINKEDIN_MAX_START = 25
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2           # Reduced from 3
RETRY_DELAY_SECONDS = 30  # Reduced from 60
DETAIL_FETCH_MIN_DELAY = 5.0   # Reduced from 12
DETAIL_FETCH_MAX_DELAY = 10.0  # Reduced from 22
SEARCH_QUERY_MIN_DELAY = 5.0   # Reduced from 15
SEARCH_QUERY_MAX_DELAY = 10.0  # Reduced from 30

JOB_EXPIRY_DAYS = 30
JOB_CHECK_DAYS = 3
JOB_DELETION_DAYS = 60
JOB_CHECK_LIMIT = 50
ACTIVE_CHECK_TIMEOUT = 20
ACTIVE_CHECK_MAX_RETRIES = 1    # Reduced from 2
ACTIVE_CHECK_RETRY_DELAY = 5    # Reduced from 10

MAX_DESCRIPTION_CHARS = 12_000
MAX_KNOWN_SKILLS = 80
MAX_KNOWN_SKILL_CHARS = 60
MAX_NAME_CHARS = 60
MAX_EVIDENCE_CHARS = 300
MAX_SKILLS_OUT = 40
MIN_CONFIDENCE = 0.5
MAX_ATTEMPTS = 2        # Reduced from 3
REQUEST_TIMEOUT_MS = 500_000
MAX_OUTPUT_TOKENS = 4096

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
