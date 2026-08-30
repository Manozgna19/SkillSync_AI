import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Recommendation(Base):
    """
    Stores a personalized recommendation generated for a learner.
    """

    __tablename__ = "recommendations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    resource_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "resources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Final recommendation score, stored as 0-100.
    score = Column(
        Numeric(6, 3),
        nullable=False,
    )

    # Why this resource was recommended.
    reasons = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    # AI-generated explanation.
    explanation = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class RecommendationFeedback(Base):
    """
    Stores learner feedback about a recommendation.

    Allowed feedback:
        too_difficult
        too_easy
        not_useful
        helpful
    """

    __tablename__ = "recommendation_feedback"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    recommendation_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "recommendations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    feedback = Column(
        String(50),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )