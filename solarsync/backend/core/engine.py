from __future__ import annotations

import logging
from datetime import datetime, time
from typing import Optional

from sqlmodel import Session, select

from core.database import engine
from models.models import (
    Appliance,
    ApplianceStatus,
    EnergyProvider,
    EnergyProviderType,
    Hub,
    HubType,
    PowerEventType,
    PowerLog,
    ScheduleMode,
)

logger = logging.getLogger(__name__)


def run_solar_engine() -> None:
    """Main solar engine loop.

    1. Read current solar surplus from the configured energy provider(s)
    2. Get all enabled appliances sorted by priority
    3. Turn on appliances that fit within available surplus (respecting time windows)
    4. Turn off appliances that no longer fit
    5. Log all state changes to the power log
    """
    with Session(engine) as session:
        surplus = _get_solar_surplus(session)
        if surplus is None:
            logger.warning("Could not read solar surplus — skipping engine run")
            return

        logger.info(f"Solar surplus: {surplus}W")

        # Log this poll event
        session.add(
            PowerLog(
                event_type=PowerEventType.POLL,
                solar_surplus_watts=surplus,
            )
        )

        appliances = session.exec(
            select(Appliance)
            .where(Appliance.is_enabled == True)  # noqa: E712
            .order_by(Appliance.priority)
        ).all()

        now = datetime.utcnow().time()
        remaining_surplus = surplus

        for appliance in appliances:
            # Skip manually overridden appliances
            if appliance.status in (
                ApplianceStatus.OVERRIDE_ON,
                ApplianceStatus.OVERRIDE_OFF,
            ):
                if appliance.status == ApplianceStatus.OVERRIDE_ON:
                    remaining_surplus -= appliance.watt_draw
                continue

            # Skip manual-mode appliances (no auto management)
            if appliance.schedule_mode == ScheduleMode.MANUAL:
                continue

            # Check time window constraint
            if appliance.schedule_mode == ScheduleMode.TIME_WINDOW:
                if not _within_time_window(
                    now, appliance.time_window_start, appliance.time_window_end
                ):
                    if appliance.status == ApplianceStatus.RUNNING:
                        _turn_off_appliance(
                            session, appliance, surplus, "outside time window"
                        )
                    continue

            # Decide whether to turn on or off
            fits_in_surplus = appliance.watt_draw <= remaining_surplus

            if fits_in_surplus and appliance.status != ApplianceStatus.RUNNING:
                _turn_on_appliance(session, appliance, surplus)
                remaining_surplus -= appliance.watt_draw
            elif not fits_in_surplus and appliance.status == ApplianceStatus.RUNNING:
                _turn_off_appliance(session, appliance, surplus, "insufficient surplus")
            elif appliance.status == ApplianceStatus.RUNNING:
                remaining_surplus -= appliance.watt_draw

        session.commit()


def _get_solar_surplus(session: Session) -> Optional[int]:
    """Read solar surplus from the primary active energy provider."""
    provider = session.exec(
        select(EnergyProvider)
        .where(EnergyProvider.is_active == True)  # noqa: E712
        .where(EnergyProvider.is_primary == True)
    ).first()

    if provider is None:
        # Fall back to any active provider
        provider = session.exec(
            select(EnergyProvider).where(EnergyProvider.is_active == True)  # noqa: E712
        ).first()

    if provider is None:
        logger.warning("No active energy provider configured")
        return None

    try:
        if provider.provider_type == EnergyProviderType.KAKU_P1:
            from providers.energy.kaku_p1 import KaKuP1Provider  # noqa: PLC0415

            hub = session.get(Hub, provider.hub_id)
            if hub is None:
                logger.error("KaKu P1 provider has no associated hub")
                return None
            p = KaKuP1Provider(hub)
            return p.get_surplus_watts()

        elif provider.provider_type == EnergyProviderType.SOLAREDGE:
            from providers.energy.solaredge import SolarEdgeProvider  # noqa: PLC0415

            p = SolarEdgeProvider(
                api_key=provider.solaredge_api_key or "",
                site_id=provider.solaredge_site_id or "",
            )
            return p.get_surplus_watts()

    except Exception:
        logger.exception(f"Error reading from energy provider {provider.name}")
        return None

    return None


def _turn_on_appliance(session: Session, appliance: Appliance, surplus: int) -> None:
    """Send turn-on command to the appliance's plug and update status."""
    try:
        _send_plug_command(session, appliance, on=True)
        appliance.status = ApplianceStatus.RUNNING
        appliance.last_changed_at = datetime.utcnow()
        session.add(
            PowerLog(
                event_type=PowerEventType.TURNED_ON,
                solar_surplus_watts=surplus,
                appliance_id=appliance.id,
            )
        )
        logger.info(f"Turned ON: {appliance.name} ({appliance.watt_draw}W)")
    except Exception:
        logger.exception(f"Failed to turn on appliance: {appliance.name}")


def _turn_off_appliance(
    session: Session, appliance: Appliance, surplus: int, reason: str
) -> None:
    """Send turn-off command to the appliance's plug and update status."""
    try:
        _send_plug_command(session, appliance, on=False)
        appliance.status = ApplianceStatus.IDLE
        appliance.last_changed_at = datetime.utcnow()
        session.add(
            PowerLog(
                event_type=PowerEventType.TURNED_OFF,
                solar_surplus_watts=surplus,
                appliance_id=appliance.id,
                note=reason,
            )
        )
        logger.info(f"Turned OFF: {appliance.name} — {reason}")
    except Exception:
        logger.exception(f"Failed to turn off appliance: {appliance.name}")


def _send_plug_command(session: Session, appliance: Appliance, on: bool) -> None:
    """Dispatch plug on/off command to the correct provider."""
    if appliance.hub_id is None or appliance.plug_entity_id is None:
        raise ValueError(f"Appliance '{appliance.name}' has no hub or plug configured")

    hub = session.get(Hub, appliance.hub_id)
    if hub is None:
        raise ValueError(f"Hub {appliance.hub_id} not found")

    if hub.hub_type == HubType.KAKU_ICS2000:
        from providers.plugs.kaku import KaKuPlugProvider  # noqa: PLC0415

        provider = KaKuPlugProvider(hub)
        if on:
            provider.turn_on(appliance.plug_entity_id)
        else:
            provider.turn_off(appliance.plug_entity_id)

    elif hub.hub_type == HubType.MQTT:
        from providers.plugs.mqtt import MqttPlugProvider  # noqa: PLC0415

        provider = MqttPlugProvider(hub)
        if on:
            provider.turn_on(appliance.plug_entity_id)
        else:
            provider.turn_off(appliance.plug_entity_id)

    else:
        raise ValueError(f"Unsupported hub type: {hub.hub_type}")


def _within_time_window(
    now: time, start_str: Optional[str], end_str: Optional[str]
) -> bool:
    """Return True if the current time falls within the configured window."""
    if not start_str or not end_str:
        return True  # No window set — always allowed

    try:
        start = time.fromisoformat(start_str)
        end = time.fromisoformat(end_str)
    except ValueError:
        logger.warning(f"Invalid time window format: {start_str!r}–{end_str!r}")
        return True

    if start <= end:
        return start <= now <= end
    else:
        # Overnight window e.g. 22:00–06:00
        return now >= start or now <= end
