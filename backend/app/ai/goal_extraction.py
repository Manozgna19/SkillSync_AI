"""
Extract a structured goal (career goal, current skills, experience level,
etc.) from a learner's free-text description.

Gemini does the natural-language understanding, but we NEVER trust its
output blindly: every field is validated and normalized against our own
skills table and a fixed set of known career goals before being used
anywhere else in the system (per architecture rule in the project spec).
"""
import re
from typing import Optional
from sqlalchemy.orm import Session

from app.ai import gemini_client
from app.models.skill import Skill

KNOWN_GOALS = [
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "DevOps Engineer",
]

SYSTEM_INSTRUCTION = """You are a goal-extraction engine for a personalized
learning platform.

Given a learner's free-text description of their career goal and background,
extract a structured JSON object with EXACTLY these keys:

{
  "goal": string,
  "experience_level": string,
  "current_skills": string[],
  "interests": string[],
  "weekly_hours": number
}

Rules:

1. Extract the learner's actual intended career goal.
2. Do NOT force the goal into a predefined list.
3. Preserve specific career names such as:
   Lawyer, Doctor, Cybersecurity Analyst, Product Manager,
   Financial Analyst, Architect, Teacher, etc.
4. Use a concise professional career title.
5. experience_level must be:
   "Beginner", "Intermediate", or "Advanced".
6. current_skills must contain only skills the learner explicitly
   says they already have.
7. weekly_hours defaults to 5 if not provided.

Only output the JSON object, nothing else."""


def _fallback_extraction(text: str) -> dict:
    """Deterministic fallback that preserves unknown career goals."""

    lower = text.lower().strip()

    experience_level = "Beginner"

    if "advanced" in lower or "expert" in lower or "senior" in lower:
        experience_level = "Advanced"
    elif "intermediate" in lower or "some experience" in lower:
        experience_level = "Intermediate"

    hours_match = re.search(r"(\d+)\s*hours?", lower)
    weekly_hours = int(hours_match.group(1)) if hours_match else 5

    # Try to extract the career after common phrases.
    patterns = [
        r"i want to become\s+(.+)",
        r"i want to be\s+(.+)",
        r"my goal is\s+(.+)",
        r"change my goal to\s+(.+)",
        r"switch my goal to\s+(.+)",
        r"i want a career in\s+(.+)",
        r"i want to pursue\s+(.+)",
    ]

    goal = None

    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            goal = match.group(1).strip()
            break

    if goal:
        goal = goal.rstrip(".!?").strip().title()
    else:
        goal = ""

    return {
        "goal": goal,
        "experience_level": experience_level,
        "current_skills": [],
        "interests": [],
        "weekly_hours": weekly_hours,
    }

def _normalize_goal(raw_goal: str) -> str:
    """
    Normalize a career goal without forcing unknown careers into
    an unrelated predefined goal.

    Known goals and common aliases are canonicalized.
    New career goals are preserved.
    """

    raw_goal = (raw_goal or "").strip()

    if not raw_goal:
        return ""

    raw_lower = raw_goal.lower()

    # Exact canonical goals
    for known in KNOWN_GOALS:
        if raw_lower == known.lower():
            return known

    # Common aliases
    aliases = {
        "ai engineering": "AI Engineer",
        "ai engineer": "AI Engineer",

        "machine learning engineering": "Machine Learning Engineer",
        "ml engineer": "Machine Learning Engineer",
        "ml engineering": "Machine Learning Engineer",

        "fullstack developer": "Full Stack Developer",
        "full stack engineering": "Full Stack Developer",

        "backend engineering": "Backend Developer",
        "backend developer": "Backend Developer",

        "frontend engineering": "Frontend Developer",
        "frontend developer": "Frontend Developer",

        "data science": "Data Scientist",
        "data scientist": "Data Scientist",

        "devops engineering": "DevOps Engineer",
        "devops engineer": "DevOps Engineer",
    }

    if raw_lower in aliases:
        return aliases[raw_lower]

    # Unknown career → preserve it.
    return raw_goal.title()

def _normalize_skills(raw_skills: list, db: Session) -> list:
    """Match free-text skill names against the canonical skills table."""
    if not raw_skills:
        return []
    all_skills = db.query(Skill.name).all()
    known_names = {s[0].lower(): s[0] for s in all_skills}
    normalized = []
    for skill in raw_skills:
        if not isinstance(skill, str):
            continue
        key = skill.strip().lower()
        if key in known_names:
            normalized.append(known_names[key])
        else:
            # partial match
            for k, v in known_names.items():
                if k in key or key in k:
                    normalized.append(v)
                    break
    return list(dict.fromkeys(normalized))  # dedupe, preserve order


def extract_goal(text: str, db: Session) -> dict:
    """
    Extract and validate a structured goal from free text.
    Returns a dict with: goal, experience_level, current_skills,
    interests, weekly_hours - all validated/normalized.
    """
    raw = gemini_client.generate_json(
        prompt=f"Learner's description:\n\"\"\"{text}\"\"\"",
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if raw is None:
        raw = _fallback_extraction(text)

    # ---- Validation & normalization (never trust the LLM blindly) ----
    goal = _normalize_goal(str(raw.get("goal", "")))

    experience_level = raw.get("experience_level", "Beginner")
    if experience_level not in ("Beginner", "Intermediate", "Advanced"):
        experience_level = "Beginner"

    current_skills = _normalize_skills(raw.get("current_skills", []) or [], db)

    interests = raw.get("interests", []) or []
    interests = [str(i)[:100] for i in interests if isinstance(i, (str,))][:10]

    weekly_hours = raw.get("weekly_hours", 5)
    try:
        weekly_hours = int(weekly_hours)
    except (TypeError, ValueError):
        weekly_hours = 5
    weekly_hours = max(1, min(weekly_hours, 80))

    return {
        "goal": goal,
        "experience_level": experience_level,
        "current_skills": current_skills,
        "interests": interests,
        "weekly_hours": weekly_hours,
    }
