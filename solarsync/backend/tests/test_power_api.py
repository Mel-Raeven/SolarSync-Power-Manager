"""Integration tests for the power status + history API routes.

The /power/status endpoint calls _get_solar_surplus() which tries to
reach a real energy provider.  We mock that call so tests are isolated.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import Appliance, ApplianceStatus, PowerEventType, PowerLog


class TestPowerStatus:
    def test_status_with_no_provider(self, client: TestClient):
        """When no energy provider is configured, surplus should be None."""
        response = client.get("/power/status")
        assert response.status_code == 200
        data = response.json()
        assert data["solar_surplus_watts"] is None
        assert data["total_appliance_load_watts"] == 0
        assert data["running_appliances"] == []
        assert "last_updated" in data

    def test_status_running_appliances_included(
        self, client: TestClient, session: Session
    ):
        """Running appliances should be listed in the status response."""
        # Create a running appliance directly in the test DB
        a = Appliance(name="EV Charger", watt_draw=2200, status=ApplianceStatus.RUNNING)
        session.add(a)
        session.commit()

        with patch("api.routes.power._get_solar_surplus", return_value=3000):
            response = client.get("/power/status")

        assert response.status_code == 200
        data = response.json()
        assert data["total_appliance_load_watts"] == 2200
        assert len(data["running_appliances"]) == 1
        assert data["running_appliances"][0]["name"] == "EV Charger"

    def test_status_override_on_counted(self, client: TestClient, session: Session):
        """Appliances with OVERRIDE_ON status should be included in the load."""
        a = Appliance(
            name="Pool Pump", watt_draw=750, status=ApplianceStatus.OVERRIDE_ON
        )
        session.add(a)
        session.commit()

        with patch("api.routes.power._get_solar_surplus", return_value=1000):
            response = client.get("/power/status")

        assert response.json()["total_appliance_load_watts"] == 750


class TestPowerHistory:
    def test_empty_history(self, client: TestClient):
        response = client.get("/power/history")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_returns_recent_logs(self, client: TestClient, session: Session):
        log = PowerLog(event_type=PowerEventType.POLL, solar_surplus_watts=500)
        session.add(log)
        session.commit()

        response = client.get("/power/history?hours=24")
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) == 1
        assert logs[0]["event_type"] == "poll"
        assert logs[0]["solar_surplus_watts"] == 500

    def test_history_excludes_old_logs(self, client: TestClient, session: Session):
        old_ts = datetime.utcnow() - timedelta(hours=50)
        log = PowerLog(
            event_type=PowerEventType.POLL,
            solar_surplus_watts=100,
            timestamp=old_ts,
        )
        session.add(log)
        session.commit()

        response = client.get("/power/history?hours=24")
        assert response.json() == []

    def test_history_hours_parameter(self, client: TestClient, session: Session):
        recent = PowerLog(event_type=PowerEventType.POLL, solar_surplus_watts=200)
        old_ts = datetime.utcnow() - timedelta(hours=2)
        older = PowerLog(
            event_type=PowerEventType.POLL, solar_surplus_watts=100, timestamp=old_ts
        )
        session.add(recent)
        session.add(older)
        session.commit()

        # hours=1 should only return the most recent log
        logs = client.get("/power/history?hours=1").json()
        assert len(logs) == 1
        assert logs[0]["solar_surplus_watts"] == 200

    def test_history_hours_validation(self, client: TestClient):
        # hours must be between 1 and 168
        assert client.get("/power/history?hours=0").status_code == 422
        assert client.get("/power/history?hours=169").status_code == 422
        assert client.get("/power/history?hours=1").status_code == 200
        assert client.get("/power/history?hours=168").status_code == 200
