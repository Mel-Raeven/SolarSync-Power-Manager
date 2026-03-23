from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_session
from models.models import (
    Hub,
    HubCreate,
    HubRead,
    EnergyProvider,
    EnergyProviderCreate,
    EnergyProviderRead,
)

router = APIRouter()


# ── Hubs ──────────────────────────────────────────────────────────────────────


@router.get("/", response_model=List[HubRead])
def list_hubs(session: Session = Depends(get_session)):
    return session.exec(select(Hub)).all()


@router.post("/", response_model=HubRead, status_code=201)
def create_hub(hub: HubCreate, session: Session = Depends(get_session)):
    from core.security import hash_password  # noqa: PLC0415

    db_hub = Hub.model_validate(
        hub,
        update={
            "password_hash": hash_password(hub.password) if hub.password else None,
            "mqtt_password_hash": hash_password(hub.mqtt_password)
            if hub.mqtt_password
            else None,
        },
    )
    session.add(db_hub)
    session.commit()
    session.refresh(db_hub)
    return db_hub


@router.get("/{hub_id}", response_model=HubRead)
def get_hub(hub_id: int, session: Session = Depends(get_session)):
    hub = session.get(Hub, hub_id)
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    return hub


@router.delete("/{hub_id}", status_code=204)
def delete_hub(hub_id: int, session: Session = Depends(get_session)):
    hub = session.get(Hub, hub_id)
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    session.delete(hub)
    session.commit()


@router.get("/{hub_id}/discover-plugs")
def discover_plugs(hub_id: int, session: Session = Depends(get_session)):
    """Discover smart plugs available on this hub."""
    hub = session.get(Hub, hub_id)
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")

    from models.models import HubType  # noqa: PLC0415

    if hub.hub_type == HubType.KAKU_ICS2000:
        from providers.plugs.kaku import KaKuPlugProvider  # noqa: PLC0415

        provider = KaKuPlugProvider(hub)
        return {"plugs": provider.discover_plugs()}

    raise HTTPException(
        status_code=400,
        detail=f"Plug discovery not supported for hub type: {hub.hub_type}",
    )


# ── Energy Providers ──────────────────────────────────────────────────────────


@router.get("/energy-providers/", response_model=List[EnergyProviderRead])
def list_energy_providers(session: Session = Depends(get_session)):
    return session.exec(select(EnergyProvider)).all()


@router.post("/energy-providers/", response_model=EnergyProviderRead, status_code=201)
def create_energy_provider(
    provider: EnergyProviderCreate, session: Session = Depends(get_session)
):
    db_provider = EnergyProvider.model_validate(provider)
    # If this is marked primary, unset primary on all others
    if db_provider.is_primary:
        existing = session.exec(
            select(EnergyProvider).where(EnergyProvider.is_primary == True)
        ).all()  # noqa: E712
        for ep in existing:
            ep.is_primary = False
            session.add(ep)
    session.add(db_provider)
    session.commit()
    session.refresh(db_provider)
    return db_provider


@router.delete("/energy-providers/{provider_id}", status_code=204)
def delete_energy_provider(provider_id: int, session: Session = Depends(get_session)):
    provider = session.get(EnergyProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Energy provider not found")
    session.delete(provider)
    session.commit()
