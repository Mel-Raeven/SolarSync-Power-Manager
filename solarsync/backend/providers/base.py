from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class EnergyProvider(ABC):
    """Abstract interface for solar/energy data sources.

    Implement this to add a new energy provider (SolarEdge, Shelly EM, etc.).
    """

    @abstractmethod
    def get_surplus_watts(self) -> Optional[int]:
        """Return the current solar surplus in watts.

        Positive = generating more than consuming (can turn on appliances).
        Negative = consuming more than generating (should turn off appliances).
        Returns None if the value cannot be read.
        """
        ...

    @abstractmethod
    def get_production_watts(self) -> Optional[int]:
        """Return current solar production in watts (panel output only)."""
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        """Return True if the provider is reachable and credentials are valid."""
        ...


class PlugProvider(ABC):
    """Abstract interface for smart plug / relay controllers.

    Implement this to add a new plug type (Shelly, Tasmota, MQTT, etc.).
    """

    @abstractmethod
    def turn_on(self, plug_id: str) -> None:
        """Turn on the plug identified by plug_id."""
        ...

    @abstractmethod
    def turn_off(self, plug_id: str) -> None:
        """Turn off the plug identified by plug_id."""
        ...

    @abstractmethod
    def get_state(self, plug_id: str) -> Optional[bool]:
        """Return True if on, False if off, None if unknown."""
        ...

    @abstractmethod
    def discover_plugs(self) -> List[dict[str, Any]]:
        """Return a list of available plugs on this hub.

        Each item should have at minimum:
            - id: str         provider-specific identifier
            - name: str       human-readable name
            - type: str       device type label
        """
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        """Return True if the hub is reachable and credentials are valid."""
        ...
