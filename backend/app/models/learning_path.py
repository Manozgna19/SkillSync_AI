import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Boolean, Integer, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    phase_order = Column(Integer, nullable=False)
    status = Column(String(50), default="not_started")
    completion_percentage = Column(Integer, default=0)
    recommendation_score = Column(Numeric(5, 2))
    reasons = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    phase_order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="not_started")
    completion_percentage = Column(Integer, default=0)
