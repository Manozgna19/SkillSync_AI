from app.ai.goal_extraction import _normalize_goal, _fallback_extraction, KNOWN_GOALS


def test_normalize_goal_exact_match():
    assert _normalize_goal("Machine Learning Engineer") == "Machine Learning Engineer"


def test_normalize_goal_partial_text():
    result = _normalize_goal("I want to become a backend developer")
    assert result == "Backend Developer"


def test_normalize_goal_unknown_falls_back_to_best_overlap():
    result = _normalize_goal("something completely unrelated")
    assert result in KNOWN_GOALS


def test_fallback_extraction_detects_hours():
    result = _fallback_extraction("I have about 8 hours a week and know some Python")
    assert result["weekly_hours"] == 8


def test_fallback_extraction_detects_experience_level():
    result = _fallback_extraction("I'm an advanced developer wanting to specialize in ML")
    assert result["experience_level"] == "Advanced"


def test_fallback_extraction_default_beginner():
    result = _fallback_extraction("I want to become a data scientist")
    assert result["experience_level"] == "Beginner"
