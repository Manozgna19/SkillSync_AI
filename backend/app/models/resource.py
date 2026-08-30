import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.core.database import Base


class Resource(Base):
    """
    Learning resource such as a course, video, article,
    documentation page, project, or assessment.
    """

    __tablename__ = "resources"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    provider = Column(
        String(255),
        nullable=True,
    )

    url = Column(
        String(500),
        nullable=True,
    )

    resource_type = Column(
        String(50),
        nullable=False,
    )

    difficulty = Column(
        String(50),
        nullable=False,
        default="Beginner",
    )

    estimated_hours = Column(
        Numeric(5, 2),
        nullable=False,
        default=1,
    )

    embedding = Column(
        Vector(settings.EMBEDDING_DIM)
    )

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class ResourceSkill(Base):
    """
    Maps a learning resource to a skill taught by that resource.
    """

    __tablename__ = "resource_skills"

    __table_args__ = (
        UniqueConstraint(
            "resource_id",
            "skill_id",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    resource_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "resources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    skill_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


class ResourcePrerequisite(Base):
    """
    Defines skills required before a learner should use
    a particular resource.
    """

    __tablename__ = "resource_prerequisites"

    __table_args__ = (
        UniqueConstraint(
            "resource_id",
            "prerequisite_skill_id",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    resource_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "resources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    prerequisite_skill_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


class CompletedResource(Base):
    """
    Stores resources completed by a learner.
    """

    __tablename__ = "completed_resources"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "resource_id",
        ),
    )

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
    )

    resource_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "resources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    completed_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )