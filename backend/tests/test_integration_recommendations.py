"""
Integration tests for the recommendation engine.

These tests require a reachable PostgreSQL database with pgvector
and seeded resources.

They are skipped automatically by the project's test configuration
when the database is unavailable.
"""

import uuid

import pytest

from app.models.user import User
from app.models.skill import (
    Skill,
    UserSkill,
)
from app.models.resource import (
    Resource,
    CompletedResource,
)
from app.core.security import hash_password

from app.recommender.engine import (
    generate_recommendations,
)

from app.services.skill_gap_service import (
    analyze_skill_gap,
)


@pytest.fixture
def test_user(db_session):

    user = User(
        id=uuid.uuid4(),
        name="Test Learner",
        email=(
            f"test-{uuid.uuid4()}@example.com"
        ),
        password_hash=hash_password(
            "TestPassword123"
        ),
    )

    db_session.add(user)
    db_session.commit()

    yield user

    db_session.delete(user)
    db_session.commit()


def test_skill_gap_analysis_returns_expected_shape(
    db_session,
    test_user,
):

    result = analyze_skill_gap(
        test_user.id,
        "Machine Learning Engineer",
        db_session,
    )

    assert (
        result["goal"]
        == "Machine Learning Engineer"
    )

    assert "missing_skills" in result

    assert "have_skills" in result

    assert isinstance(
        result["missing_skills"],
        list,
    )

    assert isinstance(
        result["have_skills"],
        list,
    )


def test_new_user_has_skill_gaps(
    db_session,
    test_user,
):

    result = analyze_skill_gap(
        test_user.id,
        "Machine Learning Engineer",
        db_session,
    )

    assert len(
        result["missing_skills"]
    ) > 0


def test_completed_resources_are_not_recommended(
    db_session,
    test_user,
):

    resources = (
        db_session
        .query(Resource)
        .limit(1)
        .all()
    )

    if not resources:

        pytest.skip(
            "No seed resources present. "
            "Run the seed script first."
        )

    resource = resources[0]

    completed = CompletedResource(
        id=uuid.uuid4(),
        user_id=test_user.id,
        resource_id=resource.id,
    )

    db_session.add(completed)
    db_session.commit()

    recommendations = generate_recommendations(
        test_user.id,
        "Full Stack Developer",
        db_session,
        top_n=50,
    )

    recommended_ids = {
        recommendation.resource.id
        for recommendation in recommendations
    }

    assert resource.id not in recommended_ids


def test_higher_proficiency_reduces_skill_gap(
    db_session,
    test_user,
):

    python_skill = (
        db_session
        .query(Skill)
        .filter(
            Skill.name == "Python"
        )
        .first()
    )

    if not python_skill:

        pytest.skip(
            "Python skill not found. "
            "Run the seed script first."
        )

    before = analyze_skill_gap(
        test_user.id,
        "Backend Developer",
        db_session,
    )

    assert (
        "Python"
        in before["missing_skills"]
    )

    user_skill = UserSkill(
        id=uuid.uuid4(),
        user_id=test_user.id,
        skill_id=python_skill.id,
        proficiency=80,
    )

    db_session.add(user_skill)
    db_session.commit()

    after = analyze_skill_gap(
        test_user.id,
        "Backend Developer",
        db_session,
    )

    assert (
        "Python"
        in after["have_skills"]
    )

    assert (
        "Python"
        not in after["missing_skills"]
    )


def test_recommendation_scores_are_valid(
    db_session,
    test_user,
):

    resources = (
        db_session
        .query(Resource)
        .limit(1)
        .all()
    )

    if not resources:

        pytest.skip(
            "No seed resources present."
        )

    recommendations = generate_recommendations(
        test_user.id,
        "Full Stack Developer",
        db_session,
        top_n=10,
    )

    for recommendation in recommendations:

        assert (
            0
            <= recommendation.score
            <= 100
        )

        assert recommendation.resource is not None

        assert isinstance(
            recommendation.reasons,
            list,
        )