import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.profile import LearnerProfile
from app.schemas.skill import SkillOut, UserSkillsUpdate, UserSkillOut, SkillGapResponse
from app.services import skill_gap_service

router = APIRouter(prefix="/api", tags=["skills"])


@router.get("/skills", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.category, Skill.name).all()


@router.get("/skills/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: uuid.UUID, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.get("/profile/skills", response_model=list[UserSkillOut])
def get_my_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(UserSkill, Skill.name)
        .join(Skill, Skill.id == UserSkill.skill_id)
        .filter(UserSkill.user_id == current_user.id)
        .all()
    )
    return [
        UserSkillOut(skill_id=us.skill_id, skill_name=name, proficiency=us.proficiency, source=us.source)
        for us, name in rows
    ]


@router.put("/profile/skills", response_model=list[UserSkillOut])
def update_my_skills(
    payload: UserSkillsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for item in payload.skills:
        skill = db.query(Skill).filter(Skill.id == item.skill_id).first()
        if not skill:
            raise HTTPException(status_code=400, detail=f"Unknown skill_id {item.skill_id}")

        existing = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == current_user.id, UserSkill.skill_id == item.skill_id)
            .first()
        )
        if existing:
            existing.proficiency = item.proficiency
            existing.source = "self_reported"
        else:
            db.add(
                UserSkill(
                    id=uuid.uuid4(),
                    user_id=current_user.id,
                    skill_id=item.skill_id,
                    proficiency=item.proficiency,
                    source="self_reported",
                )
            )
    db.commit()
    return get_my_skills(current_user, db)


@router.get("/skills/gap-analysis/me", response_model=SkillGapResponse)
def my_skill_gap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    if not profile or not profile.career_goal:
        raise HTTPException(status_code=400, detail="Set a career goal on your profile first")
    return skill_gap_service.analyze_skill_gap(current_user.id, profile.career_goal, db)
