"""
Integration module: Orchestrate job scoring with database-backed skill management

This module orchestrates:
1. Initialize SkillManager (DB → cache)
2. Initialize SkillDiscovery (for automated skill insertion)
3. Load profiles from DB
4. Score each job against each profile using SkillManager
5. Discover and insert new skills via SkillDiscovery
6. Save results to job_matches table
7. Refresh skill cache every 100 jobs

Architecture: Database is single source of truth for skills
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from supabase import create_client

from models import UserProfile, MatchResult
from job_scorer import JobScorer
from skills_manager import SkillManager
from skill_discovery import SkillDiscovery
from section_splitter import SectionSplitter
from supabase_utils import save_job_matches

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScoringOrchestrator:
    """
    Orchestrates job scoring with database-backed skill management.
    
    Workflow:
    1. Load SkillManager from database (in-memory cache)
    2. Create SkillDiscovery for automated skill insertion
    3. Load profiles from database
    4. For each job batch:
       - Score against each profile using SkillManager
       - Discover and insert new skills via SkillDiscovery
       - Save job_matches results
    5. Refresh cache every 100 jobs (progressive learning)
    """
    
    def __init__(self):
        """Initialize Supabase client and skill management components"""
        load_dotenv()
        
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Initialize skill management (DB-backed)
        logger.info("Loading SkillManager from database...")
        self.skill_manager = SkillManager(self.supabase)
        
        logger.info("Initializing SkillDiscovery for automated skill insertion...")
        self.skill_discovery = SkillDiscovery(self.supabase, self.skill_manager)
        
        self.section_splitter = SectionSplitter()
        self.scorers: Dict[str, JobScorer] = {}
        self.jobs_scored = 0  # For refresh tracking
        
        logger.info("✅ ScoringOrchestrator initialized with database-backed skill management")
    
    def load_profiles(self) -> List[Dict]:
        """Load active profiles from DB"""
        try:
            response = self.supabase.table("user_profiles").select("*").eq("is_active", True).execute()
            profiles = response.data
            logger.info(f"✅ Loaded {len(profiles)} active profiles")
            return profiles
        except Exception as e:
            logger.error(f"❌ Failed to load profiles: {e}")
            return []
    
    def load_jobs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Load active jobs from DB"""
        try:
            # Only fetch needed columns (NOT skills - we extract from description)
            response = self.supabase.table("jobs").select(
                "job_id, job_title, company, description, is_active"
            ).eq("is_active", True).range(offset, offset + limit - 1).execute()
            jobs = response.data
            logger.info(f"✅ Loaded {len(jobs)} active jobs")
            return jobs
        except Exception as e:
            logger.error(f"❌ Failed to load jobs: {e}")
            return []
    
    def initialize_scorer_for_profile(self, profile: Dict) -> Optional[JobScorer]:
        """
        Create and cache scorer for a profile.
        
        Uses SkillManager and SkillDiscovery initialized at startup.
        """
        profile_id = str(profile['id'])
        
        try:
            # Convert DB profile to UserProfile model
            user_profile = UserProfile(
                id=profile['id'],
                name=profile['name'],
                email=profile.get('email'),
                phone=profile.get('phone'),
                current_location=profile.get('current_location'),
                timezone=profile.get('timezone', 'UTC'),
                years_of_experience=profile.get('years_of_experience', 0),
                current_level=profile.get('current_level', 'mid'),
                target_level=profile.get('target_level', 'mid'),
                primary_skills=profile.get('primary_skills', []),
                secondary_skills=profile.get('secondary_skills', []),
                must_have_skills=profile.get('must_have_skills', []),
                target_job_titles=profile.get('target_job_titles', []),
                target_companies=profile.get('target_companies', []),
                exclude_companies=profile.get('exclude_companies', []),
                willing_locations=profile.get('willing_locations', []),
                willing_remote_level=profile.get('willing_remote_level', 'hybrid'),
                willing_relocation=profile.get('willing_relocation', False),
                willing_travel=profile.get('willing_travel', False),
                job_type_preference=profile.get('job_type_preference', ['Full Time']),
                min_salary=profile.get('min_salary', 0),
                currency=profile.get('currency', 'USD'),
                industry_preferences=profile.get('industry_preferences', []),
                avoid_industries=profile.get('avoid_industries', []),
                company_size_preference=profile.get('company_size_preference', []),
                work_culture_keywords=profile.get('work_culture_keywords', []),
                benefits_importance=profile.get('benefits_importance', []),
                is_active=profile.get('is_active', True),
                notes=profile.get('notes'),
                form_stage=profile.get('form_stage', 'basic_info'),
            )
            
            # Create scorer with SkillManager and SkillDiscovery
            scorer = JobScorer(
                profile=user_profile.model_dump(),
                skill_manager=self.skill_manager,
                skill_discovery=self.skill_discovery
            )
            
            self.scorers[profile_id] = scorer
            logger.info(f"✅ Scorer initialized for profile: {profile['name']}")
            return scorer
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize scorer for {profile['name']}: {e}")
            return None
    
    def score_job_for_profile(self, job: Dict, scorer: JobScorer) -> Optional[MatchResult]:
        """Score a single job against a profile"""
        try:
            job_description = job.get('description', '')
            if not job_description:
                logger.warning(f"⚠️  No description for job {job['job_id']}")
                return None
            
            # Score the job
            match_result = scorer.score(
                job_description=job_description,
                job_id=job['job_id']
            )
            
            return match_result
        
        except Exception as e:
            logger.error(f"❌ Failed to score job {job.get('job_id')}: {e}")
            return None
    
    def process_match_result(self, match_result: MatchResult, profile_id: str) -> bool:
        """Save match result to job_matches table"""
        try:
            # Save match to job_matches table
            save_job_matches(
                supabase=self.supabase,
                match_result=match_result,
                profile_id=profile_id
            )
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save match result: {e}")
            return False
    
    def refresh_skill_cache_if_needed(self) -> None:
        """
        Refresh skill cache every 100 jobs for progressive learning.
        
        Call this after each batch of jobs to ensure new skills discovered
        by LLM are immediately available in subsequent jobs' scoring.
        """
        if self.jobs_scored % 100 == 0 and self.jobs_scored > 0:
            logger.info(f"\n� Refreshing skill cache after {self.jobs_scored} jobs...")
            self.skill_manager.refresh_cache()
            logger.info(f"✅ Skill cache refreshed: {len(self.skill_manager.get_all_skills())} skills")
    
    def run_scoring_pipeline(self, limit_jobs: int = 50) -> Dict:
        """
        Run complete scoring pipeline with database-backed skill management.
        
        Process:
        1. Load profiles from DB
        2. Initialize scorers with SkillManager and SkillDiscovery
        3. For each job batch:
           - Score against each profile
           - Discover and insert new skills via SkillDiscovery
           - Save job_matches results
        4. Refresh skill cache every 100 jobs
        
        Args:
            limit_jobs: Number of jobs to process per batch
            
        Returns:
            Dictionary with stats: matches_passed, matches_failed, new_skills_found, etc.
        """
        logger.info("🚀 Starting scoring pipeline with database-backed skill management...")
        
        # Load data
        profiles = self.load_profiles()
        jobs = self.load_jobs(limit=limit_jobs)
        
        if not profiles or not jobs:
            logger.error("❌ No profiles or jobs found")
            return {"status": "failed"}
        
        # Initialize scorers for each profile
        scorers = {}
        for profile in profiles:
            scorer = self.initialize_scorer_for_profile(profile)
            if scorer:
                scorers[str(profile['id'])] = (profile, scorer)
        
        if not scorers:
            logger.error("❌ Failed to initialize any scorers")
            return {"status": "failed"}
        
        # Score all jobs
        stats = {
            "total_jobs": len(jobs),
            "total_profiles": len(scorers),
            "matches_saved": 0,
            "matches_passed": 0,
            "matches_failed": 0,
            "new_skills_discovered": 0,
            "new_skills_skipped": 0,
            "errors": 0,
        }
        
        for job_idx, job in enumerate(jobs, 1):
            logger.info(f"\n[{job_idx}/{len(jobs)}] Scoring: {job.get('job_title')} @ {job.get('company')}")
            
            for profile_id, (profile, scorer) in scorers.items():
                try:
                    # Score job
                    match_result = self.score_job_for_profile(job, scorer)
                    
                    if match_result:
                        # Save result to job_matches
                        if self.process_match_result(match_result, profile_id):
                            stats["matches_saved"] += 1
                            
                            # Track results
                            if match_result.gate_passed:
                                stats["matches_passed"] += 1
                                logger.info(f"  ✅ PASS (score: {match_result.ats_score}%)")
                            else:
                                stats["matches_failed"] += 1
                                logger.info(f"  ❌ FAIL (score: {match_result.ats_score}%)")
                
                except Exception as e:
                    logger.error(f"  ❌ Error scoring job: {e}")
                    stats["errors"] += 1
            
            # Increment jobs counter and refresh cache if needed
            self.jobs_scored += 1
            self.refresh_skill_cache_if_needed()
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("📊 SCORING PIPELINE COMPLETE")
        logger.info("="*70)
        logger.info(f"Jobs processed:           {stats['total_jobs']}")
        logger.info(f"Profiles scored:          {stats['total_profiles']}")
        logger.info(f"Matches saved:            {stats['matches_saved']}")
        logger.info(f"  ✅ Passed gate:         {stats['matches_passed']}")
        logger.info(f"  ❌ Failed gate:         {stats['matches_failed']}")
        logger.info(f"Skill Discovery:          {stats['new_skills_discovered']} discovered, {stats['new_skills_skipped']} skipped")
        logger.info(f"❌ Errors:                {stats['errors']}")
        logger.info(f"📊 Current skill cache:   {len(self.skill_manager.get_all_skills())} skills")
        logger.info("="*70)
        
        return stats


if __name__ == "__main__":
    orchestrator = ScoringOrchestrator()
    results = orchestrator.run_scoring_pipeline(limit_jobs=10)
