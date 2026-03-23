from __future__ import annotations

import logging
from typing import Optional

import httpx

from providers.base import EnergyProvider

logger = logging.getLogger(__name__)

_SOLAREDGE_BASE = "https://monitoringapi.solaredge.com"


class SolarEdgeProvider(EnergyProvider):
    """Reads solar production data from the SolarEdge cloud monitoring API."""

    def __init__(self, api_key: str, site_id: str) -> None:
        self._api_key = api_key
        self._site_id = site_id

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{_SOLAREDGE_BASE}{path}"
        default_params = {"api_key": self._api_key}
        if params:
            default_params.update(params)
        with httpx.Client(timeout=10) as client:
            response = client.get(url, params=default_params)
            response.raise_for_status()
            return response.json()

    def get_production_watts(self) -> Optional[int]:
        """Return current solar panel production in watts."""
        try:
            data = self._get(f"/site/{self._site_id}/currentPowerFlow")
            # SolarEdge currentPowerFlow structure:
            # { siteCurrentPowerFlow: { PV: { currentPower: 1234.5 } } }
            flow = data.get("siteCurrentPowerFlow", {})
            pv = flow.get("PV", {})
            power = pv.get("currentPower")
            if power is not None:
                return int(float(power) * 1000)  # kW → W
            return None
        except Exception:
            logger.exception("Failed to read SolarEdge production")
            return None

    def get_surplus_watts(self) -> Optional[int]:
        """Return solar surplus = production - consumption.

        Uses the currentPowerFlow endpoint which gives a full site overview.
        """
        try:
            data = self._get(f"/site/{self._site_id}/currentPowerFlow")
            flow = data.get("siteCurrentPowerFlow", {})

            pv_kw = float(flow.get("PV", {}).get("currentPower", 0))
            load_kw = float(flow.get("LOAD", {}).get("currentPower", 0))
            grid_kw = float(flow.get("GRID", {}).get("currentPower", 0))

            # Surplus = PV production minus site consumption
            surplus_kw = pv_kw - load_kw
            return int(surplus_kw * 1000)  # kW → W
        except Exception:
            logger.exception("Failed to read SolarEdge surplus")
            return None

    def test_connection(self) -> bool:
        try:
            data = self._get(f"/site/{self._site_id}/details")
            return "details" in data
        except Exception:
            return False
