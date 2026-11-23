from enum import Enum
from pydantic import BaseModel, Field


class RequirementLevel(str, Enum):
    MANDATORY = "mandatory"
    PREFERRED = "preferred"
    OPTIONAL = "optional"
    UNSPECIFIED = "unspecified"


class ExtractedSkill(BaseModel):
    name: str
    level: RequirementLevel
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)


class SkillExtraction(BaseModel):
    skills: list[ExtractedSkill]