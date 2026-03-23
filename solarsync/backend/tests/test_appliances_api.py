"""Integration tests for GET /health and the appliances API routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ── Health check ─────────────────────────────────────────────────────────────


class TestHealth:
    def test_health_ok(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "solarsync-backend"


# ── Appliances CRUD ───────────────────────────────────────────────────────────

_APPLIANCE_PAYLOAD = {
    "name": "Pool Pump",
    "watt_draw": 750,
    "schedule_mode": "solar_only",
    "priority": 3,
}


class TestListAppliances:
    def test_empty_list(self, client: TestClient):
        response = client.get("/appliances/")
        assert response.status_code == 200
        assert response.json() == []


class TestCreateAppliance:
    def test_create_returns_201(self, client: TestClient):
        response = client.post("/appliances/", json=_APPLIANCE_PAYLOAD)
        assert response.status_code == 201

    def test_create_body(self, client: TestClient):
        response = client.post("/appliances/", json=_APPLIANCE_PAYLOAD)
        data = response.json()
        assert data["name"] == "Pool Pump"
        assert data["watt_draw"] == 750
        assert data["schedule_mode"] == "solar_only"
        assert data["priority"] == 3
        assert data["status"] == "idle"
        assert "id" in data

    def test_create_default_status_idle(self, client: TestClient):
        response = client.post("/appliances/", json=_APPLIANCE_PAYLOAD)
        assert response.json()["status"] == "idle"

    def test_create_missing_required_field(self, client: TestClient):
        # watt_draw is required
        response = client.post("/appliances/", json={"name": "No watts"})
        assert response.status_code == 422

    def test_create_invalid_watt_draw(self, client: TestClient):
        payload = {**_APPLIANCE_PAYLOAD, "watt_draw": 0}
        response = client.post("/appliances/", json=payload)
        assert response.status_code == 422

    def test_create_invalid_schedule_mode(self, client: TestClient):
        payload = {**_APPLIANCE_PAYLOAD, "schedule_mode": "invalid_mode"}
        response = client.post("/appliances/", json=payload)
        assert response.status_code == 422


class TestGetAppliance:
    def test_get_existing(self, client: TestClient):
        created = client.post("/appliances/", json=_APPLIANCE_PAYLOAD).json()
        response = client.get(f"/appliances/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_missing_returns_404(self, client: TestClient):
        response = client.get("/appliances/9999")
        assert response.status_code == 404


class TestUpdateAppliance:
    def test_patch_name(self, client: TestClient):
        created = client.post("/appliances/", json=_APPLIANCE_PAYLOAD).json()
        response = client.patch(
            f"/appliances/{created['id']}", json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        # Other fields unchanged
        assert response.json()["watt_draw"] == 750

    def test_patch_missing_returns_404(self, client: TestClient):
        response = client.patch("/appliances/9999", json={"name": "x"})
        assert response.status_code == 404

    def test_patch_watt_draw(self, client: TestClient):
        created = client.post("/appliances/", json=_APPLIANCE_PAYLOAD).json()
        response = client.patch(
            f"/appliances/{created['id']}", json={"watt_draw": 1200}
        )
        assert response.json()["watt_draw"] == 1200


class TestDeleteAppliance:
    def test_delete_returns_204(self, client: TestClient):
        created = client.post("/appliances/", json=_APPLIANCE_PAYLOAD).json()
        response = client.delete(f"/appliances/{created['id']}")
        assert response.status_code == 204

    def test_delete_then_get_returns_404(self, client: TestClient):
        created = client.post("/appliances/", json=_APPLIANCE_PAYLOAD).json()
        client.delete(f"/appliances/{created['id']}")
        assert client.get(f"/appliances/{created['id']}").status_code == 404

    def test_delete_missing_returns_404(self, client: TestClient):
        response = client.delete("/appliances/9999")
        assert response.status_code == 404


class TestOverrideAppliance:
    def _create(self, client):
        return client.post("/appliances/", json=_APPLIANCE_PAYLOAD).json()

    def test_override_on(self, client: TestClient):
        a = self._create(client)
        response = client.post(f"/appliances/{a['id']}/override?action=on")
        assert response.status_code == 200
        assert response.json()["status"] == "override_on"

    def test_override_off(self, client: TestClient):
        a = self._create(client)
        response = client.post(f"/appliances/{a['id']}/override?action=off")
        assert response.status_code == 200
        assert response.json()["status"] == "override_off"

    def test_override_clear(self, client: TestClient):
        a = self._create(client)
        client.post(f"/appliances/{a['id']}/override?action=on")
        response = client.post(f"/appliances/{a['id']}/override?action=clear")
        assert response.json()["status"] == "idle"

    def test_override_invalid_action(self, client: TestClient):
        a = self._create(client)
        response = client.post(f"/appliances/{a['id']}/override?action=bad")
        assert response.status_code == 400

    def test_override_missing_appliance(self, client: TestClient):
        response = client.post("/appliances/9999/override?action=on")
        assert response.status_code == 404


class TestApplianceOrdering:
    def test_sorted_by_priority(self, client: TestClient):
        client.post(
            "/appliances/", json={**_APPLIANCE_PAYLOAD, "name": "Low", "priority": 9}
        )
        client.post(
            "/appliances/", json={**_APPLIANCE_PAYLOAD, "name": "High", "priority": 1}
        )
        client.post(
            "/appliances/", json={**_APPLIANCE_PAYLOAD, "name": "Mid", "priority": 5}
        )
        items = client.get("/appliances/").json()
        priorities = [a["priority"] for a in items]
        assert priorities == sorted(priorities)
