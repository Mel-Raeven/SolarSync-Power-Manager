"""Integration tests for the onboarding API routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestGetOnboardingStatus:
    def test_initial_state(self, client: TestClient):
        response = client.get("/onboarding/status")
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False
        assert data["current_step"] == 1
        assert data["energy_source_configured"] is False
        assert data["hub_configured"] is False
        assert data["first_appliance_added"] is False


class TestCompleteStep:
    def test_complete_step_1_advances(self, client: TestClient):
        response = client.post("/onboarding/complete-step?step=1")
        assert response.status_code == 200
        data = response.json()
        assert data["current_step"] == 2
        assert data["completed"] is False

    def test_complete_step_2_sets_energy_configured(self, client: TestClient):
        client.post("/onboarding/complete-step?step=2")
        data = client.get("/onboarding/status").json()
        assert data["energy_source_configured"] is True
        assert data["current_step"] == 3

    def test_complete_step_3_sets_hub_configured(self, client: TestClient):
        client.post("/onboarding/complete-step?step=3")
        data = client.get("/onboarding/status").json()
        assert data["hub_configured"] is True

    def test_complete_step_4_sets_appliance_added(self, client: TestClient):
        client.post("/onboarding/complete-step?step=4")
        data = client.get("/onboarding/status").json()
        assert data["first_appliance_added"] is True

    def test_all_steps_marks_completed(self, client: TestClient):
        client.post("/onboarding/complete-step?step=2")
        client.post("/onboarding/complete-step?step=3")
        client.post("/onboarding/complete-step?step=4")
        data = client.get("/onboarding/status").json()
        assert data["completed"] is True
        assert data["completed_at"] is not None

    def test_step_counter_is_monotonic(self, client: TestClient):
        """Completing the same step twice should not decrement current_step."""
        client.post("/onboarding/complete-step?step=3")
        client.post(
            "/onboarding/complete-step?step=1"
        )  # lower step — shouldn't go back
        data = client.get("/onboarding/status").json()
        assert data["current_step"] >= 4  # still past step 3


class TestResetOnboarding:
    def test_reset_clears_state(self, client: TestClient):
        client.post("/onboarding/complete-step?step=2")
        client.post("/onboarding/complete-step?step=3")
        client.post("/onboarding/complete-step?step=4")

        client.post("/onboarding/reset")
        data = client.get("/onboarding/status").json()

        assert data["completed"] is False
        assert data["current_step"] == 1
        assert data["energy_source_configured"] is False
        assert data["hub_configured"] is False
        assert data["first_appliance_added"] is False
        assert data["completed_at"] is None
