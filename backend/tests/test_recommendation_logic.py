from app.services.skill_gap_service import (
    GOAL_REQUIRED_SKILLS,
)

from app.recommender.engine import (
    _difficulty_match_score,
)


def test_all_known_goals_have_required_skills():

    for goal, skills in GOAL_REQUIRED_SKILLS.items():

        assert isinstance(
            skills,
            list,
        )

        assert len(skills) > 0, (
            f"{goal} should have required skills defined"
        )


def test_difficulty_match_perfect():

    assert (
        _difficulty_match_score(
            "Beginner",
            "Beginner",
        )
        == 1.0
    )

    assert (
        _difficulty_match_score(
            "Advanced",
            "Advanced",
        )
        == 1.0
    )


def test_difficulty_match_one_level_off():

    assert (
        _difficulty_match_score(
            "Intermediate",
            "Beginner",
        )
        == 0.5
    )


def test_difficulty_match_two_levels_off():

    assert (
        _difficulty_match_score(
            "Advanced",
            "Beginner",
        )
        == 0.1
    )


def test_difficulty_match_invalid_input_returns_neutral():

    assert (
        _difficulty_match_score(
            "Unknown",
            "Beginner",
        )
        == 0.5
    )


def test_difficulty_match_is_symmetric():

    assert (
        _difficulty_match_score(
            "Beginner",
            "Intermediate",
        )
        == 0.5
    )

    assert (
        _difficulty_match_score(
            "Intermediate",
            "Beginner",
        )
        == 0.5
    )