import uuid
from typing import Optional, List

from pydantic import BaseModel, Field


class ResourceOut(BaseModel):
    """
    Public representation of a learning resource.
    """

    id: uuid.UUID

    title: str

    description: Optional[str] = None

    provider: Optional[str] = None

    url: Optional[str] = None

    resource_type: str

    difficulty: str

    estimated_hours: float

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    """
    Public representation of a personalized recommendation.
    """

    id: uuid.UUID

    resource: ResourceOut

    score: float

    reasons: List[str] = Field(
        default_factory=list
    )

    explanation: str = ""

    class Config:
        from_attributes = True


class RecommendationFeedbackIn(BaseModel):
    """
    Learner feedback on a recommendation.
    """

    feedback: str

    def validate_feedback(self):
        allowed = {
            "too_difficult",
            "too_easy",
            "not_useful",
            "helpful",
        }

        if self.feedback not in allowed:
            raise ValueError(
                f"feedback must be one of: "
                f"{', '.join(sorted(allowed))}"
            )

        return self