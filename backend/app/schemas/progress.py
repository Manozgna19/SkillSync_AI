import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class ProgressCreate(BaseModel):
    learning_path_item_id: Optional[uuid.UUID] = None
    hours_logged: float = 0
    status: str = "in_progress"
    completion_percentage: int = 0
    notes: Optional[str] = None


class ProgressUpdate(BaseModel):
    hours_logged: Optional[float] = None
    status: Optional[str] = None
    completion_percentage: Optional[int] = None
    notes: Optional[str] = None


class ProgressOut(BaseModel):
    id: uuid.UUID
    learning_path_item_id: Optional[uuid.UUID]
    hours_logged: float
    status: str
    completion_percentage: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentOut(BaseModel):
    id: uuid.UUID
    title: str
    questions: List[Dict[str, Any]]  # correct_index stripped before sending to client

    class Config:
        from_attributes = True


class AssessmentSubmit(BaseModel):
    answers: List[int]  # index chosen per question, in order


class AssessmentResultOut(BaseModel):
    id: uuid.UUID
    assessment_id: uuid.UUID
    score: float
    taken_at: datetime

    class Config:
        from_attributes = True
