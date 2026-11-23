"""
Test suite for the improved job matching workflow (JobScorer).

Tests cover:
- Stage 1: Heuristic skill extraction
- Stage 2: Scoring against profile
- Stage 3-5: LLM fallback
- Full pipeline integration
"""

import pytest
from models import MatchResult, SkillMatch, MatchPath, DataQuality
from job_scorer import JobScorer, DEFAULT_ATS_THRESHOLD


class MockSpacyExtractor:
    """Mock Spacy extractor for testing"""
    def __init__(self, skills=None):
        self.skills_data = skills or []
    
    def extract(self, text):
        """Return mock skills"""
        class MockSkill:
            def __init__(self, name):
                self.name = name
                self.category = "tech"
        
        return [MockSkill(s) for s in self.skills_data]


class MockSectionSplitter:
    """Mock section splitter for testing"""
    def split_sections(self, text):
        """Return mock sections"""
        return {
            "requirements": "Python JavaScript React",
            "nice_to_have": "Docker Kubernetes",
            "responsibilities": "Build scalable apps",
            "about_company": "Tech startup",
        }, "headings"


class MockLLMExtractor:
    """Mock LLM extractor for testing"""
    def extract(self, description, known_skills=None):
        """Return mock LLM results"""
        class MockLLMResult:
            def __init__(self):
                self.status = "ok"
                self.warnings = []
                self.skills = []
                
                class MockLLMSkill:
                    def __init__(self, name, level="unspecified"):
                        self.name = name
                        self.level = level
                        self.evidence = "mentioned in job"
                        self.confidence = 0.8
                
                # Return some additional skills
                self.skills = [
                    MockLLMSkill("AWS", "preferred"),
                    MockLLMSkill("Microservices", "mandatory")
                ]
        
        return MockLLMResult()


class TestJobScorer:
    """Test cases for JobScorer"""
    
    @pytest.fixture
    def profile(self):
        """Mock user profile"""
        return {
            'name': 'John Doe',
            'primary_skills': ['Python', 'JavaScript', 'React'],
            'secondary_skills': ['Docker', 'SQL'],
        }
    
    @pytest.fixture
    def scorer(self, profile):
        """Create a JobScorer instance for testing"""
        return JobScorer(
            profile=profile,
            section_splitter=MockSectionSplitter(),
            spacy_extractor=MockSpacyExtractor(['Python', 'JavaScript', 'React', 'Docker']),
            llm_extractor=None,
            ats_threshold=DEFAULT_ATS_THRESHOLD
        )
    
    def test_normalize_skills(self):
        """Test skill normalization"""
        skills = ['Python ', '  JavaScript  ', 'C++', '  React ']
        normalized = JobScorer._normalize_skills(skills)
        
        assert 'python' in normalized
        assert 'javascript' in normalized
        assert 'c++' in normalized
        assert 'react' in normalized
        assert len(normalized) == 4
    
    def test_heuristic_extraction_with_sections(self, scorer):
        """Test heuristic skill extraction with proper sections"""
        job_desc = "Looking for Python and JavaScript developer"
        skills = scorer._extract_heuristic_skills(job_desc)
        
        # Should extract Python, JavaScript, React, Docker
        skill_names = [s.name for s in skills]
        assert 'Python' in skill_names
        assert 'JavaScript' in skill_names
    
    def test_score_perfect_match(self, scorer):
        """Test scoring when all skills match"""
        skills = [
            SkillMatch(name='Python', requirement='mandatory', source='heuristic'),
            SkillMatch(name='JavaScript', requirement='mandatory', source='heuristic'),
            SkillMatch(name='React', requirement='preferred', source='heuristic'),
        ]
        
        result = scorer._score_against_profile(skills, 'job_123')
        
        # All skills in profile, should have high score
        assert result.ats_score == 100
        assert result.gate_passed == True
        assert len(result.matched_skills) == 3
        assert len(result.missing_skills) == 0
    
    def test_score_partial_match(self, scorer):
        """Test scoring with some missing skills"""
        skills = [
            SkillMatch(name='Python', requirement='mandatory', source='heuristic'),
            SkillMatch(name='Go', requirement='mandatory', source='heuristic'),  # Not in profile
            SkillMatch(name='React', requirement='preferred', source='heuristic'),
        ]
        
        result = scorer._score_against_profile(skills, 'job_124')
        
        # Partial match with missing mandatory skill
        assert result.ats_score < 100
        assert result.gate_passed == False
        assert 'Go' in result.missing_skills
        assert 'Go' in result.mandatory_missing
    
    def test_score_no_skills(self, scorer):
        """Test scoring when no skills are found"""
        result = scorer._score_against_profile([], 'job_125')
        
        assert result.ats_score == 0
        assert result.gate_passed == False
        assert len(result.warnings) > 0
    
    def test_get_weight(self):
        """Test weight calculation"""
        assert JobScorer._get_weight('mandatory') == 2
        assert JobScorer._get_weight('preferred') == 1
        assert JobScorer._get_weight('unspecified') == 1
        assert JobScorer._get_weight('unknown') == 1  # Default
    
    def test_deduplicate_skills(self, scorer):
        """Test skill deduplication"""
        skills = [
            SkillMatch(name='Python', requirement='mandatory', source='heuristic'),
            SkillMatch(name='Python', requirement='preferred', source='heuristic'),  # Duplicate
            SkillMatch(name='JavaScript', requirement='unspecified', source='heuristic'),
        ]
        
        deduplicated = scorer._deduplicate_skills(skills)
        
        assert len(deduplicated) == 2
        # Should keep mandatory, not preferred
        python_skill = next(s for s in deduplicated if s.name == 'Python')
        assert python_skill.requirement == 'mandatory'
    
    def test_calculate_confidence_perfect_heuristic(self, scorer):
        """Test confidence calculation for perfect heuristic match"""
        result = MatchResult(
            job_id='job_126',
            ats_score=100,
            gate_passed=True,
            path=MatchPath.HEURISTIC_ONLY,
            data_quality=DataQuality.HIGH,
            matched_skills=['Python', 'JavaScript', 'React'],
            missing_skills=[],
            mandatory_missing=[]
        )
        
        confidence = JobScorer._calculate_confidence(result)
        assert confidence == 100  # 100 + 5 (heuristic) - 5 (clamped to 100)
    
    def test_calculate_confidence_llm_rescored(self, scorer):
        """Test confidence calculation for LLM rescored match"""
        result = MatchResult(
            job_id='job_127',
            ats_score=80,
            gate_passed=True,
            path=MatchPath.LLM_RESCORED,
            data_quality=DataQuality.HIGH,
            matched_skills=['Python', 'JavaScript'],
            missing_skills=['Go'],
            mandatory_missing=[]
        )
        
        confidence = JobScorer._calculate_confidence(result)
        # 80 - 5 (llm_rescored) = 75
        assert confidence == 75
    
    def test_calculate_confidence_with_missing_mandatory(self, scorer):
        """Test confidence with missing mandatory skills"""
        result = MatchResult(
            job_id='job_128',
            ats_score=70,
            gate_passed=False,
            path=MatchPath.LLM_DISABLED,
            data_quality=DataQuality.LOW,
            matched_skills=['Python'],
            missing_skills=['JavaScript', 'Go'],
            mandatory_missing=['Go']  # One missing mandatory
        )
        
        confidence = JobScorer._calculate_confidence(result)
        # 70 - 10 (llm_disabled) - 10 (low quality) - 5 (1 missing mandatory) = 45
        assert confidence == 45
    
    def test_full_pipeline_heuristic_pass(self, scorer):
        """Test full pipeline when heuristic passes"""
        job_desc = "Looking for Python and JavaScript developer"
        result = scorer.score(job_desc, 'job_129')
        
        assert result.job_id == 'job_129'
        assert result.path == MatchPath.HEURISTIC_ONLY
        assert result.gate_passed == True
        assert result.ats_score > 0
    
    def test_full_pipeline_with_llm_fallback(self):
        """Test full pipeline with LLM fallback"""
        profile = {
            'name': 'Jane Doe',
            'primary_skills': ['Python'],
            'secondary_skills': [],
        }
        
        scorer = JobScorer(
            profile=profile,
            section_splitter=MockSectionSplitter(),
            spacy_extractor=MockSpacyExtractor(['Go', 'Kubernetes']),  # Skills not in profile
            llm_extractor=MockLLMExtractor(),
            ats_threshold=DEFAULT_ATS_THRESHOLD
        )
        
        job_desc = "Looking for Go developer"
        result = scorer.score(job_desc, 'job_130')
        
        assert result.job_id == 'job_130'
        # Should fallback to LLM since heuristic fails
        assert result.path in [MatchPath.LLM_RESCORED, MatchPath.LLM_DISABLED]


