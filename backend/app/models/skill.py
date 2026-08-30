import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(100))
    difficulty = Column(String(50), default="Beginner")
    embedding = Column(Vector(settings.EMBEDDING_DIM))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"
    __table_args__ = (UniqueConstraint("skill_id", "prerequisite_skill_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    prerequisite_skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(Integer, default=50)  # 0-100
    source = Column(String(50), default="self_reported")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
