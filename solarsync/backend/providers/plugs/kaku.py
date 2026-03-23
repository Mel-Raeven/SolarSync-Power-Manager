from __future__ import annotations

import logging
from typing import Any, List, Optional

from providers.base import EnergyProvider, PlugProvider

logger = logging.getLogger(__name__)


def _make_ics_hub(hub_model):
    """Instantiate an ICS2000 Hub from a Hub DB model row."""
    from ics2000.Core import Hub  # noqa: PLC0415

    return Hub(
        mac=hub_model.mac_address,
        email=hub_model.email,
        password=hub_model.password_hash,  # stored hash used directly by ICS2000 API
    )


class KaKuP1Provider(EnergyProvider):
    """Reads solar surplus from a KlikAanKlikUit ICS2000 P1 energy module."""

    def __init__(self, hub) -> None:
        self._hub_model = hub
        self._ics_hub = None

    def _get_hub(self):
        if self._ics_hub is None:
            self._ics_hub = _make_ics_hub(self._hub_model)
        return self._ics_hub

    def get_surplus_watts(self) -> Optional[int]:
        try:
            from ics2000.Core import DeviceType  # noqa: PLC0415

            hub = self._get_hub()

            # Prefer the dedicated energy module device type
            p1_device = next(
                (
                    d
                    for d in hub.devices
                    if getattr(d, "device_type_id", None)
                    == DeviceType.ENERGY_MODULE.value
                ),
                None,
            )

            if p1_device is not None:
                status = hub.get_device_check(p1_device.entity_id)
                if status and len(status) > 5:
                    return int(status[5])

            # Fallback: scan all devices; the first one with a valid surplus at
            # functions[5] is assumed to be the P1 module.
            for device in hub.devices:
                try:
                    status = hub.get_device_check(device.entity_id)
                    if status and len(status) > 5:
                        surplus = int(status[5])
                        logger.debug(
                            "P1 surplus found via fallback scan on device "
                            f"'{device.name}': {surplus}W"
                        )
                        return surplus
                except Exception:
                    continue

            logger.warning("No P1 energy module found on ICS2000 hub")
            return None
        except Exception:
            logger.exception("Failed to read P1 surplus from ICS2000")
            return None

    def get_production_watts(self) -> Optional[int]:
        # The ICS2000 P1 module reports surplus (net), not raw solar production.
        # Raw production requires a separate solar inverter integration.
        return None

    def test_connection(self) -> bool:
        try:
            self._get_hub()
            return self._ics_hub is not None
        except Exception:
            return False


class KaKuPlugProvider(PlugProvider):
    """Controls KlikAanKlikUit smart plugs via the ICS2000 hub."""

    def __init__(self, hub) -> None:
        self._hub_model = hub
        self._ics_hub = None

    def _get_hub(self):
        if self._ics_hub is None:
            self._ics_hub = _make_ics_hub(self._hub_model)
        return self._ics_hub

    def turn_on(self, plug_id: str) -> None:
        hub = self._get_hub()
        hub.turnon(int(plug_id))
        logger.info(f"KaKu plug {plug_id} turned ON")

    def turn_off(self, plug_id: str) -> None:
        hub = self._get_hub()
        hub.turnoff(int(plug_id))
        logger.info(f"KaKu plug {plug_id} turned OFF")

    def get_state(self, plug_id: str) -> Optional[bool]:
        try:
            hub = self._get_hub()
            status = hub.get_device_status(int(plug_id))
            if status and len(status) > 0:
                return bool(status[0])
            return None
        except Exception:
            logger.exception(f"Failed to get state of KaKu plug {plug_id}")
            return None

    def discover_plugs(self) -> List[dict[str, Any]]:
        try:
            hub = self._get_hub()
            return [
                {
                    "id": str(device.entity_id),
                    "name": device.name,
                    "type": type(device).__name__,
                }
                for device in hub.devices
            ]
        except Exception:
            logger.exception("Failed to discover KaKu plugs")
            return []

    def test_connection(self) -> bool:
        try:
            self._get_hub()
            return self._ics_hub is not None
        except Exception:
            return False
