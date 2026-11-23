# =====================================================================
# PHASE 1: USER PROFILE FILTERING - CONFIGURATION & CONSTANTS
# =====================================================================

# Profile Levels and Mapping
PROFESSIONAL_LEVELS = {
    "entry": {"rank": 1, "aliases": ["entry level", "junior", "associate", "graduate"]},
    "mid": {"rank": 2, "aliases": ["mid-level", "intermediate", "mid senior"]},
    "senior": {"rank": 3, "aliases": ["senior level", "senior+", "principal engineer"]},
    "lead": {"rank": 4, "aliases": ["tech lead", "engineering lead", "team lead"]},
    "executive": {"rank": 5, "aliases": ["vp", "director", "c-level", "cto", "ceo"]}
}

# Remote Work Preferences
REMOTE_PREFERENCES = {
    "remote": {"priority": 1, "keywords": ["remote", "work from home", "wfh", "fully remote", "100% remote"]},
    "hybrid": {"priority": 2, "keywords": ["hybrid", "flexible", "3 days", "2 days", "mixed"]},
    "onsite": {"priority": 3, "keywords": ["onsite", "office", "in-person", "on-site"]},
    "any": {"priority": 4, "keywords": []}
}

# Company Size Categories
COMPANY_SIZES = {
    "startup": {"employees_range": (1, 100), "keywords": ["startup", "seed-funded", "early-stage", "pre-series"]},
    "smb": {"employees_range": (100, 500), "keywords": ["small business", "smb", "growing company"]},
    "mid_size": {"employees_range": (500, 5000), "keywords": ["mid-size", "mid market", "scale-up"]},
    "enterprise": {"employees_range": (5000, float('inf')), "keywords": ["enterprise", "fortune 500", "global", "multinational"]}
}

# Industry Categories
INDUSTRIES = [
    "Technology",
    "SaaS",
    "FinTech",
    "Healthcare",
    "E-commerce",
    "EdTech",
    "AI/ML",
    "Cloud Computing",
    "Cybersecurity",
    "Telecommunications",
    "Finance",
    "Consulting",
    "Manufacturing",
    "Logistics",
    "Gaming",
    "Media & Entertainment",
    "Government",
    "Non-Profit"
]

# Job Type Preferences
JOB_TYPES = [
    "Full Time",
    "Contract",
    "Part-time",
    "Internship",
    "Temporary",
    "Freelance"
]

# Form Stages for Multi-Step Profile Creation
FORM_STAGES = {
    "basic_info": {
        "step": 1,
        "title": "Basic Information",
        "fields": ["name", "email", "phone", "current_location", "timezone"]
    },
    "experience": {
        "step": 2,
        "title": "Experience & Level",
        "fields": ["years_of_experience", "current_level", "target_level"]
    },
    "skills": {
        "step": 3,
        "title": "Skills & Technologies",
        "fields": ["primary_skills", "secondary_skills", "must_have_skills", "avoid_skills"]
    },
    "preferences": {
        "step": 4,
        "title": "Job Preferences",
        "fields": ["target_job_titles", "target_companies", "exclude_companies", 
                   "willing_locations", "willing_remote_level", "willing_relocation",
                   "job_type_preference", "min_salary", "currency"]
    },
    "company": {
        "step": 5,
        "title": "Company Preferences",
        "fields": ["industry_preferences", "avoid_industries", "company_size_preference",
                   "work_culture_keywords", "benefits_importance"]
    },
    "review": {
        "step": 6,
        "title": "Review & Confirm",
        "fields": ["auto_filter_enabled", "profile_score_threshold", "notes"]
    }
}

# Profile Scoring Weights (for heuristic-based scoring)
PROFILE_SCORING_WEIGHTS = {
    "job_title_match": 0.25,           # Weight for job title matching
    "skills_match": 0.30,              # Weight for skills matching
    "level_match": 0.15,               # Weight for experience level matching
    "location_match": 0.10,            # Weight for location/remote preference
    "company_match": 0.10,             # Weight for company preferences
    "industry_match": 0.10              # Weight for industry preferences
}

