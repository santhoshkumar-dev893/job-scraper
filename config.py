import os
from dotenv import load_dotenv

load_dotenv()

# --- DO NOT MODIFY THE BELOW SECTION ---

# =================================================================
# 1. CORE SYSTEM CONFIGURATION (Do Not Modify)
# =================================================================
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_TABLE_NAME: str = "jobs"
SUPABASE_CUSTOMIZED_RESUMES_TABLE_NAME = "customized_resumes"
SUPABASE_STORAGE_BUCKET = "personalized_resumes"
SUPABASE_RESUME_STORAGE_BUCKET = "resumes"
SUPABASE_BASE_RESUME_TABLE_NAME = "base_resume"
SUPABASE_RESUME_STYLE_TABLE_NAME = "resume_style_settings"
BASE_RESUME_PATH = "resume.json"

# API keys — set only the key(s) needed for your chosen provider.
LLM_API_KEY = (
    os.environ.get("LLM_API_KEY")
    or os.environ.get("FIREWORKS_API_KEY")
    or os.environ.get("FIREWORKS_AI_API_KEY")
    or os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GEMINI_FIRST_API_KEY")
)

# =================================================================
# 2. USER PREFERENCES (Editable)
# =================================================================

# --- LLM Settings ---
# Use any model supported by LiteLLM (gemini, openai/gpt-4o-mini, groq/llama-3.3-70b-versatile)
# Full list of supported models & naming: https://docs.litellm.ai/docs/providers
LLM_MODEL = os.environ.get("LLM_MODEL") or "fireworks_ai/accounts/fireworks/models/glm-5p3-flash"

# --- Search Configuration ---
LINKEDIN_SEARCH_QUERIES = ["AI Engineer", "Senior Software Engineer", "Software Engineer"]
LINKEDIN_LOCATION = "India"
LINKEDIN_GEO_ID = 102713980      # Singapore: 102454443, Dubai: 100205264
LINKEDIN_JOB_TYPE = "F" # F=Full-time, C=Contract, P=Part-time, T=Temporary, I=Internship
LINKEDIN_JOB_POSTING_DATE = "r86400" # r86400=Past 24h, r604800=Past week
LINKEDIN_F_WT = "1,2,3" # 1=Onsite, 2=Remote, 3=Hybrid (use "1,2,3" or [1, 2, 3] for all, or None for no filter)

CAREERS_FUTURE_SEARCH_QUERIES = ["IT Support", "Full Stack Web Developer", "Application Support", "Cybersecurity Analyst", "fresher developer"]
CAREERS_FUTURE_SEARCH_CATEGORIES = ["Information Technology"]
CAREERS_FUTURE_SEARCH_EMPLOYMENT_TYPES = ["Full Time"]

# --- Processing Limits ---
SCRAPING_SOURCES = ["linkedin", "careers_future"] # "linkedin", "careers_future"
JOBS_TO_SCORE_PER_RUN = 10
JOBS_TO_CUSTOMIZE_PER_RUN = 2
MAX_JOBS_PER_SEARCH = {
    "linkedin": 10,
    "careers_future": 20,
}

# =================================================================
# 3. ADVANCED SYSTEM SETTINGS (Modify with Caution)
# =================================================================
LLM_MAX_RPM = 10
LLM_MAX_RETRIES = 3
LLM_RETRY_BASE_DELAY = 10
LLM_DAILY_REQUEST_BUDGET = 0
LLM_REQUEST_DELAY_SECONDS = 8

LINKEDIN_MAX_START = 25 
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 60          # Base cool-down on HTTP 429
DETAIL_FETCH_MIN_DELAY = 12.0     # Minimum delay between detail requests (seconds)
DETAIL_FETCH_MAX_DELAY = 22.0     # Maximum delay between detail requests (seconds)
SEARCH_QUERY_MIN_DELAY = 15.0     # Delay between search queries in standalone runs (seconds)
SEARCH_QUERY_MAX_DELAY = 30.0

JOB_EXPIRY_DAYS = 30
JOB_CHECK_DAYS = 3
JOB_DELETION_DAYS = 60
JOB_CHECK_LIMIT = 50
ACTIVE_CHECK_TIMEOUT = 20
ACTIVE_CHECK_MAX_RETRIES = 2
ACTIVE_CHECK_RETRY_DELAY = 10



MAX_DESCRIPTION_CHARS = 12_000
MAX_KNOWN_SKILLS = 80
MAX_KNOWN_SKILL_CHARS = 60
MAX_NAME_CHARS = 60
MAX_EVIDENCE_CHARS = 300
MAX_SKILLS_OUT = 40
MIN_CONFIDENCE = 0.5
MAX_ATTEMPTS = 3
REQUEST_TIMEOUT_MS = 500_000
MAX_OUTPUT_TOKENS = 4096


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

# =================================================================
# 4. PROMPT CACHING CONFIGURATION (New Section)
# =================================================================

# Prompt Caching Settings
ENABLE_PROMPT_CACHING = os.getenv("ENABLE_PROMPT_CACHING", "false").lower() == "true"

# Cache Provider: Choose one based on your LLM provider
# "claude" = Anthropic Claude (RECOMMENDED - best TTL + pricing)
# "openai" = OpenAI GPT-4 Turbo
# "gemini" = Google Gemini  
# None = Disable caching
CACHE_PROVIDER = os.getenv("CACHE_PROVIDER", "fireworks")

# Cache Size Limits (tokens)
CACHE_MAX_TOKENS_SYSTEM = 1000          # System instruction cache size
CACHE_MAX_TOKENS_SKILLS = 3000          # Known skills cache size
CACHE_MIN_TOKENS_TO_CACHE = 500         # Don't cache if smaller than this

# Cache Invalidation Strategy
CACHE_REVALIDATE_INTERVAL = 86400       # Revalidate every 24 hours (seconds)
CACHE_REVALIDATE_JOB_COUNT = 100        # Or revalidate every N jobs
CACHE_INVALIDATE_ON_NEW_SKILL = True    # Invalidate when new skill discovered

# Metrics & Monitoring
CACHE_TRACK_METRICS = True              # Track cache hit/miss rates
CACHE_LOG_HITS = True                   # Log cache hits for debugging
