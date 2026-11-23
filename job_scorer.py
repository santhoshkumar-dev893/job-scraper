"""
Improved Job Matching Pipeline

Combines heuristic (Spacy) matching with optional LLM fallback for robust,
cost-efficient job scoring against a user profile.

Stage 1: Heuristic Skill Extraction (Spacy)
Stage 2: Heuristic Scoring against Profile (using SkillManager)
Stage 3: LLM Skill Extraction (if heuristic fails)
Stage 4: Discover & Insert New Skills via SkillDiscovery
Stage 5: Re-score with merged skills
Stage 6: Return final MatchResult
"""
import re
import logging
from section_splitter import SectionSplitter
from typing import Optional, Set, Dict, Tuple, List, TYPE_CHECKING
from models import MatchResult, SkillMatch, MatchPath, DataQuality
from spacy_extractor import SpacySkillExtractor
from llm_skill_extractor import LLMSkillExtractor
from skill_discovery import extract_discovered_skills_from_llm_output

if TYPE_CHECKING:
    from skills_manager import SkillManager
    from skill_discovery import SkillDiscovery

log = logging.getLogger(__name__)

# Configuration
DEFAULT_ATS_THRESHOLD = 70  # Percentage (0-100)
MANDATORY_WEIGHT = 2
PREFERRED_WEIGHT = 1
UNSPECIFIED_WEIGHT = 1


