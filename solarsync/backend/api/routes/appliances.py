from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_session
from models.models import (
    Appliance,
    ApplianceCreate,
    ApplianceRead,
    ApplianceStatus,
    ApplianceUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[ApplianceRead])
def list_appliances(session: Session = Depends(get_session)):
    """Return all appliances sorted by priority."""
    return session.exec(select(Appliance).order_by(Appliance.priority)).all()


@router.post("/", response_model=ApplianceRead, status_code=201)
def create_appliance(
    appliance: ApplianceCreate, session: Session = Depends(get_session)
):
    db_appliance = Appliance.model_validate(appliance)
    session.add(db_appliance)
    session.commit()
    session.refresh(db_appliance)
    return db_appliance


@router.get("/{appliance_id}", response_model=ApplianceRead)
def get_appliance(appliance_id: int, session: Session = Depends(get_session)):
    appliance = session.get(Appliance, appliance_id)
    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")
    return appliance


@router.patch("/{appliance_id}", response_model=ApplianceRead)
def update_appliance(
    appliance_id: int,
    update: ApplianceUpdate,
    session: Session = Depends(get_session),
):
    appliance = session.get(Appliance, appliance_id)
    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(appliance, field, value)
    session.add(appliance)
    session.commit()
    session.refresh(appliance)
    return appliance


@router.delete("/{appliance_id}", status_code=204)
def delete_appliance(appliance_id: int, session: Session = Depends(get_session)):
    appliance = session.get(Appliance, appliance_id)
    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")
    session.delete(appliance)
    session.commit()


@router.post("/{appliance_id}/override")
def override_appliance(
    appliance_id: int,
    action: str,  # "on" | "off" | "clear"
    session: Session = Depends(get_session),
):
    """Manually override an appliance: force on, force off, or clear the override."""
    appliance = session.get(Appliance, appliance_id)
    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")

    if action == "on":
        appliance.status = ApplianceStatus.OVERRIDE_ON
    elif action == "off":
        appliance.status = ApplianceStatus.OVERRIDE_OFF
    elif action == "clear":
        appliance.status = ApplianceStatus.IDLE
    else:
        raise HTTPException(
            status_code=400, detail="action must be 'on', 'off', or 'clear'"
        )

    session.add(appliance)
    session.commit()
    session.refresh(appliance)
    return {"id": appliance.id, "status": appliance.status}
