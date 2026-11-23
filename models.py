from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# =====================================================================
# PHASE 1: USER PROFILE MODELS
# =====================================================================

class UserProfileBasic(BaseModel):
    """Basic user profile information (form stage 1)"""
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    current_location: str = Field(..., description="Current location")
    timezone: Optional[str] = Field("UTC", description="User's timezone")


class UserProfileExperience(BaseModel):
    """Experience and level information (form stage 2)"""
    years_of_experience: int = Field(0, ge=0, le=70, description="Years of professional experience")
    current_level: str = Field("mid", description="Current professional level: entry, mid, senior, lead, executive")
    target_level: str = Field("mid", description="Target professional level")


class UserProfileSkills(BaseModel):
    """Skills and technologies (form stage 3)"""
    primary_skills: List[str] = Field(
        default_factory=list,
        description="Core technical skills (e.g., ['Python', 'JavaScript', 'React'])"
    )
    secondary_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have skills"
    )
    must_have_skills: List[str] = Field(
        default_factory=list,
        description="Skills that MUST be in the job description"
    )


class UserProfileJobPreferences(BaseModel):
    """Job and company preferences (form stage 4)"""
    target_job_titles: List[str] = Field(
        default_factory=list,
        description="Target job titles (e.g., ['Software Engineer', 'Senior Software Engineer'])"
    )
    target_companies: List[str] = Field(
        default_factory=list,
        description="Preferred companies to work for"
    )
    exclude_companies: List[str] = Field(
        default_factory=list,
        description="Companies to exclude from search"
    )
    
    willing_locations: List[str] = Field(
        default_factory=list,
        description="Locations willing to work in (e.g., ['India', 'Singapore', 'USA'])"
    )
    willing_remote_level: str = Field(
        "hybrid",
        description="Remote work preference: remote, hybrid, onsite, any"
    )
    willing_relocation: bool = Field(False, description="Willing to relocate?")
    willing_travel: bool = Field(False, description="Willing to travel?")
    
    job_type_preference: List[str] = Field(
        default_factory=lambda: ["Full Time"],
        description="Job type: Full Time, Contract, Part-time, Internship, etc"
    )
    min_salary: int = Field(0, ge=0, description="Minimum acceptable salary (0 = no minimum)")
    currency: str = Field("USD", description="Salary currency")


class UserProfileCompanyPreferences(BaseModel):
    """Company culture and industry preferences (form stage 5)"""
    industry_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred industries (e.g., ['Technology', 'SaaS', 'FinTech'])"
    )
    avoid_industries: List[str] = Field(
        default_factory=list,
        description="Industries to avoid"
    )
    company_size_preference: List[str] = Field(
        default_factory=list,
        description="Preferred company size: Startup, SMB, Mid-size, Enterprise"
    )
    
    work_culture_keywords: List[str] = Field(
        default_factory=list,
        description="Work culture preferences (e.g., ['Innovation', 'Collaboration', 'Fast-paced'])"
    )
    benefits_importance: List[str] = Field(
        default_factory=list,
        description="Important benefits (e.g., ['Health Insurance', '401k', 'Stock Options', 'Remote Work'])"
    )


class UserProfileSettings(BaseModel):
    """Profile settings and configuration"""
    is_active: bool = Field(True, description="Is this profile active?")
    notes: Optional[str] = Field(None, description="Any additional notes about the profile")
    form_stage: str = Field("basic_info", description="Track form progress: basic_info, experience, skills, preferences, company, review")


class UserProfile(BaseModel):
    """Complete user profile with all stages combined - aligned with cleaned DB schema"""
    id: Optional[UUID] = None
    
    # Basic Info
    name: str
    email: str
    phone: Optional[str] = None
    current_location: str
    timezone: Optional[str] = "UTC"
    
    # Experience
    years_of_experience: int = 0
    current_level: str = "mid"
    target_level: str = "mid"
    
    # Skills
    primary_skills: List[str] = Field(default_factory=list)
    secondary_skills: List[str] = Field(default_factory=list)
    must_have_skills: List[str] = Field(default_factory=list)
    
    # Job Preferences
    target_job_titles: List[str] = Field(default_factory=list)
    target_companies: List[str] = Field(default_factory=list)
    exclude_companies: List[str] = Field(default_factory=list)
    willing_locations: List[str] = Field(default_factory=list)
    willing_remote_level: str = "hybrid"
    willing_relocation: bool = False
    willing_travel: bool = False
    job_type_preference: List[str] = Field(default_factory=lambda: ["Full Time"])
    min_salary: int = 0
    currency: str = "USD"
    
    # Company Preferences
    industry_preferences: List[str] = Field(default_factory=list)
    avoid_industries: List[str] = Field(default_factory=list)
    company_size_preference: List[str] = Field(default_factory=list)
    work_culture_keywords: List[str] = Field(default_factory=list)
    benefits_importance: List[str] = Field(default_factory=list)
    
    # Settings
    is_active: bool = True
    notes: Optional[str] = None
    form_stage: str = "basic_info"  # Track form progress: basic_info, experience, skills, preferences, company, review
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "current_location": "India",
                "target_job_titles": ["Software Engineer", "Senior Software Engineer"],
                "primary_skills": ["Python", "JavaScript", "React"],
                "must_have_skills": ["Python", "JavaScript"],
                "target_companies": ["Google", "Microsoft", "Amazon"],
                "willing_locations": ["India", "Singapore", "USA"],
                "willing_remote_level": "hybrid",
                "profile_score_threshold": 70
            }
        }


