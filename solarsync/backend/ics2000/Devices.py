"""
ICS2000 Device classes.
Ported from original project.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ics2000.Core import Hub


class Device:
    """Represents a generic ICS2000 device (switch, plug, sensor, etc.)."""

    def __init__(self, name: str, entity_id: int, hub: "Hub") -> None:
        self._hub = hub
        self._name = name
        self._entity_id = entity_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def entity_id(self) -> int:
        return self._entity_id

    def turnon(self) -> None:
        self._hub.turnon(self._entity_id)

    def turnoff(self) -> None:
        self._hub.turnoff(self._entity_id)

    def getstatus(self) -> Optional[bool]:
        return self._hub.getlampstatus(self._entity_id)

    def __repr__(self) -> str:
        return f"Device(name={self._name!r}, entity_id={self._entity_id})"


class Dimmer(Device):
    """Represents a dimmable ICS2000 device."""

    def dim(self, level: int) -> None:
        if 0 <= level <= 15:
            self._hub.dim(self._entity_id, level)
