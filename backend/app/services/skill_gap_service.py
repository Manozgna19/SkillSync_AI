"""
Skill gap analysis: given a learner's current skills and a career goal,
determine which required skills they have and which are missing.

This is deterministic and driven by the structured skill/prerequisite
database - NOT hallucinated by the LLM (per project architecture rule).
"""
from typing import Dict
from sqlalchemy.orm import Session

from app.models.skill import Skill, UserSkill

# Maps each known career goal to the skills required to achieve it, in
# roughly the order they should be learned. This mirrors the seed data's
# prerequisite chains so goal -> required skills is deterministic.
GOAL_REQUIRED_SKILLS: Dict[str, list] = {
    "Full Stack Developer": [
        "Git", "HTML & CSS", "JavaScript", "Python", "SQL", "REST APIs",
        "React", "FastAPI", "Django", "Docker",
    ],
    "Backend Developer": [
        "Git", "Python", "SQL", "REST APIs", "FastAPI", "Django",
        "Docker", "System Design", "AWS",
    ],
    "Frontend Developer": [
        "Git", "HTML & CSS", "JavaScript", "React", "TypeScript",
        "REST APIs", "Web Accessibility",
    ],
    "Data Scientist": [
        "Python", "SQL", "Statistics", "Probability", "NumPy", "Pandas",
        "Data Visualization", "Machine Learning",
    ],
    "Machine Learning Engineer": [
        "Python", "SQL", "Statistics", "Probability", "Linear Algebra",
        "NumPy", "Pandas", "Machine Learning", "Deep Learning",
        "TensorFlow", "PyTorch", "MLOps",
    ],
    "AI Engineer": [
        "Python", "Statistics", "Linear Algebra", "Machine Learning",
        "Deep Learning", "PyTorch", "NLP", "LLM Engineering", "MLOps",
    ],
    "DevOps Engineer": [
        "Git", "Linux Fundamentals", "Python", "Docker", "Kubernetes",
        "CI/CD", "AWS", "System Design", "Monitoring & Observability",
    ],
}


def analyze_skill_gap(user_id, goal: str, db: Session) -> dict:
    required_names = GOAL_REQUIRED_SKILLS.get(goal, [])
    required_skills = (
        db.query(Skill).filter(Skill.name.in_(required_names)).all()
        if required_names
        else []
    )
    # preserve the canonical ordering from GOAL_REQUIRED_SKILLS
    order = {name: i for i, name in enumerate(required_names)}
    required_skills.sort(key=lambda s: order.get(s.name, 999))

    user_skills = {
        us.skill_id: us.proficiency
        for us in db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    }

    required_items = []
    have_skills, missing_skills = [], []
    for skill in required_skills:
        proficiency = user_skills.get(skill.id, 0)
        has_it = proficiency >= 40  # threshold for "has this skill"
        required_items.append(
            {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "status": "have" if has_it else "missing",
                "proficiency": proficiency,
            }
        )
        (have_skills if has_it else missing_skills).append(skill.name)

    return {
        "goal": goal,
        "required_skills": required_items,
        "have_skills": have_skills,
        "missing_skills": missing_skills,
    }
