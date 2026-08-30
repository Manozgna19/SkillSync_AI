import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.profile import LearnerProfile
from app.models.goal import Goal
from app.models.resource import Resource, CompletedResource
from app.models.learning_path import LearningPath, LearningPathItem
from app.schemas.learning_path import LearningPathOut, LearningPathItemOut, LearningPathItemUpdate
from app.schemas.resource import ResourceOut
from app.services.learning_path_service import generate_learning_path

router = APIRouter(prefix="/api/learning-path", tags=["learning-path"])


def _serialize(path: LearningPath, db: Session) -> LearningPathOut:
    rows = (
        db.query(LearningPathItem, Resource)
        .join(Resource, Resource.id == LearningPathItem.resource_id)
        .filter(LearningPathItem.learning_path_id == path.id)
        .order_by(LearningPathItem.phase_order)
        .all()
    )
    items = [
        LearningPathItemOut(
            id=item.id,
            resource=ResourceOut.model_validate(resource),
            phase_order=item.phase_order,
            status=item.status,
            completion_percentage=item.completion_percentage,
            recommendation_score=float(item.recommendation_score) if item.recommendation_score is not None else None,
            reasons=item.reasons or [],
        )
        for item, resource in rows
    ]
    return LearningPathOut(id=path.id, title=path.title, is_active=path.is_active, items=items)


@router.post("/generate", response_model=LearningPathOut, status_code=201)
def generate(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    if not profile or not profile.career_goal:
        raise HTTPException(status_code=400, detail="Set a career goal first (via /goal or /profile)")

    active_goal = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id, Goal.is_active == True)  # noqa: E712
        .first()
    )
    path = generate_learning_path(
        current_user.id, profile.career_goal, db, goal_id=active_goal.id if active_goal else None
    )
    return _serialize(path, db)


@router.get("", response_model=LearningPathOut)
def get_active_path(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == current_user.id, LearningPath.is_active == True)  # noqa: E712
        .first()
    )
    if not path:
        raise HTTPException(status_code=404, detail="No active learning path yet - generate one first")
    return _serialize(path, db)


@router.put("/items/{item_id}", response_model=LearningPathItemOut)
def update_item(
    item_id: uuid.UUID,
    payload: LearningPathItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(LearningPathItem)
        .join(LearningPath, LearningPath.id == LearningPathItem.learning_path_id)
        .filter(LearningPathItem.id == item_id, LearningPath.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Learning path item not found")

    if payload.status is not None:
        if payload.status not in ("not_started", "in_progress", "completed"):
            raise HTTPException(status_code=400, detail="Invalid status")
        item.status = payload.status
        if payload.status == "completed":
            item.completion_percentage = 100
            existing = (
                db.query(CompletedResource)
                .filter(
                    CompletedResource.user_id == current_user.id,
                    CompletedResource.resource_id == item.resource_id,
                )
                .first()
            )
            if not existing:
                db.add(
                    CompletedResource(
                        id=uuid.uuid4(), user_id=current_user.id, resource_id=item.resource_id
                    )
                )

    if payload.completion_percentage is not None:
        item.completion_percentage = max(0, min(100, payload.completion_percentage))
        if item.completion_percentage == 100:
            item.status = "completed"
        elif item.completion_percentage > 0 and item.status == "not_started":
            item.status = "in_progress"

    db.commit()
    db.refresh(item)
    resource = db.query(Resource).filter(Resource.id == item.resource_id).first()
    return LearningPathItemOut(
        id=item.id,
        resource=ResourceOut.model_validate(resource),
        phase_order=item.phase_order,
        status=item.status,
        completion_percentage=item.completion_percentage,
        recommendation_score=float(item.recommendation_score) if item.recommendation_score is not None else None,
        reasons=item.reasons or [],
    )
