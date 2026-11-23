#!/usr/bin/env python3
"""
Test to verify that skill extraction works with database-backed skills.

This test verifies the migration from SKILL_MASTER (static dict) to 
database-backed skills via SkillManager.

Tests:
1. SkillManager can initialize and fetch skills from database
2. SpacySkillExtractor can be initialized with flat list from SkillManager
3. SkillExtractionService can build canonical lookup from SkillManager
4. End-to-end skill extraction works correctly
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_skill_manager_initialization():
    """Test that SkillManager can initialize and fetch skills"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: SkillManager Initialization")
    logger.info("="*80)
    
    try:
        import supabase_utils
        from skills_manager import SkillManager
        
        # Initialize SkillManager
        skill_manager = SkillManager(supabase_utils.supabase)
        
        # Verify it loaded skills
        all_skills = skill_manager.get_all_skills()
        logger.info(f"✓ SkillManager loaded {len(all_skills)} skills")
        
        if len(all_skills) == 0:
            logger.error("✗ No skills loaded from database!")
            return False
        
        # Verify skills are strings
        for skill in all_skills[:5]:
            if not isinstance(skill, str):
                logger.error(f"✗ Skill is not a string: {skill} ({type(skill)})")
                return False
        
        logger.info(f"✓ First 5 skills: {all_skills[:5]}")
        
        # Verify get_stats works
        stats = skill_manager.get_stats()
        logger.info(f"✓ Skill stats: {stats}")
        
        return True, skill_manager
        
    except Exception as e:
        logger.error(f"✗ Error initializing SkillManager: {e}", exc_info=True)
        return False, None


def test_spacy_extractor_initialization(skill_manager):
    """Test that SpacySkillExtractor can be initialized with flat skill list"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: SpacySkillExtractor Initialization")
    logger.info("="*80)
    
    try:
        from spacy_extractor import SpacySkillExtractor
        
        # Get flat list of skills from SkillManager
        skills_list = skill_manager.get_all_skills()
        logger.info(f"Using {len(skills_list)} skills from SkillManager")
        
        # Initialize extractor
        extractor = SpacySkillExtractor(skills_list)
        logger.info(f"✓ SpacySkillExtractor initialized successfully")
        
        # Test extraction
        test_text = "I have experience with Java, Python, and JavaScript"
        matches = extractor.extract(test_text)
        
        logger.info(f"✓ Extracted {len(matches)} skills from test text")
        for match in matches:
            logger.info(f"  - {match.name} (matched as '{match.matched_text}')")
        
        return True, extractor
        
    except Exception as e:
        logger.error(f"✗ Error initializing SpacySkillExtractor: {e}", exc_info=True)
        return False, None


def test_canonical_lookup_building(skill_manager):
    """Test that canonical lookup can be built from SkillManager"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Canonical Lookup Building")
    logger.info("="*80)
    
    try:
        # Build canonical lookup
        lookup = skill_manager.build_canonical_lookup()
        logger.info(f"✓ Built canonical lookup with {len(lookup)} entries")
        
        # Verify structure
        for key, value in list(lookup.items())[:5]:
            if not isinstance(value, tuple) or len(value) != 2:
                logger.error(f"✗ Invalid lookup entry: {key} -> {value}")
                return False
            
            canonical_name, category = value
            logger.info(f"  {key} -> ({canonical_name}, {category})")
        
        return True, lookup
        
    except Exception as e:
        logger.error(f"✗ Error building canonical lookup: {e}", exc_info=True)
        return False, None


def test_skill_extraction_service(skill_manager, extractor):
    """Test that SkillExtractionService works with database-backed skills"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: SkillExtractionService Integration")
    logger.info("="*80)
    
    try:
        from skill_extraction_service import SkillExtractionService
        
        # Build service with database-backed components
        service = SkillExtractionService(
            spacy_extractor=extractor,
            canonical_lookup=skill_manager.build_canonical_lookup(),
            llm_extractor=None,  # Disable LLM for this test
        )
        
        logger.info("✓ SkillExtractionService initialized successfully")
        
        # Test extraction
        test_description = """
        Looking for a backend developer with experience in:
        - Java and Spring Boot
        - Python and Django
        - SQL databases like PostgreSQL
        - REST API development
        - Docker containerization
        """
        
        result = service.extract_skills(test_description)
        
        logger.info(f"✓ Extracted {len(result.skills)} skills")
        logger.info(f"  LLM status: {result.llm_status}")
        logger.info(f"  Warnings: {result.warnings}")
        
        for skill in result.skills:
            logger.info(f"  - {skill.name} ({skill.category}) - {skill.sources}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error with SkillExtractionService: {e}", exc_info=True)
        return False


def test_scraper_initialization():
    """Test that scraper.py can initialize with new skill system"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Scraper Initialization")
    logger.info("="*80)
    
    try:
        # Import after all other tests to verify dependencies work
        import scraper
        
        logger.info("✓ scraper.py imported successfully")
        logger.info(f"✓ skill_service initialized: {scraper.skill_service}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error initializing scraper: {e}", exc_info=True)
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "="*80)
    logger.info("TESTING SKILL EXTRACTION MIGRATION (SKILL_MASTER -> DATABASE)")
    logger.info("="*80)
    
    all_passed = True
    skill_manager = None
    extractor = None
    
    # Test 1: SkillManager
    result, skill_manager = test_skill_manager_initialization()
    if not result:
        logger.error("TEST 1 FAILED")
        return 1
    logger.info("TEST 1 PASSED ✓")
    
    # Test 2: SpacySkillExtractor
    result, extractor = test_spacy_extractor_initialization(skill_manager)
    if not result:
        logger.error("TEST 2 FAILED")
        return 1
    logger.info("TEST 2 PASSED ✓")
    
    # Test 3: Canonical Lookup
    result, lookup = test_canonical_lookup_building(skill_manager)
    if not result:
        logger.error("TEST 3 FAILED")
        return 1
    logger.info("TEST 3 PASSED ✓")
    
    # Test 4: SkillExtractionService
    if not test_skill_extraction_service(skill_manager, extractor):
        logger.error("TEST 4 FAILED")
        return 1
    logger.info("TEST 4 PASSED ✓")
    
    # Test 5: Scraper Initialization
    if not test_scraper_initialization():
        logger.error("TEST 5 FAILED")
        return 1
    logger.info("TEST 5 PASSED ✓")
    
    # All tests passed
    logger.info("\n" + "="*80)
    logger.info("ALL TESTS PASSED! ✓")
    logger.info("="*80)
    logger.info("\nSummary:")
    logger.info("✓ SkillManager can load skills from database")
    logger.info("✓ SpacySkillExtractor accepts flat skill list")
    logger.info("✓ Canonical lookup is properly built")
    logger.info("✓ SkillExtractionService integrates correctly")
    logger.info("✓ scraper.py initializes without errors")
    logger.info("\nMigration from SKILL_MASTER to database-backed skills is successful!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
