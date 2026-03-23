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
        response = client.put("/settings/", json={"poll_interval": "300"})
        assert response.status_code == 200
        assert response.json()["poll_interval"] == "300"

    def test_upsert_multiple_keys(self, client: TestClient):
        data = {"key_a": "value_a", "key_b": "value_b"}
        response = client.put("/settings/", json=data)
        assert response.status_code == 200
        body = response.json()
        assert body["key_a"] == "value_a"
        assert body["key_b"] == "value_b"

    def test_update_existing_key(self, client: TestClient):
        client.put("/settings/", json={"foo": "original"})
        client.put("/settings/", json={"foo": "updated"})
        data = client.get("/settings/").json()
        assert data["foo"] == "updated"

    def test_settings_persisted_in_list(self, client: TestClient):
        client.put("/settings/", json={"energy_source": "solaredge"})
        response = client.get("/settings/")
        assert response.json()["energy_source"] == "solaredge"


class TestGetSettingByKey:
    def test_existing_key(self, client: TestClient):
        client.put("/settings/", json={"my_key": "my_value"})
        response = client.get("/settings/my_key")
        assert response.status_code == 200
        assert response.json() == {"key": "my_key", "value": "my_value"}

    def test_missing_key_returns_null_not_404(self, client: TestClient):
        response = client.get("/settings/nonexistent_key")
        assert response.status_code == 200
        assert response.json() == {"key": "nonexistent_key", "value": None}
