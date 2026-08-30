import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    experience_level = Column(String(50), default="Beginner")
    occupation = Column(String(255))
    career_goal = Column(String(255))
    interests = Column(ARRAY(String))
    preferred_learning_style = Column(String(50))
    weekly_hours = Column(Integer, default=5)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
