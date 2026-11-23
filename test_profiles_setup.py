"""
test_profiles_setup.py

Setup test profiles for testing multi-user profile scoring.
Creates 2 distinct profiles with different skills and preferences.
"""

import uuid
from datetime import datetime
from models import UserProfile

# =====================================================================
# TEST PROFILE 1: John (Python/Backend Developer)
# =====================================================================

PROFILE_1_ID = str(uuid.uuid4())  # Generate unique ID

PROFILE_1: UserProfile = UserProfile(
    id=uuid.UUID(PROFILE_1_ID),
    
    # Basic Info
    name="John Smith",
    email="john.smith@example.com",
    phone="+1-555-0101",
    current_location="San Francisco, USA",
    timezone="America/Los_Angeles",
    
    # Experience
    years_of_experience=5,
    current_level="mid",
    target_level="senior",
    
    # Skills
    primary_skills=["Python", "JavaScript", "React", "Django", "PostgreSQL"],
    secondary_skills=["Docker", "Redis", "AWS", "Git"],
    must_have_skills=["Python", "JavaScript"],
    avoid_skills=["COBOL", "Perl"],
    
    # Job Preferences
    target_job_titles=[
        "Senior Python Developer",
        "Backend Engineer",
        "Full Stack Engineer",
        "Python Engineer"
    ],
    target_companies=[
        "Google",
        "Meta",
        "Amazon",
        "Microsoft",
        "Stripe"
    ],
    exclude_companies=[
        "Company X",
        "Old Corp"
    ],
    willing_locations=["Singapore", "India", "Remote"],
    willing_remote_level="remote",  # Prefers full remote
    willing_relocation=False,
    willing_travel=False,
    job_type_preference=["Full Time"],
    min_salary=100000,
    currency="USD",
    
    # Company Preferences
    industry_preferences=["Technology", "SaaS", "FinTech"],
    avoid_industries=["Gaming", "Gambling"],
    company_size_preference=["Mid-size", "Enterprise"],
    work_culture_keywords=["Innovation", "Collaboration", "Learning"],
    benefits_importance=["Health Insurance", "401k", "Stock Options", "Remote Work"],
    
    # Profile Scoring Settings (NEW)
    career_goals="Become a senior backend engineer, lead technical projects, grow team leadership skills",
    preferred_company_size="Mid-size",
    red_flag_keywords=["unpaid", "equity only", "startup risk", "legacy system"],
    min_skill_match_percentage=70,
    
    # Settings
    auto_filter_enabled=True,
    profile_score_threshold=75,
    is_active=True,
    notes="Senior mid-level developer looking for senior roles. Prefers backend/full-stack."
)

# =====================================================================
# TEST PROFILE 2: Jane (Java/Data Engineer)
# =====================================================================

PROFILE_2_ID = str(uuid.uuid4())  # Generate unique ID

PROFILE_2: UserProfile = UserProfile(
    id=uuid.UUID(PROFILE_2_ID),
    
    # Basic Info
    name="Jane Wong",
    email="jane.wong@example.com",
    phone="+1-555-0202",
    current_location="Seattle, USA",
    timezone="America/Los_Angeles",
    
    # Experience
    years_of_experience=8,
    current_level="senior",
    target_level="lead",
    
    # Skills
    primary_skills=["Java", "Python", "Scala", "SQL", "Spark"],
    secondary_skills=["Kafka", "Flink", "Hadoop", "Cloud Storage"],
    must_have_skills=["Java", "SQL"],
    avoid_skills=["MATLAB", "Fortran"],
    
    # Job Preferences
    target_job_titles=[
        "Senior Data Engineer",
        "Lead Data Engineer",
        "Data Architecture",
        "Data Platform Engineer"
    ],
    target_companies=[
        "Databricks",
        "Airbnb",
        "Uber",
        "Netflix",
        "LinkedIn"
    ],
    exclude_companies=[
        "Small Startup",
        "Legacy Finance"
    ],
    willing_locations=["India", "Remote"],
    willing_remote_level="hybrid",  # Prefers hybrid
    willing_relocation=True,
    willing_travel=True,
    job_type_preference=["Full Time"],
    min_salary=140000,
    currency="USD",
    
    # Company Preferences
    industry_preferences=["Technology", "Data Science", "E-Commerce"],
    avoid_industries=["Traditional Finance"],
    company_size_preference=["Enterprise"],
    work_culture_keywords=["Data-driven", "Scale", "Innovation", "Impact"],
    benefits_importance=["Health Insurance", "Stock Options", "Flexible Hours"],
    
    # Profile Scoring Settings (NEW)
    career_goals="Lead data engineering teams, architect scalable data platforms, mentor junior engineers",
    preferred_company_size="Enterprise",
    red_flag_keywords=["maintenance only", "outdated tech stack", "no growth"],
    min_skill_match_percentage=60,
    
    # Settings
    auto_filter_enabled=True,
    profile_score_threshold=70,
    is_active=True,
    notes="Senior data engineer with 8 years experience. Looking for lead/principal roles."
)

# =====================================================================
# PROFILE SUMMARY
# =====================================================================

