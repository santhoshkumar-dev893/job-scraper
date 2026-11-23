"""
Automated Skill Discovery and Insertion

Responsible for:
1. Validating new skills discovered by LLM
2. Checking if skill already exists in database
3. Inserting new skills to database (atomic)
4. Updating SkillManager cache after successful insert

Designed for write-only automation:
- Uses SUPABASE_SERVICE_ROLE_KEY (backend only)
- RLS policy allows INSERT only
- Database is authoritative source of truth
- Cache is updated immediately after write
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from supabase import Client
from skills_manager import SkillManager

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredSkill:
    """Represents a skill discovered by LLM extraction"""
    name: str                          # Skill name (required)
    requirement: str                   # 'mandatory', 'preferred', 'optional', 'unspecified'
    evidence: str                      # Quote from job description (proof)
    confidence: float = 0.8            # 0.0-1.0, confidence in this skill
    description: Optional[str] = None  # Optional description


@dataclass
class DiscoveryResult:
    """Result of skill discovery operation"""
    inserted_skills: List[Dict] = field(default_factory=list)  # {id, skill_name, ...}
    skipped_skills: List[str] = field(default_factory=list)    # Already exist
    validation_errors: List[str] = field(default_factory=list) # Failed validation
    total_attempted: int = 0
    
    def __post_init__(self):
        self.total_attempted = (
            len(self.inserted_skills) + 
            len(self.skipped_skills) + 
            len(self.validation_errors)
        )
    
    def is_successful(self) -> bool:
        """True if at least one skill was inserted successfully"""
        return len(self.inserted_skills) > 0
    
    def summary(self) -> str:
        """Human-readable summary of discovery results"""
        return (
            f"Inserted: {len(self.inserted_skills)}, "
            f"Skipped: {len(self.skipped_skills)}, "
            f"Errors: {len(self.validation_errors)}"
        )


class SkillDiscovery:
    """
    Validates and inserts new skills discovered by LLM.
    
    Responsibilities:
    - Validate skill data (name, requirement, evidence)
    - Check if skill already exists (via SkillManager)
    - Insert new skills to database (atomic write)
    - Update SkillManager cache after successful insert
    - Record all operations for audit trail
    
    Design principles:
    - Never raises exceptions (returns error results)
    - Atomic writes: each skill inserted individually
    - Cache updated immediately after successful insert
    - Logs all operations for debugging
    - Trusts database as source of truth
    """
    
    def __init__(self, supabase: Client, skill_manager: SkillManager):
        """
        Initialize SkillDiscovery with database client and skill manager.
        
        Args:
            supabase: Supabase client (with service role key)
            skill_manager: SkillManager instance for cache updates
        """
        self.supabase = supabase
        self.skill_manager = skill_manager
        self.discovered_count = 0
        self.duplicate_count = 0
        
        logger.info("✅ SkillDiscovery initialized")
    
    def discover_skills(
        self,
        skills: List[DiscoveredSkill],
        job_id: str
    ) -> DiscoveryResult:
        """
        Validate and insert new skills discovered by LLM.
        
        Process:
        1. Validate each skill data
        2. Check if skill already exists
        3. Insert new skills to database
        4. Update cache for each successful insert
        5. Return detailed result
        
        Args:
            skills: List of DiscoveredSkill objects
            job_id: Source job ID for tracking
            
        Returns:
            DiscoveryResult with inserted, skipped, and error details
            
        Example:
            result = discovery.discover_skills([
                DiscoveredSkill("Python", "mandatory", "3+ years Python experience"),
                DiscoveredSkill("Docker", "preferred", "Docker experience preferred"),
            ], job_id="job123")
            
            print(f"Inserted: {len(result.inserted_skills)}")
            print(f"Skipped: {len(result.skipped_skills)}")
        """
        if not skills:
            return DiscoveryResult()
        
        logger.info(f"Discovering {len(skills)} skills from job_id={job_id}")
        
        result = DiscoveryResult()
        
        for skill in skills:
            # Step 1: Validate skill data
            is_valid, error_msg = self._validate_skill(skill)
            if not is_valid:
                logger.warning(f"Skill validation failed: {error_msg}")
                result.validation_errors.append(error_msg)
                continue
            
            # Step 2: Check if skill already exists
            skill_name_lower = skill.name.lower().strip()
            if self.skill_manager.has_skill(skill_name_lower):
                logger.debug(f"⏭️  Skill already exists: {skill.name}")
                result.skipped_skills.append(skill.name)
                self.duplicate_count += 1
                continue
            
            # Step 3: Insert to database
            inserted_skill = self._insert_skill(skill, job_id)
            if inserted_skill:
                logger.info(f"✨ New skill discovered: {skill.name}")
                result.inserted_skills.append(inserted_skill)
                self.discovered_count += 1
                
                # Step 4: Update cache immediately
                self._update_cache(inserted_skill)
            else:
                # Insert failed (database error or duplicate constraint)
                error_msg = f"Database insert failed for skill: {skill.name}"
                logger.error(f"❌ {error_msg}")
                result.validation_errors.append(error_msg)
        
        # Summary logging
        if result.inserted_skills:
            logger.info(
                f"🎯 Discovery complete for job_id={job_id}: "
                f"{result.summary()}"
            )
        
        return result
    
    def _validate_skill(self, skill: DiscoveredSkill) -> Tuple[bool, str]:
        """
        Validate skill data format and content.
        
        Checks:
        - Skill name is not empty and ≤ 100 chars
        - Requirement is valid (mandatory/preferred/optional/unspecified)
        - Evidence is not empty and ≤ 500 chars
        - Confidence is between 0.0 and 1.0
        
        Args:
            skill: DiscoveredSkill to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Validate skill name
        if not skill.name or not isinstance(skill.name, str):
            return False, "Skill name is required and must be a string"
        
        skill_name = skill.name.strip()
        if not skill_name:
            return False, "Skill name cannot be empty or whitespace only"
        
        if len(skill_name) > 100:
            return False, f"Skill name too long ({len(skill_name)} > 100 chars)"
        
        # Validate requirement level
        valid_requirements = {'mandatory', 'preferred', 'optional', 'unspecified'}
        if skill.requirement not in valid_requirements:
            return False, (
                f"Invalid requirement '{skill.requirement}'. "
                f"Must be one of: {', '.join(valid_requirements)}"
            )
        
        # Validate evidence
        if not skill.evidence or not isinstance(skill.evidence, str):
            return False, "Evidence is required and must be a string"
        
        evidence = skill.evidence.strip()
        if not evidence:
            return False, "Evidence cannot be empty or whitespace only"
        
        if len(evidence) > 500:
            return False, f"Evidence too long ({len(evidence)} > 500 chars)"
        
        # Validate confidence
        if not isinstance(skill.confidence, (int, float)):
            return False, "Confidence must be a number"
        
        if not (0.0 <= skill.confidence <= 1.0):
            return False, (
                f"Confidence {skill.confidence} out of range [0.0, 1.0]"
            )
        
        # Validate description (optional)
        if skill.description is not None:
            if not isinstance(skill.description, str):
                return False, "Description must be a string"
            
            if len(skill.description.strip()) > 500:
                return False, "Description too long (> 500 chars)"
        
        return True, ""
    
    def _skill_exists(self, skill_name: str) -> bool:
        """
        Check if skill already exists (uses SkillManager cache).
        
        Args:
            skill_name: Skill name to check
            
        Returns:
            True if skill exists in cache
        """
        return self.skill_manager.has_skill(skill_name)
    
    def _insert_skill(self, skill: DiscoveredSkill, job_id: str) -> Optional[Dict]:
        """
        Insert skill to database and return inserted record.
        
        Performs atomic write:
        1. Prepare skill record
        2. Insert to database
        3. Return inserted record (with generated ID)
        
        Args:
            skill: DiscoveredSkill to insert
            job_id: Source job ID for tracking
            
        Returns:
            Inserted skill record dict, or None if failed
        """
        try:
            # Prepare record for database
            skill_record = {
                "skill_name": skill.name.strip(),
                "category": "discovered",        # All LLM skills are categorized as discovered
                "source": "llm",                 # Automated discovery source
                "confidence_score": int(skill.confidence * 100),  # Convert 0-1 to 0-100
                "validation_status": "pending",  # Manual review required
                "discovered_from_job_id": job_id,
                "description": skill.description.strip() if skill.description else None,
                # Optional: could add tags based on requirement
                "tags": [skill.requirement],
            }
            
            # Insert to database (uses RLS policy: INSERT allowed)
            response = self.supabase.table("skills").insert(skill_record).execute()
            
            if response.data:
                inserted = response.data[0] if isinstance(response.data, list) else response.data
                logger.debug(f"Inserted skill record: {inserted}")
                return inserted
            else:
                logger.error(f"Database insert failed: empty response for skill {skill.name}")
                return None
                
        except Exception as e:
            # Check if it's a unique constraint violation (duplicate)
            error_msg = str(e)
            if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
                logger.warning(f"Skill already exists in database: {skill.name}")
                # Don't return error, just return None
                # Caller should treat this as a skipped duplicate
            else:
                logger.error(f"Error inserting skill {skill.name}: {e}")
            return None
    
    def _update_cache(self, skill: Dict) -> None:
        """
        Update SkillManager cache after successful insert.
        
        The cache is immediately available for lookup in subsequent
        scoring operations, so no need to wait for periodic refresh.
        
        Args:
            skill: Inserted skill record from database
        """
        try:
            # Directly update the cache in SkillManager
            skill_name_lower = skill['skill_name'].lower()
            
            # Add to normalized set for fast lookups
            self.skill_manager.skills_normalized.add(skill_name_lower)
            
            # Add full record to cache
            self.skill_manager.skills_cache[skill_name_lower] = skill
            
            logger.debug(f"Cache updated for skill: {skill['skill_name']}")
            
        except Exception as e:
            logger.error(f"Error updating cache for skill {skill.get('skill_name')}: {e}")
            # Don't raise - cache will be refreshed at next batch boundary


