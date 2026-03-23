from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, desc

from core.database import get_session
from core.engine import _get_solar_surplus
from models.models import Appliance, ApplianceStatus, PowerLog, PowerLogRead

router = APIRouter()


@router.get("/status")
def get_power_status(session: Session = Depends(get_session)):
    """Return the current live power state: surplus, running appliances, total load."""
    surplus = _get_solar_surplus(session)

    running = session.exec(
        select(Appliance).where(
            Appliance.status.in_([ApplianceStatus.RUNNING, ApplianceStatus.OVERRIDE_ON])
        )
    ).all()

    total_load = sum(a.watt_draw for a in running)

    return {
        "solar_surplus_watts": surplus,
        "total_appliance_load_watts": total_load,
        "running_appliances": [
            {"id": a.id, "name": a.name, "watt_draw": a.watt_draw, "status": a.status}
            for a in running
        ],
        "last_updated": datetime.utcnow().isoformat(),
    }


@router.get("/history", response_model=List[PowerLogRead])
def get_power_history(
    hours: int = Query(default=24, ge=1, le=168),
    session: Session = Depends(get_session),
):
    """Return power log entries for the last N hours (default 24, max 168 = 1 week)."""
    since = datetime.utcnow() - timedelta(hours=hours)
    logs = session.exec(
        select(PowerLog)
        .where(PowerLog.timestamp >= since)
        .order_by(desc(PowerLog.timestamp))
        .limit(1000)
    ).all()
    return logs
