import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.progress import Progress
from app.schemas.progress import ProgressCreate, ProgressUpdate, ProgressOut

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.post("", response_model=ProgressOut, status_code=201)
def create_progress(
    payload: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = Progress(
        id=uuid.uuid4(),
        user_id=current_user.id,
        learning_path_item_id=payload.learning_path_item_id,
        hours_logged=payload.hours_logged,
        status=payload.status,
        completion_percentage=payload.completion_percentage,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[ProgressOut])
def list_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Progress)
        .filter(Progress.user_id == current_user.id)
        .order_by(Progress.created_at.desc())
        .all()
    )


@router.put("/{progress_id}", response_model=ProgressOut)
def update_progress(
    progress_id: uuid.UUID,
    payload: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(Progress)
        .filter(Progress.id == progress_id, Progress.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Progress entry not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)
    return entry
