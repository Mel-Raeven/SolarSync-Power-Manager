from __future__ import annotations

import os
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine

# ── Database path ─────────────────────────────────────────────────────────────
# Reads DB_DATABASE from environment, defaulting to /data/solarsync.sqlite
# Inside Docker this maps to a named volume; locally it writes to ./data/
_DB_PATH = os.getenv(
    "DB_DATABASE",
    str(Path(__file__).parent.parent.parent / "data" / "solarsync.sqlite"),
)
_DB_DIR = Path(_DB_PATH).parent
_DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{_DB_PATH}"

# SQLite pragmas for better performance and reliability on a Pi
_CONNECT_ARGS = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=_CONNECT_ARGS,
    echo=False,  # Set to True to log all SQL statements (debug only)
)


def create_db_and_tables() -> None:
    """Create all database tables if they don't exist.
    Called once at application startup.
    """
    SQLModel.metadata.create_all(engine)

    # Ensure the SQLite file is group/world-writable so the frontend container
    # (running as www-data) can also write to the shared volume.
    db_path = Path(_DB_PATH)
    if db_path.exists():
        db_path.chmod(0o666)

    # Ensure there is always exactly one OnboardingState row
    from models.models import OnboardingState  # noqa: PLC0415 (avoid circular at module level)

    with Session(engine) as session:
        existing = session.get(OnboardingState, 1)
        if existing is None:
            session.add(OnboardingState(id=1))
            session.commit()


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
