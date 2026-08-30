"""
Conversational learning assistant.

Handles:
1. Normal learning questions using Gemini.
2. Explicit career-goal changes.
3. Learning requests for ANY topic, independent of the career goal.
4. Progress questions using deterministic logic.
"""

import re
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.ai import gemini_client
from app.ai.goal_extraction import extract_goal
from app.models.profile import LearnerProfile
from app.models.goal import Goal
from app.models.learning_path import LearningPath, LearningPathItem
from app.models.resource import Resource
from app.models.skill import Skill, UserSkill
from app.services import skill_gap_service
from app.services.learning_path_service import generate_learning_path


SYSTEM_INSTRUCTION = """You are a friendly and intelligent AI learning
assistant embedded in a personalized learning-path platform.

You help learners with:
- career goals
- learning topics
- skills
- prerequisites
- learning paths
- progress
- career-related questions

The learner may ask to learn ANY valid topic, technology, framework,
tool, language, academic subject, or professional skill.

IMPORTANT:
- A learning path is a recommendation, NOT a restriction.
- Never reject a learning request just because the topic is not
  currently in the learner's learning path.
- Do not tell the learner to change their career goal simply because
  they want to learn something outside their current career path.
- If a topic is relevant to the learner's goal, explain why.
- If it is unrelated, clearly say so but still help the learner.
- Do not invent learner progress, skills, or resources.
- Use only the learner context provided to you when discussing
  their current progress or learning path.

Be helpful, concise, accurate, and encouraging.
"""


# ============================================================
# BUILD LEARNER CONTEXT
# ============================================================

def _build_context(user_id, db: Session) -> str:
    """Build the learner's current goal, skills, gaps and path."""

    profile = (
        db.query(LearnerProfile)
        .filter(LearnerProfile.user_id == user_id)
        .first()
    )

    lines = []

    if profile:
        lines.append(
            f"Current career goal: "
            f"{profile.career_goal or 'not set'}"
        )

        lines.append(
            f"Experience level: "
            f"{profile.experience_level or 'Beginner'}"
        )

        lines.append(
            f"Weekly available hours: "
            f"{profile.weekly_hours or 5}"
        )

    # --------------------------------------------------------
    # Skill gaps
    # --------------------------------------------------------

    if profile and profile.career_goal:

        try:
            gap = skill_gap_service.analyze_skill_gap(
                user_id,
                profile.career_goal,
                db,
            )

            lines.append(
                "Current skills: "
                + (
                    ", ".join(gap.get("have_skills", []))
                    or "none recorded"
                )
            )

            lines.append(
                "Skill gaps: "
                + (
                    ", ".join(gap.get("missing_skills", []))
                    or "none"
                )
            )

        except Exception:
            lines.append("Skill-gap information unavailable.")

    # --------------------------------------------------------
    # Learning path
    # --------------------------------------------------------

    path = (
        db.query(LearningPath)
        .filter(
            LearningPath.user_id == user_id,
            LearningPath.is_active == True,  # noqa: E712
        )
        .first()
    )

    if not path:
        lines.append("Current learning path: none")
        return "\n".join(lines)

    try:

        items = (
            db.query(LearningPathItem, Resource)
            .join(
                Resource,
                Resource.id == LearningPathItem.resource_id,
            )
            .filter(
                LearningPathItem.learning_path_id == path.id
            )
            .order_by(LearningPathItem.phase_order)
            .all()
        )

        if items:
            lines.append("Current learning path:")

            for item, resource in items:

                status = getattr(
                    item,
                    "status",
                    "not_started",
                )

                percentage = getattr(
                    item,
                    "completion_percentage",
                    0,
                )

                lines.append(
                    f"  Phase {item.phase_order}: "
                    f"{resource.title} "
                    f"[{status}, {percentage}% done]"
                )

        else:
            lines.append("Current learning path: empty")

    except Exception:
        lines.append("Current learning path information unavailable.")

    return "\n".join(lines)


# ============================================================
# PROGRESS HANDLER
# ============================================================

def _handle_progress_question(context: str) -> Optional[str]:
    """Provide a simple deterministic progress response."""

    phases = re.findall(
        r"Phase\s+\d+:.*?\[(.*?)\]",
        context,
    )

    if not phases:
        return (
            "You don't have an active learning path yet. "
            "Generate one from your Goal page first."
        )

    total = len(phases)

    completed = sum(
        1
        for phase in phases
        if "completed" in phase.lower()
    )

    percentage = round(
        (completed / total) * 100
    ) if total else 0

    return (
        f"You've completed {completed} of {total} "
        f"learning phases ({percentage}% of the current path). "
        "Keep going!"
    )


