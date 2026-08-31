import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.user import User
from app.models.profile import LearnerProfile
from app.models.recommendation import (
    Recommendation,
    RecommendationFeedback,
)
from app.models.resource import Resource

from app.schemas.resource import (
    RecommendationOut,
    ResourceOut,
    RecommendationFeedbackIn,
)

from app.recommender.engine import (
    generate_recommendations,
)

from app.ai.explanation import (
    explain_recommendation,
)

from app.services import adaptive_service


router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
)


# ============================================================
# GENERATE PERSONALIZED RECOMMENDATIONS
# ============================================================

@router.post(
    "/generate",
    response_model=list[RecommendationOut],
)
def generate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    profile = (
        db.query(LearnerProfile)
        .filter(
            LearnerProfile.user_id
            == current_user.id
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Learner profile not found.",
        )

    if not profile.career_goal:
        raise HTTPException(
            status_code=400,
            detail=(
                "Set a career goal first "
                "via the goal or profile page."
            ),
        )

    scored = generate_recommendations(
        current_user.id,
        profile.career_goal,
        db,
    )

    if not scored:
        return []

    output = []

    for scored_resource in scored:

        explanation = explain_recommendation(
            profile.career_goal,
            scored_resource.resource.title,
            scored_resource.reasons,
        )

        recommendation = Recommendation(
            id=uuid.uuid4(),
            user_id=current_user.id,
            resource_id=scored_resource.resource.id,
            score=scored_resource.score,
            reasons=scored_resource.reasons,
            explanation=explanation,
        )

        db.add(recommendation)

        output.append(
            RecommendationOut(
                id=recommendation.id,
                resource=ResourceOut.model_validate(
                    scored_resource.resource
                ),
                score=float(
                    scored_resource.score
                ),
                reasons=scored_resource.reasons,
                explanation=explanation,
            )
        )

    db.commit()

    return output


# ============================================================
# LIST PREVIOUS RECOMMENDATIONS
# ============================================================

@router.get(
    "",
    response_model=list[RecommendationOut],
)
def list_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    rows = (
        db.query(
            Recommendation,
            Resource,
        )
        .join(
            Resource,
            Resource.id
            == Recommendation.resource_id,
        )
        .filter(
            Recommendation.user_id
            == current_user.id
        )
        .order_by(
            Recommendation.created_at.desc()
        )
        .limit(20)
        .all()
    )

    return [
        RecommendationOut(
            id=recommendation.id,
            resource=ResourceOut.model_validate(
                resource
            ),
            score=float(
                recommendation.score
            ),
            reasons=(
                recommendation.reasons
                or []
            ),
            explanation=(
                recommendation.explanation
                or ""
            ),
        )
        for recommendation, resource in rows
    ]


# ============================================================
# RECOMMENDATION FEEDBACK
# ============================================================

@router.post(
    "/{recommendation_id}/feedback"
)
def give_feedback(
    recommendation_id: uuid.UUID,
    payload: RecommendationFeedbackIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    recommendation = (
        db.query(Recommendation)
        .filter(
            Recommendation.id
            == recommendation_id,
            Recommendation.user_id
            == current_user.id,
        )
        .first()
    )

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found.",
        )

    resource = (
        db.query(Resource)
        .filter(
            Resource.id
            == recommendation.resource_id
        )
        .first()
    )

    feedback = RecommendationFeedback(
        id=uuid.uuid4(),
        recommendation_id=recommendation.id,
        user_id=current_user.id,
        feedback=payload.feedback,
    )

    db.add(feedback)

    db.commit()

    adaptive_hint = (
        adaptive_service
        .apply_recommendation_feedback(
            payload.feedback,
            resource.difficulty
            if resource
            else "",
        )
    )

    return {
        "status": "recorded",
        "adaptive_hint": adaptive_hint,
    }