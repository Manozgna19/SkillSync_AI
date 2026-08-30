import uuid
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.resource import ResourceOut


class LearningPathItemOut(BaseModel):
    id: uuid.UUID
    resource: ResourceOut
    phase_order: int
    status: str
    completion_percentage: int
    recommendation_score: Optional[float]
    reasons: Optional[List[str]]

    class Config:
        from_attributes = True


class LearningPathOut(BaseModel):
    id: uuid.UUID
    title: str
    is_active: bool
    items: List[LearningPathItemOut]

    class Config:
        from_attributes = True


class LearningPathItemUpdate(BaseModel):
    status: Optional[str] = None  # not_started | in_progress | completed
    completion_percentage: Optional[int] = None