PROFILES = {
    "john": {
        "profile_id": PROFILE_1_ID,
        "name": "John Smith",
        "email": "john.smith@example.com",
        "focus": "Backend/Python Developer",
        "years_exp": 5,
        "level": "mid",
        "primary_skills": ["Python", "JavaScript", "React"],
        "min_salary": 100000,
        "profile_score_threshold": 75,
        "remote_preference": "remote"
    },
    "jane": {
        "profile_id": PROFILE_2_ID,
        "name": "Jane Wong",
        "email": "jane.wong@example.com",
        "focus": "Data Engineer",
        "years_exp": 8,
        "level": "senior",
        "primary_skills": ["Java", "Python", "Scala", "SQL"],
        "min_salary": 140000,
        "profile_score_threshold": 70,
        "remote_preference": "hybrid"
    }
}

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def get_profile_by_name(name: str) -> UserProfile:
    """Get a test profile by name (john or jane)"""
    if name.lower() == "john":
        return PROFILE_1
    elif name.lower() == "jane":
        return PROFILE_2
    else:
        raise ValueError(f"Unknown profile: {name}")


def get_profile_by_id(profile_id: str) -> UserProfile:
    """Get a test profile by ID"""
    if profile_id == PROFILE_1_ID:
        return PROFILE_1
    elif profile_id == PROFILE_2_ID:
        return PROFILE_2
    else:
        raise ValueError(f"Unknown profile ID: {profile_id}")


def print_profile_summary(profile: UserProfile):
    """Pretty print a profile summary"""
    print("\n" + "="*80)
    print(f"PROFILE: {profile.name}")
    print("="*80)
    print(f"Email: {profile.email}")
    print(f"Location: {profile.current_location}")
    print(f"Experience: {profile.years_of_experience} years")
    print(f"Current Level: {profile.current_level.upper()}")
    print(f"Target Level: {profile.target_level.upper()}")
    print(f"\nTarget Job Titles: {', '.join(profile.target_job_titles[:3])}...")
    print(f"Primary Skills: {', '.join(profile.primary_skills[:5])}")
    print(f"Must-Have Skills: {', '.join(profile.must_have_skills)}")
    print(f"\nPreferred Locations: {', '.join(profile.willing_locations)}")
    print(f"Remote Preference: {profile.willing_remote_level}")
    print(f"Salary Range: ${profile.min_salary:,}K+")
    print(f"Industries: {', '.join(profile.industry_preferences)}")
    print(f"Company Size: {', '.join(profile.company_size_preference)}")
    print(f"\nCareer Goals: {profile.career_goals}")
    print(f"Profile Score Threshold: {profile.profile_score_threshold}/100")
    print(f"Min Skill Match: {profile.min_skill_match_percentage}%")
    print(f"Red Flag Keywords: {', '.join(profile.red_flag_keywords)}")
    print(f"\nActive: {profile.is_active}")
    print(f"Notes: {profile.notes}")
    print("="*80 + "\n")


# =====================================================================
# EXAMPLE USAGE
# =====================================================================

if __name__ == "__main__":
    print("\n" + "🎯 TEST PROFILES FOR PROFILE SCORING" + "\n")
    
    # Print both profiles
    print_profile_summary(PROFILE_1)
    print_profile_summary(PROFILE_2)
    
    # Show summary table
    print("\n" + "="*80)
    print("QUICK COMPARISON")
    print("="*80)
    print(f"{'Aspect':<30} {'John (Python)':<25} {'Jane (Data)':<25}")
    print("-"*80)
    print(f"{'Experience':<30} {PROFILE_1.years_of_experience} years{'':<12} {PROFILE_2.years_of_experience} years")
    print(f"{'Level':<30} {PROFILE_1.current_level.upper():<25} {PROFILE_2.current_level.upper():<25}")
    print(f"{'Primary Skills':<30} Python, JS, React{'':<7} Java, Scala, SQL")
    print(f"{'Target Role':<30} Backend/Senior Python{'':<5} Data Engineer/Lead")
    print(f"{'Salary Range':<30} $100K+{'':<18} $140K+")
    print(f"{'Remote Preference':<30} Full Remote{'':<14} Hybrid")
    print(f"{'Company Size':<30} Mid-size, Enterprise{'':<4} Enterprise")
    print(f"{'Score Threshold':<30} {PROFILE_1.profile_score_threshold}/100{'':<18} {PROFILE_2.profile_score_threshold}/100")
    print("="*80 + "\n")
    
    # Show how to use
    print("HOW TO USE IN TESTS:")
    print("-" * 80)
    print("""
from test_profiles_setup import PROFILE_1, PROFILE_2, get_profile_by_name, PROFILES

# Option 1: Use the profile objects directly
scorer = ProfileJobScorer()
john_score = scorer.score_single_job(test_job, PROFILE_1)
jane_score = scorer.score_single_job(test_job, PROFILE_2)

# Option 2: Get profile by name
john_profile = get_profile_by_name("john")
jane_profile = get_profile_by_name("jane")

# Option 3: Get profile IDs for database operations
john_id = PROFILES["john"]["profile_id"]
jane_id = PROFILES["jane"]["profile_id"]

# Option 4: Access profile info
print(PROFILES["john"]["primary_skills"])  # ['Python', 'JavaScript', 'React']
print(PROFILES["jane"]["years_exp"])       # 8
    """)
    print("-" * 80)
