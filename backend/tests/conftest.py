"""
Shared pytest fixtures.

These tests focus on the deterministic business logic (skill gap analysis,
recommendation scoring rules, goal normalization) that must be correct
regardless of the LLM. Tests that need a real Postgres+pgvector database
are marked and skipped automatically if DATABASE_URL isn't reachable, so
`pytest` still runs cleanly without Docker for pure-logic checks.
"""
import os
import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, engine


def _db_available() -> bool:
    try:
        with engine.connect():
            return True
    except Exception:
        return False


DB_AVAILABLE = _db_available()


@pytest.fixture(scope="session")
def db_session():
    if not DB_AVAILABLE:
        pytest.skip("Postgres not reachable - skipping DB-dependent tests")
    import app.models  # noqa: F401 register models

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
