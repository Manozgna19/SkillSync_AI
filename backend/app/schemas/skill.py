import uuid
from typing import Optional, List

from pydantic import BaseModel, Field


class SkillOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    category: Optional[str]
    difficulty: str

    class Config:
        from_attributes = True


class UserSkillIn(BaseModel):
    skill_id: uuid.UUID
    proficiency: int = Field(ge=0, le=100, default=50)


class UserSkillsUpdate(BaseModel):
    skills: List[UserSkillIn]


class UserSkillOut(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    proficiency: int
    source: str

    class Config:
        from_attributes = True


class SkillGapItem(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    status: str  # "have" | "missing"
    proficiency: int = 0


class SkillGapResponse(BaseModel):
    goal: str
    required_skills: List[SkillGapItem]
    missing_skills: List[str]
    have_skills: List[str]