# Skill Matching Thresholds
SKILL_MATCHING = {
    "exact_match_score": 100,           # Exact skill match
    "partial_match_score": 75,          # Partial/similar skill match
    "related_match_score": 50,          # Related technology/skill
    "no_match_score": 0                 # No match
}

# Job Title Normalization & Similar Titles
JOB_TITLE_VARIANTS = {
    "software engineer": [
        "software engineer", "sw engineer", "soft. engineer",
        "software developer", "application developer", "app developer",
        "full stack engineer", "full stack developer", "backend engineer",
        "backend developer", "frontend engineer", "frontend developer",
        "web developer", "web engineer", "systems engineer"
    ],
    "data scientist": [
        "data scientist", "ml engineer", "machine learning engineer",
        "ai engineer", "artificial intelligence engineer",
        "data analyst", "analytics engineer", "ai/ml engineer"
    ],
    "product manager": [
        "product manager", "pm", "associate pm", "senior pm",
        "product lead", "product owner", "program manager"
    ],
    "devops engineer": [
        "devops engineer", "devops", "site reliability engineer", "sre",
        "platform engineer", "infrastructure engineer", "cloud engineer"
    ]
}

# Keywords to Avoid in Job Descriptions
NEGATIVE_KEYWORDS = [
    "startup (unpaid equity only)",
    "unpaid internship",
    "commission only",
    "MLM",
    "multi-level marketing"
]

# Matching Configuration
PROFILE_MATCHING_CONFIG = {
    "min_profile_score": 50,            # Minimum score to consider a job
    "score_threshold_for_apply": 70,    # Score threshold for recommending to apply
    "use_llm_for_scoring": False,       # Use LLM or heuristic-based scoring (Phase 1 uses heuristic)
    "cache_profile_matches": True,      # Cache matching results in-memory
    "re_evaluate_after_days": 7         # Re-evaluate job match after N days
}

# Default Profile Score Thresholds (can be overridden per user)
DEFAULT_PROFILE_SCORE_THRESHOLD = 70

# Skills Database (Common Tech Skills)
COMMON_TECH_SKILLS = {
    # Programming Languages
    "python": ["python", "py", "python3"],
    "javascript": ["javascript", "js", "node.js", "nodejs"],
    "typescript": ["typescript", "ts"],
    "java": ["java"],
    "cpp": ["c++", "cpp"],
    "golang": ["go", "golang"],
    "rust": ["rust"],
    "ruby": ["ruby", "rails", "ruby on rails"],
    "php": ["php"],
    "swift": ["swift"],
    "kotlin": ["kotlin"],
    
    # Frontend
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "angular": ["angular"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "scss", "sass"],
    
    # Backend
    "nodejs": ["node.js", "nodejs", "node"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring": ["spring", "spring boot", "java spring"],
    "express": ["express", "express.js"],
    
    # Databases
    "postgresql": ["postgresql", "postgres", "pg", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch"],
    
    # Cloud & DevOps
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud"],
    "azure": ["azure", "microsoft azure"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    
    # Data & ML
    "machine_learning": ["machine learning", "ml"],
    "deep_learning": ["deep learning"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit_learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
}

# Location Matching (Regional Mappings)
REGION_MAPPINGS = {
    "india": ["india", "bangalore", "mumbai", "delhi", "pune", "hyderabad", "chennai"],
    "usa": ["usa", "united states", "new york", "california", "san francisco", "seattle"],
    "europe": ["europe", "uk", "london", "germany", "berlin", "france", "paris"],
    "asia_pacific": ["singapore", "australia", "japan", "hong kong", "tokyo", "sydney"],
    "remote": ["remote", "work from home", "wfh", "fully remote", "anywhere"]
}