# ============================================================
# CAREER GOAL CHANGE DETECTION
# ============================================================

def _is_goal_change_request(message: str) -> bool:
    """
    Detect explicit requests to change the learner's career goal.

    Examples:
        I want to become an AI Engineer
        I want to be a lawyer
        My goal is Data Scientist
        Change my goal to Cybersecurity Analyst
    """

    text = message.lower().strip()

    patterns = [
        r"\bi want to become\b",
        r"\bi want to be\b",
        r"\bmy goal is\b",
        r"\bchange my goal to\b",
        r"\bswitch my goal to\b",
        r"\bi want a career in\b",
        r"\bi want to pursue\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


# ============================================================
# LEARNING REQUEST DETECTION
# ============================================================

def _extract_learning_request(
    message: str,
) -> Optional[str]:
    """
    Detect requests to learn ANY topic.

    Examples:
        I want to learn Playwright
        I want to learn Kubernetes
        Teach me React
        I want to study Linear Algebra
        Help me learn Photoshop
        I would like to learn Python
    """

    patterns = [
        r"\bi want to learn\s+(.+)",
        r"\bi want to study\s+(.+)",
        r"\bteach me\s+(.+)",
        r"\bhelp me learn\s+(.+)",
        r"\bi'd like to learn\s+(.+)",
        r"\bi would like to learn\s+(.+)",
        r"\bi'd like to study\s+(.+)",
        r"\bi would like to study\s+(.+)",
    ]

    text = message.lower().strip()

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:

            topic = match.group(1).strip()

            topic = topic.rstrip(
                ".!?"
            ).strip()

            if topic:
                return topic

    return None


# ============================================================
# CAREER GOAL UPDATE
# ============================================================

def _change_goal(
    user_id,
    message: str,
    db: Session,
) -> Optional[str]:
    """
    Extract a new career goal, update the profile and generate
    a completely new personalized learning path.
    """

    extracted = extract_goal(
        message,
        db,
    )

    new_goal_name = extracted.get(
        "goal",
        "",
    ).strip()

    if not new_goal_name:
        return None

    profile = (
        db.query(LearnerProfile)
        .filter(
            LearnerProfile.user_id == user_id
        )
        .first()
    )

    if not profile:
        return None

    # --------------------------------------------------------
    # Deactivate old goals
    # --------------------------------------------------------

    db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.is_active == True,  # noqa: E712
    ).update(
        {
            "is_active": False
        }
    )

    # --------------------------------------------------------
    # Preserve learner information
    # --------------------------------------------------------

    experience_level = (
        profile.experience_level
        or extracted.get(
            "experience_level"
        )
        or "Beginner"
    )

    weekly_hours = (
        profile.weekly_hours
        or extracted.get(
            "weekly_hours"
        )
        or 5
    )

    # --------------------------------------------------------
    # Create new goal
    # --------------------------------------------------------

    new_goal = Goal(
        id=uuid.uuid4(),
        user_id=user_id,
        raw_text=message,
        normalized_goal=new_goal_name,
        experience_level=experience_level,
        extracted_current_skills=extracted.get(
            "current_skills",
            [],
        ),
        extracted_missing_skills=[],
        is_active=True,
    )

    db.add(new_goal)

    # --------------------------------------------------------
    # Update learner profile
    # --------------------------------------------------------

    profile.career_goal = new_goal_name
    profile.experience_level = experience_level
    profile.weekly_hours = weekly_hours

    # --------------------------------------------------------
    # Add detected skills
    # --------------------------------------------------------

    for skill_name in extracted.get(
        "current_skills",
        [],
    ):

        skill = (
            db.query(Skill)
            .filter(
                Skill.name == skill_name
            )
            .first()
        )

        if not skill:
            continue

        existing = (
            db.query(UserSkill)
            .filter(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill.id,
            )
            .first()
        )

        if not existing:

            db.add(
                UserSkill(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    skill_id=skill.id,
                    proficiency=60,
                    source="inferred",
                )
            )

    db.flush()

    # --------------------------------------------------------
    # Generate new personalized learning path
    # --------------------------------------------------------

    generate_learning_path(
        user_id=user_id,
        goal=new_goal_name,
        db=db,
        goal_id=new_goal.id,
        top_n=12,
    )

    return new_goal_name


# ============================================================
# GENERIC LEARNING REQUEST
# ============================================================

