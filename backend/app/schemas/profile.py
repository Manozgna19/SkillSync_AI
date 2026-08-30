import uuid
from typing import Optional, List

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    experience_level: Optional[str] = Field(default=None, pattern="^(Beginner|Intermediate|Advanced)$")
    occupation: Optional[str] = None
    career_goal: Optional[str] = None
    interests: Optional[List[str]] = None
    preferred_learning_style: Optional[str] = Field(
        default=None, pattern="^(Visual|Reading|Hands-on|Mixed)$"
    )
    weekly_hours: Optional[int] = Field(default=None, ge=1, le=80)


class ProfileOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    experience_level: Optional[str]
    occupation: Optional[str]
    career_goal: Optional[str]
    interests: Optional[List[str]]
    preferred_learning_style: Optional[str]
    weekly_hours: Optional[int]

    class Config:
        from_attributes = True
