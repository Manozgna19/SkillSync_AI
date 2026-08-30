import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.progress import Assessment, AssessmentResult
from app.schemas.progress import AssessmentOut, AssessmentSubmit, AssessmentResultOut
from app.services import adaptive_service

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def _strip_answers(questions: list) -> list:
    """Never send correct_index to the client."""
    return [{"question": q["question"], "options": q["options"]} for q in questions]


@router.get("", response_model=list[AssessmentOut])
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).all()
    return [
        AssessmentOut(id=a.id, title=a.title, questions=_strip_answers(a.questions))
        for a in assessments
    ]


@router.post("/{assessment_id}/submit", response_model=AssessmentResultOut)
def submit_assessment(
    assessment_id: uuid.UUID,
    payload: AssessmentSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = assessment.questions
    if len(payload.answers) != len(questions):
        raise HTTPException(status_code=400, detail="Answer count does not match question count")

    correct = sum(
        1
        for given, q in zip(payload.answers, questions)
        if given == q.get("correct_index")
    )
    score = round(100 * correct / len(questions), 2) if questions else 0.0

    result = AssessmentResult(
        id=uuid.uuid4(),
        user_id=current_user.id,
        assessment_id=assessment.id,
        score=score,
        answers=payload.answers,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    # Adaptive learning: update skill proficiency based on this result.
    adaptive_service.apply_assessment_result(current_user.id, assessment, score, db)

    return result