def _handle_learning_request(
    user_id,
    topic: str,
    db: Session,
) -> str:
    """
    Handle learning requests independently of the learner's
    career goal and current learning path.

    The learner is allowed to learn any topic.
    """

    context = _build_context(
        user_id,
        db,
    )

    prompt = f"""
The learner wants to learn:

{topic}

Here is the learner's current personalized context:

{context}

IMPORTANT RULES:

1. The learner can learn ANY valid topic.

2. Do NOT reject the topic just because it is not present
   in the current learning path.

3. Do NOT tell the learner to change their career goal
   simply because they want to learn this topic.

4. Explain briefly what the requested topic is.

5. Explain whether the topic is relevant to the learner's
   current career goal.

6. If relevant, explain how it helps the learner's career.

7. If unrelated, clearly explain that it is outside the
   core requirements of the current career goal, but still
   help the learner learn it.

8. Identify prerequisites when appropriate.

9. Give a practical learning approach.

10. If the topic is already present in the learning path,
    explain where it fits.

11. If the topic is NOT present in the learning path,
    do NOT treat that as an error.

12. Do not invent specific courses, resources, progress,
    or learner skills that are not present in the context.

13. Do not change the learner's career goal.

Answer naturally, helpfully, and concisely.
"""

    response = gemini_client.generate(
        prompt,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if response:
        return response.strip()

    return (
        f"{topic} can be learned independently of your "
        "current career goal. It is not required to be part "
        "of your current learning path."
    )


# ============================================================
# MAIN MESSAGE HANDLER
# ============================================================

def handle_message(
    user_id,
    message: str,
    db: Session,
) -> str:
    """
    Main entry point for the conversational assistant.

    Priority:

    1. Career goal change
    2. Learning request
    3. Progress question
    4. Normal Gemini conversation
    """

    message = (
        message or ""
    ).strip()

    if not message:
        return (
            "I'm here to help with your learning journey. "
            "Tell me what you'd like to learn or what career "
            "goal you're working toward."
        )

    # ========================================================
    # 1. CAREER GOAL CHANGE
    # ========================================================

    if _is_goal_change_request(
        message
    ):

        try:

            new_goal = _change_goal(
                user_id=user_id,
                message=message,
                db=db,
            )

            if new_goal:

                db.commit()

                # IMPORTANT:
                # Rebuild context AFTER the new goal and
                # learning path have been generated.

                context = _build_context(
                    user_id,
                    db,
                )

                prompt = f"""
The learner has changed their career goal to:

{new_goal}

Their updated personalized context is:

{context}

Their original message was:

{message}

Tell them clearly that their career goal has been updated
and that a new personalized learning path has been generated.

Briefly explain what the new path focuses on.

Do not mention internal implementation details.
"""

                response = gemini_client.generate(
                    prompt,
                    system_instruction=SYSTEM_INSTRUCTION,
                )

                if response:
                    return response.strip()

                return (
                    f"Great! I've updated your career goal "
                    f"to {new_goal} and generated a new "
                    "personalized learning path for you."
                )

            return (
                "I understood that you want to change your "
                "career goal, but I couldn't determine the "
                "new goal. Please try again with something "
                "like: 'I want to become a Data Scientist'."
            )

        except Exception:
            db.rollback()

            return (
                "I understood that you want to change your "
                "career goal, but I couldn't update the "
                "learning path right now. Please try again."
            )

    # ========================================================
    # 2. ANY LEARNING REQUEST
    # ========================================================

    learning_topic = _extract_learning_request(
        message
    )

    if learning_topic:

        return _handle_learning_request(
            user_id=user_id,
            topic=learning_topic,
            db=db,
        )

    # ========================================================
    # 3. PROGRESS QUESTIONS
    # ========================================================

    lower = message.lower()

    if (
        "how close" in lower
        or "how far" in lower
        or "progress" in lower
        or "how much have i completed" in lower
        or "what have i completed" in lower
    ):

        context = _build_context(
            user_id,
            db,
        )

        deterministic = _handle_progress_question(
            context
        )

        if deterministic:
            return deterministic

    # ========================================================
    # 4. NORMAL GEMINI CONVERSATION
    # ========================================================

    context = _build_context(
        user_id,
        db,
    )

    prompt = f"""
Learner context:

{context}

Learner's message:

{message}

Respond helpfully using the learner context.

Remember:

- The learning path is a recommendation, not a restriction.
- The learner can ask about any topic.
- Do not claim a topic is unavailable merely because it is
  absent from the current learning path.
- Do not change the learner's career goal unless they
  explicitly request a career-goal change.
- Do not invent learner progress or resources.
"""

    response = gemini_client.generate(
        prompt,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if response:
        return response.strip()

    # ========================================================
    # 5. FALLBACK
    # ========================================================

    return (
        "I couldn't reach the AI service right now, "
        "but I can still help you with your current "
        "learning goal and progress."
    )