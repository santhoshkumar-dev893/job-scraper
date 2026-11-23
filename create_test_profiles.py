"""
Create 2 test profiles in Supabase database for testing profile-level scoring.

This script:
1. Creates Profile 1: Python Backend Developer (Senior)
2. Creates Profile 2: Java Full-Stack Developer (Mid-level)
3. Both profiles are inserted directly into Supabase user_profiles table
4. Ready for scoring real jobs from the database
"""

import supabase_utils
from uuid import uuid4
import logging
from datetime import datetime,timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
now = datetime.now(timezone.utc)
# =====================================================================
# TEST PROFILE 1: PYTHON BACKEND DEVELOPER (SENIOR)
# =====================================================================
PROFILE_1 = {
    "id": str(uuid4()),  # Generate UUID
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0101",
    "current_location": "San Francisco, USA",
    "timezone": "America/Los_Angeles",
    
    # Experience
    "years_of_experience": 8,
    "current_title": "Senior Software Engineer",
    "current_level": "senior",
    "target_level": "senior",
    
    # Skills
    "primary_skills": ["Python", "JavaScript", "PostgreSQL", "Redis", "Docker"],
    "secondary_skills": ["React", "GraphQL", "Kubernetes", "AWS"],
    "must_have_skills": ["Python", "PostgreSQL"],
    "avoid_skills": ["PHP", "COBOL"],
    
    # Job Preferences
    "target_job_titles": ["Senior Backend Engineer", "Senior Software Engineer", "Tech Lead"],
    "target_companies": ["Google", "Amazon", "Microsoft", "Meta", "Stripe", "GitLab"],
    "exclude_companies": ["WeChat", "Alibaba"],
    "willing_locations": ["USA", "Canada", "UK", "Germany"],
    "willing_remote_level": "remote",
    "willing_relocation": False,
    "willing_travel": True,
    "job_type_preference": ["Full Time"],
    "min_salary": 150000,
    "currency": "USD",
    
    # Company Preferences
    "industry_preferences": ["Technology", "SaaS", "FinTech"],
    "avoid_industries": ["Gambling", "Tobacco"],
    "company_size_preference": ["Mid-size", "Enterprise"],
    "work_culture_keywords": ["Innovation", "Collaboration", "Fast-paced", "Learning"],
    "benefits_importance": ["Health Insurance", "401k", "Stock Options", "Remote Work", "Learning Budget"],
    
    # Career Goals (for profile scoring)
    "career_goals": "Lead backend architecture projects, mentor junior engineers, move towards tech lead/architect role",
    "preferred_company_size": "Mid-size",
    "red_flag_keywords": ["unpaid", "equity only", "startup with no funding", "mandatory office"],
    "min_skill_match_percentage": 70,
    
    # Settings
    "auto_filter_enabled": True,
    "profile_score_threshold": 75,
    "is_active": True,
    "notes": "Test Profile 1: Senior Python Backend Engineer - Looking for remote roles with growth opportunities",
    "form_stage": "review",
    
    # Timestamps
    "created_at": now.isoformat(),
    "updated_at": now.isoformat(),
    "last_used_at": now.isoformat(),
}

# =====================================================================
# TEST PROFILE 2: JAVA FULL-STACK DEVELOPER (MID-LEVEL)
# =====================================================================
PROFILE_2 = {
    "id": str(uuid4()),  # Generate UUID
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "+1-555-0102",
    "current_location": "New York, USA",
    "timezone": "America/New_York",
    
    # Experience
    "years_of_experience": 5,
    "current_title": "Software Engineer",
    "current_level": "mid",
    "target_level": "senior",
    
    # Skills
    "primary_skills": ["Java", "React", "Spring Boot", "MySQL", "JavaScript"],
    "secondary_skills": ["MongoDB", "Docker", "Angular", "HTML/CSS"],
    "must_have_skills": ["Java", "React"],
    "avoid_skills": ["Python", "C++", "Assembly"],
    
    # Job Preferences
    "target_job_titles": ["Software Engineer", "Full Stack Engineer", "Backend Engineer"],
    "target_companies": ["Netflix", "Airbnb", "Twitter", "Uber", "LinkedIn", "Apple"],
    "exclude_companies": ["WeChat"],
    "willing_locations": ["USA", "Canada"],
    "willing_remote_level": "hybrid",
    "willing_relocation": True,
    "willing_travel": False,
    "job_type_preference": ["Full Time"],
    "min_salary": 110000,
    "currency": "USD",
    
    # Company Preferences
    "industry_preferences": ["Technology", "Media", "E-commerce"],
    "avoid_industries": ["Gambling"],
    "company_size_preference": ["Startup", "Mid-size", "Enterprise"],
    "work_culture_keywords": ["Growth", "Quality Code", "Agile"],
    "benefits_importance": ["Health Insurance", "PTO", "Professional Development"],
    
    # Career Goals (for profile scoring)
    "career_goals": "Transition to full-stack development, gain experience with modern frontend frameworks, move to senior engineer role",
    "preferred_company_size": "Mid-size",
    "red_flag_keywords": ["unpaid", "no benefits", "overworked"],
    "min_skill_match_percentage": 60,
    
    # Settings
    "auto_filter_enabled": True,
    "profile_score_threshold": 70,
    "is_active": True,
    "notes": "Test Profile 2: Mid-level Java Full-Stack Developer - Looking for growth opportunities",
    "form_stage": "review",
    
    # Timestamps
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "last_used_at": datetime.utcnow().isoformat(),
}


