"""
Hybrid recommendation engine.

Recommendation Score =
    35% Goal Relevance        (cosine similarity of goal/skill-gap embedding vs resource embedding)
    25% Skill Gap Relevance   (does the resource teach a skill the learner is missing?)
    20% Prerequisite Match    (has the learner already satisfied this resource's prerequisites?)
    10% Difficulty Match      (does resource difficulty match learner's experience level?)
    10% Learner Preference    (interests / resource type alignment + past feedback)

We deliberately do NOT just return nearest-vector matches: pgvector cosine
similarity gives us a fast top-N candidate pool, and scikit-learn's
cosine_similarity plus explicit business rules refine the final ranking.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.embeddings.embedder import embed_text
from app.models.resource import Resource, ResourceSkill, ResourcePrerequisite, CompletedResource
from app.models.skill import UserSkill, Skill
from app.models.recommendation import RecommendationFeedback, Recommendation
from app.models.profile import LearnerProfile
from app.services import skill_gap_service

WEIGHTS = {
    "goal_relevance": 0.35,
    "skill_gap_relevance": 0.25,
    "prerequisite_match": 0.20,
    "difficulty_match": 0.10,
    "learner_preference": 0.10,
}

EXPERIENCE_TO_DIFFICULTY = {
    "Beginner": "Beginner",
    "Intermediate": "Intermediate",
    "Advanced": "Advanced",
}
DIFFICULTY_ORDER = ["Beginner", "Intermediate", "Advanced"]


@dataclass
class ScoredResource:
    resource: Resource
    score: float
    reasons: List[str] = field(default_factory=list)


def _candidate_pool(db: Session, query_embedding: List[float], limit: int = 40) -> List[Resource]:
    """Use pgvector cosine distance for fast ANN retrieval of candidates."""
    embedding_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"
    rows = db.execute(
        text(
            """
            SELECT id FROM resources
            ORDER BY embedding <=> CAST(:emb AS vector)
            LIMIT :limit
            """
        ),
        {"emb": embedding_literal, "limit": limit},
    ).fetchall()
    ids = [r[0] for r in rows]
    if not ids:
        return db.query(Resource).limit(limit).all()
    resources = db.query(Resource).filter(Resource.id.in_(ids)).all()
    order = {rid: i for i, rid in enumerate(ids)}
    resources.sort(key=lambda r: order.get(r.id, 999))
    return resources


def _difficulty_match_score(resource_difficulty: str, experience_level: str) -> float:
    try:
        r_idx = DIFFICULTY_ORDER.index(resource_difficulty)
        e_idx = DIFFICULTY_ORDER.index(experience_level)
    except ValueError:
        return 0.5
    distance = abs(r_idx - e_idx)
    if distance == 0:
        return 1.0
    if distance == 1:
        return 0.5
    return 0.1


def _get_feedback_penalty(db: Session, user_id, resource: Resource) -> float:
    """Reduce score for resource types the learner previously marked 'not_useful'."""
    feedbacks = (
        db.query(RecommendationFeedback.feedback)
        .join(Recommendation, Recommendation.id == RecommendationFeedback.recommendation_id)
        .join(Resource, Resource.id == Recommendation.resource_id)
        .filter(
            RecommendationFeedback.user_id == user_id,
            Resource.resource_type == resource.resource_type,
        )
        .all()
    )
    not_useful_count = sum(1 for f in feedbacks if f[0] == "not_useful")
    return max(0.0, 1.0 - 0.15 * not_useful_count)


def generate_recommendations(
    user_id, goal: str, db: Session, top_n: int = 10
) -> List[ScoredResource]:
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    experience_level = profile.experience_level if profile else "Beginner"
    interests = set((profile.interests or []) if profile else [])

    gap = skill_gap_service.analyze_skill_gap(user_id, goal, db)
    missing_skill_names = set(gap["missing_skills"])

    completed_ids = {
        c.resource_id
        for c in db.query(CompletedResource).filter(CompletedResource.user_id == user_id).all()
    }

    user_skill_ids = {
        us.skill_id
        for us in db.query(UserSkill).filter(
            UserSkill.user_id == user_id, UserSkill.proficiency >= 40
        ).all()
    }

    query_text = f"{goal}. Skills needed: {', '.join(missing_skill_names)}"
    query_embedding = embed_text(query_text)

    candidates = _candidate_pool(db, query_embedding, limit=60)
    candidates = [c for c in candidates if c.id not in completed_ids]
    if not candidates:
        return []

    candidate_embeddings = np.array([c.embedding for c in candidates])
    query_vec = np.array(query_embedding).reshape(1, -1)
    goal_similarities = cosine_similarity(query_vec, candidate_embeddings)[0]

    scored: List[ScoredResource] = []
    for resource, goal_sim in zip(candidates, goal_similarities):
        reasons = []

        # --- Goal relevance (0-1, from embeddings) ---
        goal_relevance = float(max(0.0, goal_sim))
        if goal_relevance > 0.5:
            reasons.append(f"Strongly related to your {goal} goal")

        # --- Skill gap relevance ---
        taught_skills = {
            rs.skill_id
            for rs in db.query(ResourceSkill).filter(ResourceSkill.resource_id == resource.id).all()
        }
        taught_skill_names = {
            s.name for s in db.query(Skill).filter(Skill.id.in_(taught_skills)).all()
        } if taught_skills else set()
        gap_overlap = taught_skill_names & missing_skill_names
        skill_gap_relevance = 1.0 if gap_overlap else 0.0
        if gap_overlap:
            reasons.append(f"Fills your skill gap in {', '.join(sorted(gap_overlap))}")

        # --- Prerequisite match ---
        prereq_skill_ids = {
            rp.prerequisite_skill_id
            for rp in db.query(ResourcePrerequisite)
            .filter(ResourcePrerequisite.resource_id == resource.id)
            .all()
        }
        if not prereq_skill_ids:
            prerequisite_match = 1.0
        else:
            satisfied = prereq_skill_ids & user_skill_ids
            prerequisite_match = len(satisfied) / len(prereq_skill_ids)
        if prerequisite_match >= 0.99 and prereq_skill_ids:
            reasons.append("You've already completed its prerequisites")
        elif prerequisite_match < 0.5 and prereq_skill_ids:
            reasons.append("Note: some prerequisites are still missing")

        # --- Difficulty match ---
        difficulty_match = _difficulty_match_score(resource.difficulty, experience_level)
        if difficulty_match == 1.0:
            reasons.append(f"Matches your {experience_level.lower()} level")

        # --- Learner preference (interests + resource-type feedback) ---
        preference_score = 0.5
        if interests and resource.description:
            desc_lower = resource.description.lower()
            if any(i.lower() in desc_lower for i in interests):
                preference_score = 1.0
                reasons.append("Aligned with your stated interests")
        preference_score *= _get_feedback_penalty(db, user_id, resource)

        total_score = (
            WEIGHTS["goal_relevance"] * goal_relevance
            + WEIGHTS["skill_gap_relevance"] * skill_gap_relevance
            + WEIGHTS["prerequisite_match"] * prerequisite_match
            + WEIGHTS["difficulty_match"] * difficulty_match
            + WEIGHTS["learner_preference"] * preference_score
        )

        if profile and profile.weekly_hours:
            reasons.append(f"Fits your available weekly study time ({profile.weekly_hours}h/week)")

        scored.append(ScoredResource(resource=resource, score=round(total_score * 100, 2), reasons=reasons))

    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:top_n]
