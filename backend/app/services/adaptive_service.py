"""
Adaptive learning logic: reacts to assessment scores and recommendation
feedback by adjusting the learner's stored skill proficiency, which in
turn changes future skill-gap analysis and recommendations.
"""
import uuid
from sqlalchemy.orm import Session

from app.models.skill import UserSkill
from app.models.progress import Assessment


def apply_assessment_result(user_id, assessment: Assessment, score: float, db: Session):
    """
    Update the learner's proficiency for the assessment's skill based on
    their score. Low scores lower proficiency (surfacing the skill as a
    gap again so easier resources get recommended); high scores raise it.
    """
    if not assessment.skill_id:
        return

    user_skill = (
        db.query(UserSkill)
        .filter(UserSkill.user_id == user_id, UserSkill.skill_id == assessment.skill_id)
        .first()
    )

    # Map score (0-100) to a proficiency delta.
    if score < 50:
        target_proficiency = min(30, int(score))  # weak skill -> mark as gap
    elif score < 75:
        target_proficiency = 60
    else:
        target_proficiency = 90

    if user_skill:
        user_skill.proficiency = target_proficiency
        user_skill.source = "assessment"
    else:
        user_skill = UserSkill(
            id=uuid.uuid4(),
            user_id=user_id,
            skill_id=assessment.skill_id,
            proficiency=target_proficiency,
            source="assessment",
        )
        db.add(user_skill)
    db.commit()


def apply_recommendation_feedback(feedback: str, resource_difficulty: str) -> dict:
    """
    Returns adjustment hints that the recommendation engine's difficulty
    matching implicitly benefits from on the next generation call, since
    `too_difficult`/`too_easy` feedback is stored and penalizes/boosts
    similar resource types via `_get_feedback_penalty`. This function is a
    hook point for any additional immediate side effects.
    """
    hints = {"too_difficult": "prefer_easier", "too_easy": "prefer_harder", "not_useful": "deprioritize_type"}
    return {"action": hints.get(feedback, "none")}