class TestSkillMatch:
    """Test SkillMatch dataclass"""
    
    def test_skill_match_creation(self):
        """Test creating a SkillMatch"""
        skill = SkillMatch(
            name='Python',
            requirement='mandatory',
            source='heuristic',
            is_new=False,
            evidence='mentioned in requirements'
        )
        
        assert skill.name == 'Python'
        assert skill.requirement == 'mandatory'
        assert skill.source == 'heuristic'
        assert skill.is_new == False


class TestMatchResult:
    """Test MatchResult dataclass"""
    
    def test_match_result_to_dict(self):
        """Test converting MatchResult to dictionary"""
        result = MatchResult(
            job_id='job_131',
            ats_score=85,
            gate_passed=True,
            matched_skills=['Python', 'JavaScript'],
            missing_skills=['Go'],
            mandatory_missing=[],
            skills=[
                SkillMatch(name='Python', requirement='mandatory', source='heuristic'),
                SkillMatch(name='JavaScript', requirement='preferred', source='heuristic'),
            ],
            path=MatchPath.HEURISTIC_ONLY,
            data_quality=DataQuality.HIGH,
            warnings=['Some warning'],
        )
        
        data = result.to_dict()
        
        assert data['job_id'] == 'job_131'
        assert data['ats_score'] == 85
        assert data['gate_passed'] == True
        assert data['path'] == 'heuristic_only'
        assert data['data_quality'] == 'high'
        assert len(data['skills']) == 2
        assert data['matched_skills'] == ['Python', 'JavaScript']
    
    def test_match_result_to_json(self):
        """Test converting MatchResult to JSON string"""
        result = MatchResult(
            job_id='job_132',
            ats_score=90,
            gate_passed=True,
            matched_skills=['Python'],
            missing_skills=[],
            mandatory_missing=[],
            skills=[SkillMatch(name='Python', requirement='mandatory', source='heuristic')],
            path=MatchPath.HEURISTIC_ONLY,
            data_quality=DataQuality.HIGH,
        )
        
        json_str = result.to_json_str()
        
        assert 'job_132' in json_str
        assert '"ats_score": 90' in json_str
        assert '"gate_passed": true' in json_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
