from __future__ import annotations

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from core.database import get_session
from models.models import Setting

router = APIRouter()


@router.get("/")
def get_settings(session: Session = Depends(get_session)) -> Dict[str, str]:
    """Return all settings as a key-value dict."""
    settings = session.exec(select(Setting)).all()
    return {s.key: s.value for s in settings}


@router.put("/")
def update_settings(
    updates: Dict[str, str],
    session: Session = Depends(get_session),
) -> Dict[str, str]:
    """Upsert one or more settings keys."""
    for key, value in updates.items():
        existing = session.get(Setting, key)
        if existing:
            existing.value = value
            existing.updated_at = datetime.utcnow()
            session.add(existing)
        else:
            session.add(Setting(key=key, value=value))
    session.commit()
    return updates


@router.get("/{key}")
def get_setting(key: str, session: Session = Depends(get_session)):
    setting = session.get(Setting, key)
    if not setting:
        return {"key": key, "value": None}
    return {"key": setting.key, "value": setting.value}
