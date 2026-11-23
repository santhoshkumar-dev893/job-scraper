import logging
from typing import Dict, List, Set, Optional
from supabase import Client

logger = logging.getLogger(__name__)


class SkillManager:
    """
    Manages skills with DB as single source of truth.
    
    Responsibilities:
    - Load skills from DB into memory cache
    - Check if skill exists (uses cache for performance)
    - Refresh cache periodically
    - Provide normalized skill lookups
    """
    
    def __init__(self, supabase: Client):
        """Initialize SkillManager and load skills from DB"""
        self.supabase = supabase
        self.skills_cache: Dict[str, Dict] = {}  # {skill_name_lower: skill_data}
        self.skills_normalized: Set[str] = set()  # For fast lookups
        self.last_refresh_count = 0
        
        # Load initial skills from DB
        self.refresh_cache()
        logger.info(f"✅ SkillManager initialized with {len(self.skills_cache)} skills")
    
    def refresh_cache(self) -> bool:
        """
        Refresh in-memory cache from database.
        
        Call this:
        - At startup
        - Every 100 jobs (progressive learning)
        - On demand when new skills discovered
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.supabase.table("skills").select(
                "id, skill_name, category, source, confidence_score, tags"
            ).execute()
            
            if not response.data:
                logger.warning("⚠️  No skills found in database")
                return False
            
            # Clear and rebuild cache
            self.skills_cache.clear()
            self.skills_normalized.clear()
            
            for skill_record in response.data:
                skill_name = skill_record['skill_name']
                skill_name_lower = skill_name.lower()
                
                self.skills_cache[skill_name_lower] = skill_record
                self.skills_normalized.add(skill_name_lower)
            
            logger.info(f"✅ Skill cache refreshed: {len(self.skills_cache)} skills loaded")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error refreshing skill cache: {e}")
            return False
    
    def has_skill(self, skill_name: str) -> bool:
        """
        Check if skill exists in cache (fast lookup).
        
        Args:
            skill_name: Skill to check
            
        Returns:
            True if skill exists in cache
        """
        return skill_name.lower() in self.skills_normalized
    
    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """
        Get skill details from cache.
        
        Args:
            skill_name: Skill to retrieve
            
        Returns:
            Skill dict or None if not found
        """
        return self.skills_cache.get(skill_name.lower())
    
    def get_all_skills(self) -> List[str]:
        """Get list of all normalized skill names"""
        return list(self.skills_normalized)
    
    def get_skills_by_category(self, category: str) -> List[str]:
        """Get skills filtered by category (core/discovered)"""
        return [
            skill_name for skill_name, skill_data in self.skills_cache.items()
            if skill_data.get('category') == category
        ]
    
    def get_stats(self) -> Dict:
        """Get statistics about skills in cache"""
        core_skills = len(self.get_skills_by_category('core'))
        discovered_skills = len(self.get_skills_by_category('discovered'))
        
        return {
            'total_skills': len(self.skills_cache),
            'core_skills': core_skills,
            'discovered_skills': discovered_skills,
            'discovery_rate': f"{(discovered_skills / len(self.skills_cache) * 100):.1f}%" if self.skills_cache else "0%",
            'last_refresh_count': self.last_refresh_count
        }
    
    def should_refresh(self, jobs_processed: int, refresh_interval: int = 100) -> bool:
        """
        Determine if cache should be refreshed.
        
        Refresh every N jobs to catch newly discovered skills.
        
        Args:
            jobs_processed: Total jobs processed so far
            refresh_interval: Refresh every N jobs (default 100)
            
        Returns:
            True if should refresh
        """
        should_refresh = (jobs_processed % refresh_interval == 0) and (jobs_processed > 0)
        
        if should_refresh:
            self.last_refresh_count += 1
            logger.info(f"🔄 Refreshing skill cache (refresh #{self.last_refresh_count})")
        
        return should_refresh
    
    def build_canonical_lookup(self) -> Dict[str, tuple[str, str]]:
        """
        Build a canonical lookup mapping (skill name or alias -> (canonical_name, category)).
        
        For database-backed skills, the canonical name is the skill_name from the database
        and category is the category field. Since we don't have aliases in the database yet,
        this is a simple 1:1 mapping.
        
        Returns:
            Dict mapping lowercase skill names to (canonical_name, category) tuples
        """
        lookup: Dict[str, tuple[str, str]] = {}
        
        for skill_name_lower, skill_data in self.skills_cache.items():
            skill_name = skill_data['skill_name']
            category = skill_data.get('category', 'uncategorized')
            
            # Map the skill name and its lowercase version
            lookup[skill_name_lower] = (skill_name, category)
            
        logger.info(f"✅ Built canonical lookup with {len(lookup)} entries")
        return lookup