# ============================================================================
# Helper Functions for Common Discovery Operations
# ============================================================================

def extract_discovered_skills_from_llm_output(
    llm_extraction_result,
    confidence_threshold: float = 0.5
) -> List[DiscoveredSkill]:
    """
    Convert LLM extraction result to DiscoveredSkill objects.
    
    Expects llm_extraction_result to have:
    - skills: List[ExtractedSkill] with {name, level, evidence, confidence}
    - status: str ("ok" or "partial")
    
    Args:
        llm_extraction_result: ExtractionResult from LLMSkillExtractor.extract()
        confidence_threshold: Min confidence to include (0.0-1.0)
        
    Returns:
        List of DiscoveredSkill objects
    """
    discovered = []
    
    # Check if result has skills attribute
    if not hasattr(llm_extraction_result, 'skills'):
        logger.warning("⚠️  LLM extraction result has no 'skills' attribute")
        return discovered
    
    skills_list = llm_extraction_result.skills
    if not skills_list:
        logger.debug("No skills in LLM extraction result")
        return discovered
    
    for skill in skills_list:
        try:
            # Map LLM "level" to our "requirement" field
            # ExtractedSkill.level is a RequirementLevel enum
            requirement_str = skill.level if isinstance(skill.level, str) else skill.level.value
            
            requirement_map = {
                "mandatory": "mandatory",
                "preferred": "preferred",
                "optional": "optional",
                "unspecified": "unspecified",
            }
            requirement = requirement_map.get(requirement_str, "unspecified")
            
            # Filter by confidence
            if skill.confidence >= confidence_threshold:
                discovered.append(DiscoveredSkill(
                    name=skill.name,
                    requirement=requirement,
                    evidence=skill.evidence,
                    confidence=skill.confidence,
                ))
                logger.debug(f"Discovered skill: {skill.name} (confidence: {skill.confidence})")
        except AttributeError as e:
            logger.error(f"❌ Error accessing skill attributes: {e}. Skill object: {skill}")
            continue
    
    logger.info(f"✨ Extracted {len(discovered)} discovered skills from LLM (threshold: {confidence_threshold})")
    return discovered
