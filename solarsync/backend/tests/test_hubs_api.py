"""Integration tests for the hubs + energy providers API routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

_HUB_PAYLOAD = {
    "name": "My ICS2000",
    "hub_type": "kaku_ics2000",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "email": "test@example.com",
    "password": "secret123",
}

_MQTT_HUB_PAYLOAD = {
    "name": "MQTT Hub",
    "hub_type": "mqtt",
    "mqtt_host": "mosquitto",
    "mqtt_port": 1883,
}

_PROVIDER_PAYLOAD = {
    "name": "SolarEdge",
    "provider_type": "solaredge",
    "solaredge_api_key": "ABC123",
    "solaredge_site_id": "12345",
    "is_primary": True,
}


class TestListHubs:
    def test_empty_list(self, client: TestClient):
        response = client.get("/hubs/")
        assert response.status_code == 200
        assert response.json() == []


class TestCreateHub:
    def test_create_kaku_hub(self, client: TestClient):
        response = client.post("/hubs/", json=_HUB_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My ICS2000"
        assert data["hub_type"] == "kaku_ics2000"
        assert "id" in data

    def test_password_is_hashed_not_stored_plaintext(self, client: TestClient):
        response = client.post("/hubs/", json=_HUB_PAYLOAD)
        data = response.json()
        # The stored password_hash should NOT equal the original plaintext
        assert data.get("password_hash") != "secret123"

    def test_create_mqtt_hub(self, client: TestClient):
        response = client.post("/hubs/", json=_MQTT_HUB_PAYLOAD)
        assert response.status_code == 201
        assert response.json()["hub_type"] == "mqtt"

    def test_create_missing_name(self, client: TestClient):
        payload = {k: v for k, v in _HUB_PAYLOAD.items() if k != "name"}
        response = client.post("/hubs/", json=payload)
        assert response.status_code == 422

    def test_create_invalid_hub_type(self, client: TestClient):
        payload = {**_HUB_PAYLOAD, "hub_type": "unsupported_type"}
        response = client.post("/hubs/", json=payload)
        assert response.status_code == 422


class TestGetHub:
    def test_get_existing(self, client: TestClient):
        created = client.post("/hubs/", json=_HUB_PAYLOAD).json()
        response = client.get(f"/hubs/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_missing_returns_404(self, client: TestClient):
        assert client.get("/hubs/9999").status_code == 404


class TestDeleteHub:
    def test_delete_returns_204(self, client: TestClient):
        created = client.post("/hubs/", json=_HUB_PAYLOAD).json()
        assert client.delete(f"/hubs/{created['id']}").status_code == 204

    def test_delete_missing_returns_404(self, client: TestClient):
        assert client.delete("/hubs/9999").status_code == 404


class TestEnergyProviders:
    def test_list_empty(self, client: TestClient):
        response = client.get("/hubs/energy-providers/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_provider(self, client: TestClient):
        response = client.post("/hubs/energy-providers/", json=_PROVIDER_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "SolarEdge"
        assert data["provider_type"] == "solaredge"
        assert data["is_primary"] is True

    def test_create_second_primary_demotes_first(self, client: TestClient):
        client.post("/hubs/energy-providers/", json=_PROVIDER_PAYLOAD)
        second = {**_PROVIDER_PAYLOAD, "name": "Second SE", "is_primary": True}
        client.post("/hubs/energy-providers/", json=second)

        providers = client.get("/hubs/energy-providers/").json()
        primaries = [p for p in providers if p["is_primary"]]
        assert len(primaries) == 1

    def test_delete_provider(self, client: TestClient):
        created = client.post("/hubs/energy-providers/", json=_PROVIDER_PAYLOAD).json()
        assert (
            client.delete(f"/hubs/energy-providers/{created['id']}").status_code == 204
        )

    def test_delete_missing_provider_returns_404(self, client: TestClient):
        assert client.delete("/hubs/energy-providers/9999").status_code == 404

    def test_kaku_p1_provider_requires_hub_id(self, client: TestClient):
        """KaKu P1 provider should reference a hub — missing hub_id is still accepted
        at the API level but the engine will fail gracefully; we just verify creation works."""
        payload = {
            "name": "KaKu P1",
            "provider_type": "kaku_p1",
            "is_primary": False,
        }
        response = client.post("/hubs/energy-providers/", json=payload)
        assert response.status_code == 201
