from __future__ import annotations

import logging
from typing import Any, List, Optional

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

from providers.base import PlugProvider

logger = logging.getLogger(__name__)

# Zigbee2MQTT topic conventions:
#   Command:  zigbee2mqtt/<friendly_name>/set  {"state": "ON"/"OFF"}
#   State:    zigbee2mqtt/<friendly_name>       {"state": "ON"/"OFF", ...}


class MqttPlugProvider(PlugProvider):
    """Controls plugs/relays via MQTT (Zigbee2MQTT, Shelly, Tasmota, etc.)."""

    def __init__(self, hub) -> None:
        self._hub_model = hub
        self._host = hub.mqtt_host or "mosquitto"
        self._port = hub.mqtt_port or 1883
        self._auth = None
        if hub.mqtt_username:
            self._auth = {
                "username": hub.mqtt_username,
                "password": hub.mqtt_password_hash or "",
            }

    def _topic_set(self, plug_id: str) -> str:
        """Return the MQTT set-topic for a given plug_id (friendly name)."""
        return f"zigbee2mqtt/{plug_id}/set"

    def turn_on(self, plug_id: str) -> None:
        publish.single(
            topic=self._topic_set(plug_id),
            payload='{"state": "ON"}',
            hostname=self._host,
            port=self._port,
            auth=self._auth,
        )
        logger.info(f"MQTT plug {plug_id} turned ON")

    def turn_off(self, plug_id: str) -> None:
        publish.single(
            topic=self._topic_set(plug_id),
            payload='{"state": "OFF"}',
            hostname=self._host,
            port=self._port,
            auth=self._auth,
        )
        logger.info(f"MQTT plug {plug_id} turned OFF")

    def get_state(self, plug_id: str) -> Optional[bool]:
        """Subscribe to the state topic briefly to get current state.
        Note: For production use, consider maintaining a persistent MQTT connection
        and caching state instead of subscribing on each call.
        """
        result: list[Optional[bool]] = [None]

        def on_message(client, userdata, msg):
            import json  # noqa: PLC0415

            try:
                payload = json.loads(msg.payload)
                result[0] = str(payload.get("state", "")).upper() == "ON"
            except Exception:
                pass

        client = mqtt.Client()
        if self._auth:
            client.username_pw_set(self._auth["username"], self._auth["password"])
        client.on_message = on_message
        client.connect(self._host, self._port, 5)
        client.subscribe(f"zigbee2mqtt/{plug_id}", qos=0)
        client.loop_start()

        import time  # noqa: PLC0415

        time.sleep(1)
        client.loop_stop()
        client.disconnect()

        return result[0]

    def discover_plugs(self) -> List[dict[str, Any]]:
        """Subscribe to zigbee2mqtt/bridge/devices to get the device list."""
        devices: list[dict[str, Any]] = []

        def on_message(client, userdata, msg):
            import json  # noqa: PLC0415

            try:
                data = json.loads(msg.payload)
                for dev in data:
                    if dev.get("type") in ("Router", "EndDevice"):
                        devices.append(
                            {
                                "id": dev.get("friendly_name", ""),
                                "name": dev.get("friendly_name", ""),
                                "type": dev.get("definition", {}).get(
                                    "description", "Zigbee device"
                                ),
                                "ieee_address": dev.get("ieee_address", ""),
                            }
                        )
            except Exception:
                pass

        client = mqtt.Client()
        if self._auth:
            client.username_pw_set(self._auth["username"], self._auth["password"])
        client.on_message = on_message
        client.connect(self._host, self._port, 5)
        client.subscribe("zigbee2mqtt/bridge/devices", qos=0)
        client.loop_start()

        import time  # noqa: PLC0415

        time.sleep(2)
        client.loop_stop()
        client.disconnect()

        return devices

    def test_connection(self) -> bool:
        try:
            client = mqtt.Client()
            if self._auth:
                client.username_pw_set(self._auth["username"], self._auth["password"])
            client.connect(self._host, self._port, 5)
            client.disconnect()
            return True
        except Exception:
            return False