def create_profiles():
    """
    Insert 2 test profiles directly into Supabase database.
    """
    try:
        logger.info("=" * 80)
        logger.info("CREATING TEST PROFILES IN SUPABASE")
        logger.info("=" * 80)
        
        # Create Profile 1
        logger.info("\n📝 Creating Profile 1: John Doe (Senior Python Backend Developer)...")
        # response1 = supabase_utils.supabase.table("user_profiles").insert(PROFILE_1).execute()
        response1 = supabase_utils.create_user_profile(PROFILE_1)
        
        
        if hasattr(response1, 'error') and response1.error:
            logger.error(f"Error creating Profile 1: {response1.error}")
            return False
        
        profile1_id = PROFILE_1["id"]
        logger.info(f"✅ Profile 1 created successfully!")
        logger.info(f"   Profile ID: {profile1_id}")
        logger.info(f"   Name: {PROFILE_1['name']}")
        logger.info(f"   Email: {PROFILE_1['email']}")
        logger.info(f"   Current Title: {PROFILE_1['current_title']}")
        logger.info(f"   Skills: {', '.join(PROFILE_1['primary_skills'][:3])}...")
        
        # Create Profile 2
        logger.info("\n📝 Creating Profile 2: Jane Smith (Mid-level Java Full-Stack Developer)...")
        response2 = supabase_utils.supabase.table("user_profiles").insert(PROFILE_2).execute()
        
        if hasattr(response2, 'error') and response2.error:
            logger.error(f"Error creating Profile 2: {response2.error}")
            return False
        
        profile2_id = PROFILE_2["id"]
        logger.info(f"✅ Profile 2 created successfully!")
        logger.info(f"   Profile ID: {profile2_id}")
        logger.info(f"   Name: {PROFILE_2['name']}")
        logger.info(f"   Email: {PROFILE_2['email']}")
        logger.info(f"   Current Title: {PROFILE_2['current_title']}")
        logger.info(f"   Skills: {', '.join(PROFILE_2['primary_skills'][:3])}...")
        
        logger.info("\n" + "=" * 80)
        logger.info("SUCCESS: Both profiles created in database!")
        logger.info("=" * 80)
        
        print_profile_summary(profile1_id, profile2_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating profiles: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_profile_summary(profile1_id, profile2_id):
    """Print a summary of created profiles with test scenarios."""
    
    summary = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                     TEST PROFILES CREATED IN DATABASE                      ║
╚════════════════════════════════════════════════════════════════════════════╝

📌 PROFILE 1: Senior Python Backend Developer
   ─────────────────────────────────────────
   Profile ID: {profile1_id}
   Name: John Doe
   Email: john.doe@example.com
   Experience: 8 years (Senior Level)
   Location: San Francisco, USA
   Work Mode: Remote (preferred)
   
   Skills:
   ├─ Primary: Python, JavaScript, PostgreSQL, Redis, Docker
   ├─ Secondary: React, GraphQL, Kubernetes, AWS
   └─ Must-Have: Python, PostgreSQL
   
   Job Preferences:
   ├─ Titles: Senior Backend Engineer, Tech Lead
   ├─ Companies: Google, Amazon, Microsoft, Meta, Stripe
   ├─ Locations: USA, Canada, UK, Germany
   ├─ Salary Range: $150K - ∞ USD
   └─ Company Size: Mid-size, Enterprise
   
   Career Goal: "Lead backend architecture, mentor engineers, move to tech lead/architect"
   Red Flags: "unpaid", "equity only", "mandatory office"
   Min Skill Match: 70%
   Score Threshold: 75/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 PROFILE 2: Mid-level Java Full-Stack Developer
   ──────────────────────────────────────────────
   Profile ID: {profile2_id}
   Name: Jane Smith
   Email: jane.smith@example.com
   Experience: 5 years (Mid Level)
   Location: New York, USA
   Work Mode: Hybrid (preferred)
   
   Skills:
   ├─ Primary: Java, React, Spring Boot, MySQL, JavaScript
   ├─ Secondary: MongoDB, Docker, Angular, HTML/CSS
   └─ Must-Have: Java, React
   
   Job Preferences:
   ├─ Titles: Software Engineer, Full Stack Engineer
   ├─ Companies: Netflix, Airbnb, Twitter, Uber, LinkedIn
   ├─ Locations: USA, Canada (willing to relocate)
   ├─ Salary Range: $110K - ∞ USD
   └─ Company Size: Startup, Mid-size, Enterprise
   
   Career Goal: "Transition to full-stack, gain modern frontend experience, become senior"
   Red Flags: "unpaid", "no benefits", "overworked"
   Min Skill Match: 60%
   Score Threshold: 70/100

╔════════════════════════════════════════════════════════════════════════════╗
║                            TESTING SCENARIOS                               ║
╚════════════════════════════════════════════════════════════════════════════╝

🧪 SCENARIO 1: Python Backend Job
   ──────────────────────────────
   Job Example: "Senior Python Engineer at Google"
   
   Expected Scores:
   ├─ John (Profile 1):  HIGH (85-95/100)
   │  └─ Reason: Perfect tech stack match, right seniority, target company
   │
   └─ Jane (Profile 2):  LOW (20-35/100)
      └─ Reason: Python not in her skills, wrong role for her experience

🧪 SCENARIO 2: Java Full-Stack Job
   ────────────────────────────────
   Job Example: "Full Stack Engineer at Netflix"
   
   Expected Scores:
   ├─ Jane (Profile 2):  HIGH (80-92/100)
   │  └─ Reason: Java + React match, target company, right level
   │
   └─ John (Profile 1):  MEDIUM (45-60/100)
      └─ Reason: Has JavaScript but Java not in his skills, not backend-focused

🧪 SCENARIO 3: DevOps/Infrastructure Job
   ──────────────────────────────────────
   Job Example: "DevOps Engineer at Microsoft"
   
   Expected Scores:
   ├─ John (Profile 1):  MEDIUM-HIGH (65-80/100)
   │  └─ Reason: Has Docker, Kubernetes but not primary focus
   │
   └─ Jane (Profile 2):  LOW-MEDIUM (35-50/100)
      └─ Reason: Docker experience but not her focus area

╔════════════════════════════════════════════════════════════════════════════╗
║                          NEXT STEPS FOR TESTING                            ║
╚════════════════════════════════════════════════════════════════════════════╝

1️⃣ Verify Profiles Created
   └─ Run: python -c "import supabase_utils; print(supabase_utils.get_user_profile('{profile1_id}'))"

2️⃣ Score Jobs Against Profiles
   └─ Run: python test_multi_user_scoring.py

3️⃣ Query Top Jobs for Each Profile
   └─ john_top = supabase_utils.get_top_jobs_for_profile('{profile1_id}', 10)
   └─ jane_top = supabase_utils.get_top_jobs_for_profile('{profile2_id}', 10)

4️⃣ Check Profile Scoring Statistics
   └─ john_stats = supabase_utils.get_profile_scoring_stats_v2('{profile1_id}')
   └─ jane_stats = supabase_utils.get_profile_scoring_stats_v2('{profile2_id}')

5️⃣ View Multi-User Job Analysis
   └─ scores = supabase_utils.get_job_scores_across_profiles('some-job-id')
   └─ Shows how same job scored for both profiles!

╔════════════════════════════════════════════════════════════════════════════╗
║                         DATABASE VERIFICATION                              ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ Check Supabase Dashboard:
   ├─ Go to: Tables → user_profiles
   ├─ Filter by: email = 'john.doe@example.com' OR 'jane.smith@example.com'
   ├─ Verify: Both profiles exist with all fields populated
   └─ Note the Profile IDs displayed above

✅ Run Test Query:
   SELECT id, name, email, current_title, years_of_experience 
   FROM user_profiles 
   WHERE email IN ('john.doe@example.com', 'jane.smith@example.com');

✅ Check Relationships:
   ├─ These profiles will be linked to jobs via: profile_job_scores table
   ├─ Each scored job creates: (profile_id, job_id, profile_score) row
   └─ Different profiles can have different scores for same job!

╔════════════════════════════════════════════════════════════════════════════╗
║                    PROFILE IDs FOR FUTURE REFERENCE                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Profile 1 (John Doe):    {profile1_id}
Profile 2 (Jane Smith):  {profile2_id}

Save these IDs for use in:
  • test_multi_user_scoring.py
  • scraper.py (for testing)
  • job_manager.py (for querying)
  • Any profile-level scoring tests

Use in Python:
  ├─ supabase_utils.get_top_jobs_for_profile('{profile1_id}', 10)
  ├─ supabase_utils.get_top_jobs_for_profile('{profile2_id}', 10)
  └─ supabase_utils.get_job_scores_across_profiles('job_id')

"""
    print(summary)


def verify_profiles_created():
    """Verify both profiles were created successfully."""
    try:
        logger.info("\n🔍 Verifying profiles in database...\n")
        
        # Query Profile 1
        response1 = supabase_utils.supabase.table("user_profiles")\
            .select("id, name, email, current_title, years_of_experience, is_active")\
            .eq("email", PROFILE_1["email"])\
            .execute()
        
        if response1.data:
            profile = response1.data[0]
            logger.info(f"✅ Profile 1 VERIFIED in database:")
            logger.info(f"   ID: {profile['id']}")
            logger.info(f"   Name: {profile['name']}")
            logger.info(f"   Email: {profile['email']}")
            logger.info(f"   Title: {profile['current_title']}")
            logger.info(f"   Experience: {profile['years_of_experience']} years")
            logger.info(f"   Active: {profile['is_active']}")
        else:
            logger.warning("⚠️  Profile 1 not found in database")
        
        # Query Profile 2
        response2 = supabase_utils.supabase.table("user_profiles")\
            .select("id, name, email, current_title, years_of_experience, is_active")\
            .eq("email", PROFILE_2["email"])\
            .execute()
        
        if response2.data:
            profile = response2.data[0]
            logger.info(f"\n✅ Profile 2 VERIFIED in database:")
            logger.info(f"   ID: {profile['id']}")
            logger.info(f"   Name: {profile['name']}")
            logger.info(f"   Email: {profile['email']}")
            logger.info(f"   Title: {profile['current_title']}")
            logger.info(f"   Experience: {profile['years_of_experience']} years")
            logger.info(f"   Active: {profile['is_active']}")
        else:
            logger.warning("⚠️  Profile 2 not found in database")
        
        # Count total profiles
        count_response = supabase_utils.supabase.table("user_profiles")\
            .select("id", count="exact")\
            .execute()
        
        total_count = len(count_response.data) if count_response.data else 0
        logger.info(f"\n📊 Total profiles in database: {total_count}")
        
    except Exception as e:
        logger.error(f"Error verifying profiles: {e}")


if __name__ == "__main__":
    logger.info("\n🚀 Starting Test Profile Creation\n")
    
    # Create profiles
    success = create_profiles()
    
    if success:
        # Verify they were created
        verify_profiles_created()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ TEST PROFILES SUCCESSFULLY CREATED AND VERIFIED!")
        logger.info("=" * 80)
        logger.info("\n📝 Next Step: Use these profiles for testing job scoring")
        logger.info("   - Run: python test_multi_user_scoring.py")
        logger.info("   - Or manually test with scraper.py\n")
    else:
        logger.error("\n" + "=" * 80)
        logger.error("❌ FAILED TO CREATE TEST PROFILES")
        logger.error("=" * 80)
        logger.error("\n🔧 Troubleshooting:")
        logger.error("   1. Check Supabase connection in config.py")
        logger.error("   2. Verify user_profiles table exists")
        logger.error("   3. Check RLS policies allow INSERT\n")