class JobScorer:
    """
    Scores jobs against a user profile using heuristic + optional LLM fallback.
    
    Uses SkillManager for skill lookups (database-backed cache) instead of
    static SKILL_MASTER list. Integrates with SkillDiscovery for automated
    skill discovery.
    
    Attributes:
        profile: User profile with skills and preferences
        skill_manager: SkillManager for skill lookups (DB-backed cache)
        skill_discovery: SkillDiscovery for inserting new skills
        section_splitter: Tool to split job description into sections
        spacy_extractor: Heuristic skill extractor
        llm_extractor: Optional LLM skill extractor for fallback
        ats_threshold: Score threshold to pass gate (default 70%)
    """
    
    def __init__(
        self,
        profile: dict,
        skill_manager: 'SkillManager',
        skill_discovery: Optional['SkillDiscovery'] = None,
        ats_threshold: int = DEFAULT_ATS_THRESHOLD,
    ):
        """
        Initialize job scorer with profile and skill management tools.
        
        Args:
            profile: User profile with skills
            skill_manager: SkillManager for database-backed skill lookups
            skill_discovery: Optional SkillDiscovery for automated skill insertion
            ats_threshold: Score threshold for gate (default 70%)
        """
        self.profile = profile
        self.skill_manager = skill_manager
        self.skill_discovery = skill_discovery
        self.section_splitter = SectionSplitter()
        self.spacy_extractor = SpacySkillExtractor(self.skill_manager.get_all_skills())
        self.llm_extractor = LLMSkillExtractor()
        self.ats_threshold = ats_threshold
        
        # Normalize profile skills to lowercase for comparison
        self.profile_skills_normalized = self._normalize_skills(
            profile.get('primary_skills', []) + 
            profile.get('secondary_skills', [])
        )
        
        log.debug(
            f"Initialized JobScorer with {len(self.profile_skills_normalized)} profile skills, "
            f"SkillManager has {len(skill_manager.get_all_skills())} cached skills"
        )
    
    @staticmethod
    def _normalize_skills(skills: List[str]) -> Set[str]:
        """Normalize skill names: lowercase, trim, collapse spaces"""
        return {
            skill.strip().lower().replace(r'\s+', ' ')
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        }
    
    def score(self, job_description: str, job_id: str) -> MatchResult:
        """
        Score a job against the profile using the full pipeline.
        
        Args:
            job_description: Full job description text
            job_id: Unique job identifier
            
        Returns:
            MatchResult with scoring details and recommendations
        """
        log.info(f"Starting job scoring for job_id={job_id}")
        
        # Track jobs processed for cache revalidation
        if hasattr(self.llm_extractor, 'cache_manager'):
            self.llm_extractor.cache_manager.record_job_processed()
        
        # Stage 1: Heuristic Skill Extraction
        heuristic_skills = self._extract_heuristic_skills(job_description)
        log.debug(f"Heuristic extracted {len(heuristic_skills)} skills")
        
        # Stage 2: Score against profile
        result = self._score_against_profile(heuristic_skills, job_id)
        result.heuristic_score = result.ats_score
        log.debug(f"Heuristic score: {result.ats_score}%, gate_passed: {result.gate_passed}")
        
        # Stage 3-5: LLM fallback if gate failed
        if not result.gate_passed and self.llm_extractor:
            result = self._run_llm_fallback(result, job_description, heuristic_skills, job_id)
        elif not result.gate_passed and not self.llm_extractor:
            result.path = MatchPath.LLM_DISABLED
            log.info(f"LLM disabled; job_id={job_id} fails gate with score {result.ats_score}%")
        
        # Final confidence score
        result.confidence_score = self._calculate_confidence(result)
        
        # Print cache stats periodically
        if hasattr(self.llm_extractor, 'cache_manager'):
            if self.llm_extractor.cache_manager.jobs_processed % 100 == 0 and \
               self.llm_extractor.cache_manager.jobs_processed > 0:
                stats = self.llm_extractor.get_cache_stats()
                log.info(f"Cache Stats: {stats}")
        
        log.info(f"score {result}")
        log.info(f"Job scoring complete: job_id={job_id}, score={result.ats_score}%, gate={result.gate_passed}")
        return result
    
    def _extract_heuristic_skills(self, job_description: str) -> List[SkillMatch]:
        """
        Stage 1: Extract skills using Spacy (heuristic).
        
        Splits job description into sections and extracts:
        - Skills from "requirements" section → "mandatory"
        - Skills from "nice_to_have" section → "preferred"
        - Skills from other sections → "unspecified"
        
        Returns:
            List of SkillMatch objects with requirement levels
        """
        try:
            # Try to split into sections
            sections, split_method = self.section_splitter.split_sections(job_description)
            
            # Determine data quality
            data_quality = DataQuality.HIGH if split_method == "headings" else DataQuality.LOW
            
            extracted_skills = []
            
            if sections:
                # Extract from requirements (mandatory)
                req_text = sections.get("requirements", "")
                if req_text:
                    for spacy_skill in self.spacy_extractor.extract(req_text):
                        extracted_skills.append(SkillMatch(
                            name=spacy_skill.name,
                            requirement="mandatory",
                            source="heuristic"
                        ))
                
                # Extract from nice_to_have (preferred)
                nice_text = sections.get("nice_to_have", "")
                if nice_text:
                    for spacy_skill in self.spacy_extractor.extract(nice_text):
                        extracted_skills.append(SkillMatch(
                            name=spacy_skill.name,
                            requirement="preferred",
                            source="heuristic"
                        ))
                
                # Extract from other sections (unspecified)
                for section_name in ["responsibilities", "about_company", "benefits", "other"]:
                    section_text = sections.get(section_name, "")
                    if section_text:
                        for spacy_skill in self.spacy_extractor.extract(section_text):
                            extracted_skills.append(SkillMatch(
                                name=spacy_skill.name,
                                requirement="unspecified",
                                source="heuristic"
                            ))
            else:
                # No sections found, extract from full text with unspecified
                data_quality = DataQuality.LOW
                for spacy_skill in self.spacy_extractor.extract(job_description):
                    extracted_skills.append(SkillMatch(
                        name=spacy_skill.name,
                        requirement="unspecified",
                        source="heuristic"
                    ))
            
            # Deduplicate by name, keeping highest requirement level
            unique_skills = self._deduplicate_skills(extracted_skills)
            
            log.debug(f"Heuristic extraction: found {len(unique_skills)} unique skills, data_quality={data_quality.value}")
            return unique_skills
            
        except Exception as e:
            log.error(f"Error extracting heuristic skills: {e}")
            return []
    
    def _deduplicate_skills(self, skills: List[SkillMatch]) -> List[SkillMatch]:
        """
        Deduplicate skills by name, keeping the highest requirement level.
        
        Priority: mandatory > preferred > unspecified
        """
        requirement_priority = {"mandatory": 3, "preferred": 2, "unspecified": 1}
        skills_dict: Dict[str, SkillMatch] = {}
        
        for skill in skills:
            skill_key = skill.name.lower()
            existing = skills_dict.get(skill_key)
            
            if not existing:
                skills_dict[skill_key] = skill
            elif requirement_priority.get(skill.requirement, 0) > requirement_priority.get(existing.requirement, 0):
                skills_dict[skill_key] = skill
        
        return list(skills_dict.values())
    
    
    def _score_against_profile(self, skills: List[SkillMatch], job_id: str) -> MatchResult:
        """
        Stage 2: Score the extracted skills against the user profile.
        
        Uses SkillManager for skill lookups instead of SKILL_MASTER.
        
        Formula:
            ats_score = (matched_skills_count / total_skills_count) × 100
        
        This penalizes missing skills - more complete skill match = higher score.
        
        Gate passes if:
            - At least 80% of mandatory skills are present AND
            - ats_score >= ats_threshold
        
        Returns:
            MatchResult with scoring details
        """
        result = MatchResult(job_id=job_id)
        
        if not skills:
            log.warning(f"No skills found for job_id={job_id}, gate fails")
            result.warnings.append("No skills extracted from job description")
            return result
        
        matched_skill_names = []
        missing_skill_names = []
        mandatory_missing = []
        
        # Check each skill against profile using SkillManager
        for skill in skills:
            skill_normalized = skill.name.lower()
            
            # First check: does user's profile have this skill?
            if skill_normalized in self.profile_skills_normalized:
                matched_skill_names.append(skill.name)
            # Second check: is this a known skill in the database?
            elif self.skill_manager.has_skill(skill_normalized):
                # Job requires a skill the user doesn't have
                missing_skill_names.append(skill.name)
                if skill.requirement == "mandatory":
                    mandatory_missing.append(skill.name)
            else:
                # Unknown skill - might be new discovery opportunity
                missing_skill_names.append(skill.name)
                if skill.requirement == "mandatory":
                    mandatory_missing.append(skill.name)
        
        # Calculate ATS score based on skill coverage
        # Formula: (matched skills / total skills) × 100
        total_skills = len(skills)
        matched_skills = len(matched_skill_names)
        
        if total_skills > 0:
            result.ats_score = round(100 * matched_skills / total_skills)
        else:
            result.ats_score = 0
        
        # Determine gate pass - need 80% of mandatory skills
        total_mandatory = sum(1 for s in skills if s.requirement == "mandatory")
        if total_mandatory > 0:
            mandatory_found = total_mandatory - len(mandatory_missing)
            mandatory_coverage = mandatory_found / total_mandatory
            gate_mandatory_ok = mandatory_coverage >= 0.8
        else:
            gate_mandatory_ok = True
        
        result.gate_passed = gate_mandatory_ok and result.ats_score >= self.ats_threshold
        
        # Store results
        result.matched_skills = matched_skill_names
        result.missing_skills = missing_skill_names
        result.mandatory_missing = mandatory_missing
        result.skills = skills
        result.data_quality = DataQuality.HIGH if len(skills) >= 3 else DataQuality.LOW
        result.path = MatchPath.HEURISTIC_ONLY if result.gate_passed else MatchPath.LLM_DISABLED
        
        log.debug(
            f"Scoring: job_id={job_id}, score={result.ats_score}%, "
            f"matched={len(matched_skill_names)}, missing={len(missing_skill_names)}"
        )
        
        return result
    
    @staticmethod
    def _get_weight(requirement: str) -> int:
        """Get weight for requirement level"""
        weights = {
            "mandatory": MANDATORY_WEIGHT,
            "preferred": PREFERRED_WEIGHT,
            "unspecified": UNSPECIFIED_WEIGHT
        }
        return weights.get(requirement, UNSPECIFIED_WEIGHT)
    
    def _run_llm_fallback(
        self,
        result: MatchResult,
        job_description: str,
        heuristic_skills: List[SkillMatch],
        job_id: str
    ) -> MatchResult:
        """
        Stage 3-5: LLM fallback when heuristic gate fails.
        
        1. Extract additional skills using LLM
        2. Discover new skills via SkillDiscovery (automatic DB insertion)
        3. Merge with heuristic skills
        4. Re-score with merged skills
        
        Returns:
            Updated MatchResult with LLM findings
        """
        log.info(f"Running LLM fallback for job_id={job_id}")
        
        try:
            # Stage 3: LLM skill extraction
            known_skills = [s.name for s in heuristic_skills]
            llm_result = self.llm_extractor.extract(job_description, known_skills=known_skills)
            log.info(f"LLM result {llm_result}")
            
            # Check LLM status
            if llm_result.status not in {"ok", "partial"}:
                result.path = MatchPath.LLM_FAILED
                result.warnings.append(f"LLM extraction failed: {llm_result.status}")
                log.warning(f"LLM failed for job_id={job_id}: {llm_result.status}")
                return result
            
            # Stage 4: Discover new skills via SkillDiscovery
            # Convert LLM output to DiscoveredSkill objects
            discovered_skills = extract_discovered_skills_from_llm_output(llm_result)
            
            if discovered_skills and self.skill_discovery:
                discovery_result = self.skill_discovery.discover_skills(
                    discovered_skills,
                    job_id=job_id
                )
                log.info(
                    f"Skill discovery: {discovery_result.summary()} "
                    f"(job_id={job_id})"
                )
                result.warnings.extend(discovery_result.validation_errors)
            
            # Merge LLM skills with heuristic
            merged_skills = self._merge_skills(
                heuristic_skills,
                llm_result.skills,
                job_id
            )
            result.warnings.extend(llm_result.warnings)
            
            # Stage 5: Re-score with merged skills
            result = self._score_against_profile(merged_skills, job_id)
            result.llm_score = result.ats_score
            result.path = MatchPath.LLM_RESCORED
            
            log.info(f"LLM fallback complete: job_id={job_id}, new_score={result.ats_score}%")
            return result
            
        except Exception as e:
            log.error(f"Error in LLM fallback for job_id={job_id}: {e}")
            result.path = MatchPath.LLM_FAILED
            result.warnings.append(f"LLM exception: {str(e)}")
            return result
    
    def _merge_skills(
        self,
        heuristic_skills: List[SkillMatch],
        llm_skills: List,
        job_id: str
    ) -> List[SkillMatch]:
        """
        Merge LLM skills with heuristic skills.
        
        Rules:
        - Keep heuristic skill names (canonical from spacy)
        - Use LLM requirement level if it upgrades unspecified
        - Mark LLM-only skills as "new"
        - Update source to "both" if found by both
        """
        # Create dict of heuristic skills by normalized name
        heuristic_dict = {s.name.lower(): s for s in heuristic_skills}
        merged = list(heuristic_skills)
        new_skills = []
        
        for llm_skill in llm_skills:
            llm_name_normalized = llm_skill.name.strip().lower()
            
            # Check if already in heuristic
            if llm_name_normalized in heuristic_dict:
                # Update requirement level if LLM is more specific
                existing = heuristic_dict[llm_name_normalized]
                if existing.requirement == "unspecified" and llm_skill.level != "unspecified":
                    existing.requirement = llm_skill.level
                    existing.source = "both"
            else:
                # New skill from LLM
                skill = SkillMatch(
                    name=llm_skill.name,
                    requirement=llm_skill.level,
                    source="llm",
                    is_new=True,
                    evidence=llm_skill.evidence
                )
                merged.append(skill)
                new_skills.append(skill)
        
        if new_skills:
            log.info(f"LLM found {len(new_skills)} new skills for job_id={job_id}")
        
        return merged
    
    @staticmethod
    def _calculate_confidence(result: MatchResult) -> int:
        """
        Calculate overall confidence score based on various factors.
        
        Factors:
        - ATS score: Heavily weighted
        - Path: LLM_RESCORED less confident than HEURISTIC_ONLY
        - Data quality: HIGH more confident than LOW
        - Missing skills: Fewer missing = more confident
        """
        confidence = result.ats_score  # Base on ATS score
        
        # Adjust based on path
        if result.path == MatchPath.HEURISTIC_ONLY:
            confidence += 5  # High confidence if heuristic passes
        elif result.path == MatchPath.LLM_RESCORED:
            confidence -= 5  # Slightly lower if needed LLM
        elif result.path == MatchPath.LLM_FAILED:
            confidence -= 20  # Much lower if LLM failed
        elif result.path == MatchPath.LLM_DISABLED:
            confidence -= 10  # Lower if LLM unavailable
        
        # Adjust based on data quality
        if result.data_quality == DataQuality.LOW:
            confidence -= 10
        
        # Adjust based on missing mandatory skills
        if result.mandatory_missing:
            confidence -= (len(result.mandatory_missing) * 5)
        
        # Clamp to 0-100
        return max(0, min(100, confidence))


# ============================================================================
# Utility Functions
# ============================================================================

def create_job_scorer(profile: dict, section_splitter=None) -> JobScorer:
    """Factory function to create a JobScorer instance"""
    # Create section_splitter if not provided
    if section_splitter is None:
        section_splitter = SectionSplitter()
    
    return JobScorer(
        profile=profile,
        ats_threshold=DEFAULT_ATS_THRESHOLD
    )
