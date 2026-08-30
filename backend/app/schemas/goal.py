import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class GoalCreate(BaseModel):
    text: str  # natural language goal, e.g. "I want to become a backend developer..."


class GoalOut(BaseModel):
    id: uuid.UUID
    raw_text: str
    normalized_goal: str
    experience_level: Optional[str]
    extracted_current_skills: Optional[List[str]]
    extracted_missing_skills: Optional[List[str]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