class UserProfileResponse(BaseModel):
    """Response model for API endpoints"""
    success: bool
    message: str
    profile: Optional[UserProfile] = None
    data: Optional[Dict[str, Any]] = None


# =====================================================================
# PHASE 2: PROFILE-LEVEL JOB SCORING MODELS (Junction Table)
# =====================================================================

class ProfileJobScore(BaseModel):
    """
    Score of a single job against a user's profile.
    This is the junction table between profiles and jobs.
    Each (profile_id, job_id) pair has exactly one score.
    """
    profile_id: UUID
    job_id: str
    
    # Overall Score (0-100)
    profile_score: int = Field(..., ge=0, le=100, description="Overall fit score for this job against profile")
    profile_match_reason: Optional[str] = Field(None, description="LLM explanation of why this score was given")
    
    # Detailed Scoring Breakdown (each 0-20)
    career_fit: int = Field(0, ge=0, le=20, description="Career alignment score: does it align with career goals?")
    skills_fit: int = Field(0, ge=0, le=20, description="Skills match score: do they have required/preferred skills?")
    seniority_fit: int = Field(0, ge=0, le=20, description="Seniority alignment: is role appropriate for their level?")
    location_fit: int = Field(0, ge=0, le=20, description="Location/remote fit: matches preferences?")
    culture_fit: int = Field(0, ge=0, le=20, description="Company culture fit: company size, industry, signals?")
    
    # Reasoning
    key_positives: List[str] = Field(default_factory=list, description="Reasons why this job is a good fit")
    key_concerns: List[str] = Field(default_factory=list, description="Reasons why there might be concerns")
    should_apply: bool = Field(False, description="LLM recommendation: should user apply?")
    
    # Timestamps
    scored_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_id": "linkedin-12345",
                "profile_score": 85,
                "profile_match_reason": "Strong Python background with matching seniority level and remote work preference",
                "career_fit": 18,
                "skills_fit": 20,
                "seniority_fit": 17,
                "location_fit": 20,
                "culture_fit": 10,
                "key_positives": ["Strong tech stack match", "Remote position", "Growth opportunity"],
                "key_concerns": ["Startup with limited stability"],
                "should_apply": True,
                "scored_at": "2026-10-25T10:30:00Z"
            }
        }


class JobWithProfileScore(BaseModel):
    """
    Complete job data with profile score for a specific user.
    This is what you show to the user in their job feed.
    """
    # Job Details
    job_id: str
    company: str
    job_title: str
    location: str
    level: Optional[str] = None
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_at: Optional[datetime] = None
    is_active: bool = True
    
    # Profile Score (only present if this job has been scored for this user)
    profile_score: Optional[int] = None
    profile_match_reason: Optional[str] = None
    should_apply: Optional[bool] = None
    scored_at: Optional[datetime] = None
    
    # Breakdown (optional)
    career_fit: Optional[int] = None
    skills_fit: Optional[int] = None
    seniority_fit: Optional[int] = None
    location_fit: Optional[int] = None
    culture_fit: Optional[int] = None
    key_positives: Optional[List[str]] = None
    key_concerns: Optional[List[str]] = None


class ProfileScoringStats(BaseModel):
    """Statistics about profile scoring for a user"""
    profile_id: UUID
    profile_name: str
    total_scored_jobs: int = 0
    above_threshold_jobs: int = 0
    recommended_jobs: int = 0
    avg_score: Optional[float] = None
    highest_score: Optional[int] = None
    lowest_score: Optional[int] = None
    last_scored_at: Optional[datetime] = None


class ProfileJobScoringRequest(BaseModel):
    """Request to score a batch of jobs for a profile"""
    profile_id: UUID
    job_ids: List[str] = Field(..., description="Job IDs to score")
    rescore_existing: bool = Field(False, description="Should we rescore jobs that were already scored?")


# =====================================================================
# EXISTING MODELS (Resume & Related)
# =====================================================================

class Education(BaseModel):
    degree: str = ""
    field_of_study: str = ""
    institution: str = ""
    start_year: str = ""
    end_year: str = ""

class Experience(BaseModel):
    job_title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""

class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)

class Certification(BaseModel):
    name: str = ""
    issuer: str = ""
    year: str = ""

class Links(BaseModel):
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""

class Resume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    links: Links = Field(default_factory=Links)

