"""
Shared pytest fixtures for the SolarSync backend test suite.

Uses an in-memory SQLite database so tests never touch the real data file.
The scheduler is disabled during tests to avoid background threads.
"""

from __future__ import annotations

import os
import sys

# Ensure the backend package root is on sys.path when pytest is run from the
# tests/ subdirectory or from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# ---------------------------------------------------------------------------
# Patch the scheduler before any app code imports it so no background thread
# is started during the test session.
# ---------------------------------------------------------------------------
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def _disable_scheduler():
    """Prevent APScheduler from starting during tests."""
    with (
        patch("core.scheduler.start_scheduler"),
        patch("core.scheduler.stop_scheduler"),
    ):
        yield


# ---------------------------------------------------------------------------
# In-memory SQLite engine + session override
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite://"  # pure in-memory, no file


@pytest.fixture(name="session")
def session_fixture():
    """Yield a fresh in-memory SQLite session for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    # Seed the OnboardingState row (id=1) that the app expects
    from models.models import OnboardingState

    with Session(engine) as s:
        if not s.get(OnboardingState, 1):
            s.add(OnboardingState(id=1))
            s.commit()

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Return a FastAPI TestClient backed by the in-memory test session."""
    from main import app
    from core.database import get_session

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
