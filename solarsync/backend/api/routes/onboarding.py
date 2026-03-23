from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.database import get_session
from models.models import OnboardingState

router = APIRouter()


@router.get("/status")
def get_onboarding_status(session: Session = Depends(get_session)):
    """Return the current onboarding state."""
    state = session.get(OnboardingState, 1)
    return state


@router.post("/complete-step")
def complete_step(
    step: int,
    session: Session = Depends(get_session),
):
    """Mark a specific onboarding step as complete and advance the state."""
    state = session.get(OnboardingState, 1)

    if step == 1:
        pass  # Welcome step — just advance
    elif step == 2:
        state.energy_source_configured = True
    elif step == 3:
        state.hub_configured = True
    elif step == 4:
        state.first_appliance_added = True

    # Advance the current step counter
    state.current_step = max(state.current_step, step + 1)

    # Mark onboarding complete when all steps are done
    if (
        state.energy_source_configured
        and state.hub_configured
        and state.first_appliance_added
    ):
        state.completed = True
        state.completed_at = datetime.utcnow()

    session.add(state)
    session.commit()
    session.refresh(state)
    return state


@router.post("/reset")
def reset_onboarding(session: Session = Depends(get_session)):
    """Reset onboarding back to step 1 (for re-configuration)."""
    state = session.get(OnboardingState, 1)
    state.completed = False
    state.current_step = 1
    state.energy_source_configured = False
    state.hub_configured = False
    state.first_appliance_added = False
    state.completed_at = None
    session.add(state)
    session.commit()
    session.refresh(state)
    return state
