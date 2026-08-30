import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.goal import Goal
from app.models.profile import LearnerProfile
from app.models.skill import Skill, UserSkill
from app.schemas.goal import GoalCreate, GoalOut
from app.ai.goal_extraction import extract_goal

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(payload: GoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    extracted = extract_goal(payload.text, db)

    # Deactivate previous goals
    db.query(Goal).filter(Goal.user_id == current_user.id, Goal.is_active == True).update(  # noqa: E712
        {"is_active": False}
    )

    goal = Goal(
        id=uuid.uuid4(),
        user_id=current_user.id,
        raw_text=payload.text,
        normalized_goal=extracted["goal"],
        experience_level=extracted["experience_level"],
        extracted_current_skills=extracted["current_skills"],
        extracted_missing_skills=[],  # computed on demand via skill-gap endpoint
        is_active=True,
    )
    db.add(goal)

    # Sync the learner profile with what we just learned.
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    if profile:
        profile.career_goal = extracted["goal"]
        profile.experience_level = extracted["experience_level"]
        if extracted["weekly_hours"]:
            profile.weekly_hours = extracted["weekly_hours"]
        if extracted["interests"]:
            profile.interests = list(set((profile.interests or []) + extracted["interests"]))

    # Record any newly-mentioned current skills.
    for skill_name in extracted["current_skills"]:
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill:
            continue
        existing = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill.id)
            .first()
        )
        if not existing:
            db.add(
                UserSkill(
                    id=uuid.uuid4(),
                    user_id=current_user.id,
                    skill_id=skill.id,
                    proficiency=60,
                    source="inferred",
                )
            )

    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=list[GoalOut])
def list_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(Goal.created_at.desc())
        .all()
    )
