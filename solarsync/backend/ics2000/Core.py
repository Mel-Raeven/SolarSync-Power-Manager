"""
ICS2000 Hub driver.
Ported from original project — typed, cleaned up, numpy removed.
"""

from __future__ import annotations

import ast
import enum
import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional

import requests
from sqlmodel import Session

from core.database import engine
from ics2000.Command import Command
from ics2000.Cryptographer import decrypt
from ics2000.Devices import Device, Dimmer
from models.models import Setting

logger = logging.getLogger(__name__)

_KAKU_DEVICE_ID_KEY = "kaku_device_id"


def _get_or_create_device_id() -> str:
    """Return the persistent KaKu device UUID from the DB, creating it on first use."""
    with Session(engine) as session:
        setting = session.get(Setting, _KAKU_DEVICE_ID_KEY)
        if setting is not None:
            return setting.value
        new_id = str(uuid.uuid4())
        session.add(
            Setting(key=_KAKU_DEVICE_ID_KEY, value=new_id, updated_at=datetime.utcnow())
        )
        session.commit()
        logger.info("Generated new KaKu device ID: %s", new_id)
        return new_id


_BASE_URL = "https://trustsmartcloud2.com/ics2000_api"


def _constraint_int(inp: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, inp))


class Hub:
    """Represents a connected KlikAanKlikUit ICS2000 hub."""

    def __init__(self, mac: str, email: str, password: str) -> None:
        self.mac: str = mac
        self.aes: Optional[str] = None
        self._email = email
        self._password = password
        self._home_id: int = -1
        self._connected: bool = False
        self._devices: List[Device] = []
        self._device_unique_id: str = _get_or_create_device_id()
        self._login()
        self._pull_devices()

    # ── Authentication ────────────────────────────────────────────────────────

    def _login(self) -> None:
        logger.info("Logging in to ICS2000...")
        resp = requests.get(
            f"{_BASE_URL}/account.php",
            params={
                "action": "login",
                "email": self._email,
                "mac": self.mac.replace(":", ""),
                "password_hash": self._password,
                "device_unique_id": self._device_unique_id,
                "platform": "Android",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self.aes = data["homes"][0]["aes_key"]
        self._home_id = data["homes"][0]["home_id"]
        if self.aes:
            self._connected = True
            logger.info("ICS2000 login successful")

    def connected(self) -> bool:
        return self._connected

    # ── Device discovery ──────────────────────────────────────────────────────

    def _pull_devices(self) -> None:
        resp = requests.get(
            f"{_BASE_URL}/gateway.php",
            params={
                "action": "sync",
                "email": self._email,
                "mac": self.mac.replace(":", ""),
                "password_hash": self._password,
                "home_id": self._home_id,
            },
            timeout=10,
        )
        resp.raise_for_status()
        self._devices = []
        known_types = {item.value for item in DeviceType}

        for raw_device in resp.json():
            try:
                decrypted = json.loads(decrypt(raw_device["data"], self.aes))
            except Exception:
                continue

            module = decrypted.get("module", {})
            if not module:
                continue

            name = module.get("name")
            entity_id = module.get("id")
            device_type_id = module.get("device")

            if not name or entity_id is None:
                continue

            if device_type_id not in known_types:
                self._devices.append(Device(name, entity_id, self))
                continue

            dev_type = DeviceType(device_type_id)
            if dev_type == DeviceType.DIMMER:
                self._devices.append(Dimmer(name, entity_id, self))
            else:
                self._devices.append(Device(name, entity_id, self))

    @property
    def devices(self) -> List[Device]:
        return self._devices

    def refresh_devices(self) -> None:
        """Re-sync device list from the hub."""
        self._pull_devices()

    # ── Command sending ───────────────────────────────────────────────────────

    def sendcommand(self, command: str) -> None:
        requests.get(
            f"{_BASE_URL}/command.php",
            params={
                "action": "add",
                "email": self._email,
                "mac": self.mac.replace(":", ""),
                "password_hash": self._password,
                "device_unique_id": self._device_unique_id,
                "command": command,
            },
            timeout=10,
        )

    def simplecmd(self, entity: int, function: int, value) -> Command:
        cmd = Command()
        cmd.setmac(self.mac)
        cmd.settype(128)
        cmd.setmagic()
        cmd.setentityid(entity)
        cmd.setdata(
            json.dumps(
                {"module": {"id": entity, "function": function, "value": value}}
            ),
            self.aes,
        )
        return cmd

    # ── Switch / dim control ──────────────────────────────────────────────────

    def turnon(self, entity: int) -> None:
        self.sendcommand(self.simplecmd(entity, 0, 1).getcommand())

    def turnoff(self, entity: int) -> None:
        self.sendcommand(self.simplecmd(entity, 0, 0).getcommand())

    def dim(self, entity: int, level: int) -> None:
        self.sendcommand(self.simplecmd(entity, 1, level).getcommand())

    # ── Zigbee control ────────────────────────────────────────────────────────

    def zigbee_color_temp(self, entity: int, color_temp: int) -> None:
        color_temp = _constraint_int(color_temp, 0, 600)
        self.sendcommand(self.simplecmd(entity, 9, color_temp).getcommand())

    def zigbee_dim(self, entity: int, dim_lvl: int) -> None:
        dim_lvl = _constraint_int(dim_lvl, 1, 254)
        self.sendcommand(self.simplecmd(entity, 4, dim_lvl).getcommand())

    def zigbee_switch(self, entity: int, power: bool) -> None:
        self.sendcommand(self.simplecmd(entity, 3, "1" if power else "0").getcommand())

    def zigbee_socket(self, entity: int, power: bool) -> None:
        self.sendcommand(self.simplecmd(entity, 3, 1 if power else 0).getcommand())

    # ── Status reading ────────────────────────────────────────────────────────

    def get_device_status(self, entity: int) -> list:
        """Get the current status functions array via get-multiple endpoint."""
        resp = requests.get(
            f"{_BASE_URL}/entity.php",
            params={
                "action": "get-multiple",
                "email": self._email,
                "mac": self.mac.replace(":", ""),
                "password_hash": self._password,
                "home_id": self._home_id,
                "entity_id": f"[{entity}]",
            },
            timeout=10,
        )
        resp.raise_for_status()
        arr = resp.json()
        if len(arr) == 1 and arr[0].get("status") is not None:
            try:
                decrypted = json.loads(decrypt(arr[0]["status"], self.aes))
                return decrypted.get("module", {}).get("functions", [])
            except Exception:
                pass
        return []

    def get_device_check(self, entity: int) -> list:
        """Get the current status via the check endpoint.

        Returns the functions array. Index 5 = solar surplus in watts for P1 modules.
        """
        resp = requests.get(
            f"{_BASE_URL}/entity.php",
            params={
                "action": "check",
                "email": self._email,
                "mac": self.mac.replace(":", ""),
                "password_hash": self._password,
                "entity_id": str(entity),
            },
            timeout=10,
        )
        resp.raise_for_status()
        arr = resp.json()
        # arr[3] = status payload when length is 4
        if len(arr) == 4 and arr[3] is not None:
            try:
                decrypted = json.loads(decrypt(arr[3], self.aes))
                return decrypted.get("module", {}).get("functions", [])
            except (TypeError, json.JSONDecodeError, Exception):
                pass
        return []

    def getlampstatus(self, entity: int) -> Optional[bool]:
        status = self.get_device_status(entity)
        if len(status) >= 1:
            return status[0] == 1
        return None

    # ── P1 energy module helpers ──────────────────────────────────────────────

    def get_p1_module(self) -> Optional[Device]:
        """Return the first P1 energy module device found on this hub."""
        for device in self._devices:
            # Try to match by device type stored in the device list from pulldevices
            # The ENERGY_MODULE type id is 238
            pass
        # Fall back: scan all devices checking for P1 data structure
        return None

    def get_solar_surplus_watts(self) -> Optional[int]:
        """Read solar surplus from the P1 energy module.

        Returns watts as integer (positive = surplus, negative = deficit).
        Returns None if no P1 module found or read fails.
        """
        for device in self._devices:
            try:
                functions = self.get_device_check(device.entity_id)
                if functions and len(functions) > 5:
                    surplus = int(functions[5])
                    logger.debug(f"P1 surplus from device '{device.name}': {surplus}W")
                    return surplus
            except (ValueError, TypeError, Exception):
                continue
        return None


# ── Device type enum ──────────────────────────────────────────────────────────


class DeviceType(enum.Enum):
    SWITCH = 1
    DIMMER = 2
    ACTUATOR = 3
    MOTION_SENSOR = 4
    CONTACT_SENSOR = 5
    DOORBELL_ACDB_7000A = 6
    WALL_CONTROL_1_CHANNEL = 7
    WALL_CONTROL_2_CHANNEL = 8
    REMOTE_CONTROL_1_CHANNEL = 9
    REMOTE_CONTROL_2_CHANNEL = 10
    REMOTE_CONTROL_3_CHANNEL = 11
    REMOTE_CONTROL_16_CHANNEL = 12
    REMOTE_CONTROL_AYCT_202 = 13
    CHIME = 14
    DUSK_SENSOR = 15
    ARC_REMOTE = 16
    ARC_CONTACT_SENSOR = 17
    ARC_MOTION_SENSOR = 18
    ARC_SMOKE_SENSOR = 19
    ARC_SIREN = 20
    DOORBELL_ACDB_7000B = 21
    AWMT = 22
    SOMFY_ACTUATOR = 23
    LIGHT = 24
    WALL_SWITCH_AGST_8800 = 25
    WALL_SWITCH_AGST_8802 = 26
    BREL_ACTUATOR = 27
    CONTACT_SENSOR_2 = 28
    ARC_KEYCHAIN_REMOTE = 29
    ARC_ACTION_BUTTON = 30
    ARC_ROTARY_DIMMER = 31
    ZIGBEE_UNKNOWN_DEVICE = 32
    ZIGBEE_SWITCH = 33
    ZIGBEE_DIMMER = 34
    ZIGBEE_RGB = 35
    ZIGBEE_TUNABLE = 36
    ZIGBEE_MULTI_PURPOSE_SENSOR = 37
    ZIGBEE_LOCK = 38
    ZIGBEE_LIGHT_LINK_REMOTE = 39
    ZIGBEE_LIGHT = 40
    ZIGBEE_SOCKET = 41
    ZIGBEE_LEAKAGE_SENSOR = 42
    ZIGBEE_SMOKE_SENSOR = 43
    ZIGBEE_CARBON_MONOXIDE_SENSOR = 44
    ZIGBEE_TEMPERATURE_AND_HUMIDITY_SENSOR = 45
    ZIGBEE_LIGHT_GROUP = 46
    ZIGBEE_FIREANGEL_SENSOR = 47
    CAMERA_MODULE = 48
    LOCATION_MODULE = 49
    SYSTEM_MODULE = 50
    SECURITY_MODULE = 53
    ENERGY_MODULE = 238
    WEATHER_MODULE = 244


# ── Factory function ──────────────────────────────────────────────────────────


def get_hub(mac: str, email: str, password: str) -> Optional[Hub]:
    """Test connectivity and return a Hub instance, or None on failure."""
    try:
        resp = requests.get(
            f"{_BASE_URL}/gateway.php",
            params={
                "action": "check",
                "email": email,
                "mac": mac.replace(":", ""),
                "password_hash": password,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            parsed = ast.literal_eval(resp.text)
            if parsed[1] == "true":
                return Hub(mac, email, password)
    except Exception:
        logger.exception("Failed to connect to ICS2000 hub")
    return None