# --- Pydantic models for Stage 1 & Stage 2 LLM structured output ---
class RoleFocus(BaseModel):
    company: str
    job_title: str
    key_achievements_to_highlight: List[str] = Field(
        default_factory=list,
        description="Key responsibilities, tools, or achievements from this role in the base resume to emphasize."
    )
    points_to_condense_or_omit: List[str] = Field(
        default_factory=list,
        description="Responsibilities or tasks from this role in the base resume that are irrelevant to the target JD."
    )

class CurationPlan(BaseModel):
    strategy_summary: str = Field(
        description="Brief 1-2 sentence strategy explaining how the candidate's actual background aligns with the target job."
    )
    selected_project_names: List[str] = Field(
        default_factory=list,
        description="Exact names of projects from the base resume to include (choose 1 to 3 most relevant projects; omit irrelevant ones)."
    )
    selected_skills: List[str] = Field(
        default_factory=list,
        description="Curated list of 8 to 15 skills strictly from the candidate's base resume that match the target JD."
    )
    experience_guidance: List[RoleFocus] = Field(
        default_factory=list,
        description="Guidance for each job in the candidate's history on what to highlight or prune."
    )

class TailoredResumeContent(BaseModel):
    summary: str = Field(
        description="Impactful 2-3 sentence professional summary tailored to the target job, preserving core identity."
    )
    skills: List[str] = Field(
        default_factory=list,
        description="Curated list of 8-15 skills matching the target job (strictly subset of base resume)."
    )
    experience: List[Experience] = Field(
        default_factory=list,
        description="List of all work experiences with tailored, newline-separated bullet-point descriptions."
    )
    projects: List[Project] = Field(
        default_factory=list,
        description="List of selected projects with tailored, newline-separated bullet-point descriptions."
    )

# --- Legacy models kept for backwards compatibility ---
class SummaryOutput(BaseModel):
    summary: str

class SkillsOutput(BaseModel):
    skills: List[str]

class ExperienceListOutput(BaseModel):
    experience: List[Experience]

class SingleExperienceOutput(BaseModel):
    experience: Experience

class ProjectListOutput(BaseModel):
    projects: List[Project]

class SingleProjectOutput(BaseModel):
    project: Project

class ValidationResponse(BaseModel):
    is_valid: bool
    reason: str

class Config:
    extra = 'allow'

# =====================================================================
# IMPROVED WORKFLOW: JOB MATCHING MODELS
# =====================================================================

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class MatchPath(str, Enum):
    """Describes which stages of the matching pipeline were used"""
    HEURISTIC_ONLY = "heuristic_only"        # Spacy found skills, gate passed
    LLM_RESCORED = "llm_rescored"            # Spacy failed, LLM found skills, re-scored
    LLM_FAILED = "llm_failed"                # Spacy failed, LLM also failed/error
    LLM_DISABLED = "llm_disabled"            # Spacy failed but LLM not available


class DataQuality(str, Enum):
    """Describes the quality of the job description"""
    HIGH = "high"      # Well-structured with clear sections
    LOW = "low"        # Poorly structured or vague


@dataclass(frozen=True)
class SkillMatch:
    """Represents a matched skill with its metadata"""
    name: str                           # Skill name (canonical)
    requirement: str                    # mandatory | preferred | unspecified
    source: str                         # heuristic | llm | both
    is_new: bool = False                # Is this a new skill not in skills.txt?
    evidence: Optional[str] = None      # Evidence from job description


@dataclass
class MatchResult:
    """Complete job matching result for a profile"""
    job_id: str
    profile_id: Optional[str] = None
    
    # Scoring
    ats_score: int = 0                  # 0-100, ATS match percentage
    gate_passed: bool = False           # Does profile fit this job?
    
    # Skill details
    matched_skills: list[str] = field(default_factory=list)        # All matched skills
    missing_skills: list[str] = field(default_factory=list)        # All skills not in profile
    mandatory_missing: list[str] = field(default_factory=list)     # Mandatory skills not in profile
    skills: list[SkillMatch] = field(default_factory=list)         # Detailed skill info
    new_skills: list[SkillMatch] = field(default_factory=list)
    # Pipeline metadata
    path: MatchPath = MatchPath.HEURISTIC_ONLY
    data_quality: DataQuality = DataQuality.LOW
    warnings: list[str] = field(default_factory=list)
    
    # Confidence and additional metrics
    confidence_score: int = 0           # 0-100, overall confidence
    heuristic_score: Optional[int] = None    # Score before LLM
    llm_score: Optional[int] = None         # Score after LLM
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['path'] = self.path.value
        data['data_quality'] = self.data_quality.value
        data['skills'] = [
            {
                'name': s.name,
                'requirement': s.requirement,
                'source': s.source,
                'is_new': s.is_new,
                'evidence': s.evidence
            }
            for s in self.skills
        ]
        return data
    
    def to_json_str(self):
        """Convert to JSON string"""
        import json
        return json.dumps(self.to_dict())
