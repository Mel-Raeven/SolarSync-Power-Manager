"""Integration tests for the settings API routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestGetSettings:
    def test_empty_returns_empty_dict(self, client: TestClient):
        response = client.get("/settings/")
        assert response.status_code == 200
        assert response.json() == {}


class TestUpdateSettings:
    def test_upsert_single_key(self, client: TestClient):
        response = client.put("/settings/", json={"poll_interval_seconds": "300"})
        assert response.status_code == 200
        assert response.json()["poll_interval_seconds"] == "300"

    def test_upsert_multiple_keys(self, client: TestClient):
        data = {"energy_source": "solaredge", "solaredge_site_id": "12345"}
        response = client.put("/settings/", json=data)
        assert response.status_code == 200
        body = response.json()
        assert body["energy_source"] == "solaredge"
        assert body["solaredge_site_id"] == "12345"

    def test_update_existing_key(self, client: TestClient):
        client.put("/settings/", json={"energy_source": "kaku_p1"})
        client.put("/settings/", json={"energy_source": "solaredge"})
        data = client.get("/settings/").json()
        assert data["energy_source"] == "solaredge"

    def test_settings_persisted_in_list(self, client: TestClient):
        client.put("/settings/", json={"energy_source": "solaredge"})
        response = client.get("/settings/")
        assert response.json()["energy_source"] == "solaredge"

    def test_rejects_unknown_key(self, client: TestClient):
        response = client.put("/settings/", json={"unknown_key": "value"})
        assert response.status_code == 400
        assert "unknown_key" in response.json()["detail"]


class TestGetSettingByKey:
    def test_existing_key(self, client: TestClient):
        client.put("/settings/", json={"solaredge_site_id": "my_site"})
        response = client.get("/settings/solaredge_site_id")
        assert response.status_code == 200
        assert response.json() == {"key": "solaredge_site_id", "value": "my_site"}

    def test_missing_key_returns_null_not_404(self, client: TestClient):
        response = client.get("/settings/poll_interval_seconds")
        assert response.status_code == 200
        assert response.json() == {"key": "poll_interval_seconds", "value": None}

    def test_invalid_key_returns_400(self, client: TestClient):
        response = client.get("/settings/nonexistent_key")
        assert response.status_code == 400
