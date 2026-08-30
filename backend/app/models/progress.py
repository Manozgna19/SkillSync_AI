import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_path_item_id = Column(UUID(as_uuid=True), ForeignKey("learning_path_items.id", ondelete="CASCADE"))
    hours_logged = Column(Numeric(5, 2), default=0)
    status = Column(String(50), default="in_progress")
    completion_percentage = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    questions = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    answers = Column(JSONB)
    taken_at = Column(DateTime(timezone=True), default=datetime.utcnow)
