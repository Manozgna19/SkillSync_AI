"""
Generates an ordered, personalized learning path (roadmap) for a learner.

Takes the top recommendations from the recommendation engine and arranges
them into phases in prerequisite-respecting order (topological-ish sort by
number of unmet prerequisite skills, then by recommendation score).
"""
import uuid
from sqlalchemy.orm import Session

from app.models.learning_path import LearningPath, LearningPathItem
from app.models.resource import ResourcePrerequisite
from app.models.goal import Goal
from app.recommender.engine import generate_recommendations, ScoredResource


def _prerequisite_depth(db: Session, resource_id) -> int:
    """Rough proxy for ordering: how many prerequisite skills a resource has."""
    return (
        db.query(ResourcePrerequisite)
        .filter(ResourcePrerequisite.resource_id == resource_id)
        .count()
    )


def generate_learning_path(user_id, goal: str, db: Session, goal_id=None, top_n: int = 12) -> LearningPath:
    scored_resources = generate_recommendations(user_id, goal, db, top_n=top_n)

    # Order: fewer unmet prerequisites first (foundational material earlier),
    # then higher recommendation score.
    def sort_key(sr: ScoredResource):
        depth = _prerequisite_depth(db, sr.resource.id)
        return (depth, -sr.score)

    ordered = sorted(scored_resources, key=sort_key)

    # Deactivate any existing active path for this user before creating a new one.
    db.query(LearningPath).filter(
        LearningPath.user_id == user_id, LearningPath.is_active == True  # noqa: E712
    ).update({"is_active": False})

    path = LearningPath(
        id=uuid.uuid4(),
        user_id=user_id,
        goal_id=goal_id,
        title=f"{goal} Roadmap",
        is_active=True,
    )
    db.add(path)
    db.flush()

    for i, sr in enumerate(ordered, start=1):
        item = LearningPathItem(
            id=uuid.uuid4(),
            learning_path_id=path.id,
            resource_id=sr.resource.id,
            phase_order=i,
            status="not_started",
            completion_percentage=0,
            recommendation_score=sr.score,
            reasons=sr.reasons,
        )
        db.add(item)

    db.commit()
    db.refresh(path)
    return path
