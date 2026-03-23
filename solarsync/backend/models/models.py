from __future__ import annotations

import enum
from datetime import datetime, time
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# ── Enums ────────────────────────────────────────────────────────────────────


class ScheduleMode(str, enum.Enum):
    """How an appliance decides when to run."""

    SOLAR_ONLY = "solar_only"  # Only run when solar surplus covers it
    SOLAR_PREFERRED = "solar_preferred"  # Prefer solar, but allow grid if needed
    TIME_WINDOW = "time_window"  # Solar surplus + must be within a time window
    MANUAL = "manual"  # Fully manual — never auto-managed


class ApplianceStatus(str, enum.Enum):
    RUNNING = "running"
    IDLE = "idle"
    DISABLED = "disabled"
    OVERRIDE_ON = "override_on"  # Manual override — forced on
    OVERRIDE_OFF = "override_off"  # Manual override — forced off


class HubType(str, enum.Enum):
    KAKU_ICS2000 = "kaku_ics2000"
    MQTT = "mqtt"


class EnergyProviderType(str, enum.Enum):
    KAKU_P1 = "kaku_p1"
    SOLAREDGE = "solaredge"


class PowerEventType(str, enum.Enum):
    TURNED_ON = "turned_on"
    TURNED_OFF = "turned_off"
    OVERRIDE_ON = "override_on"
    OVERRIDE_OFF = "override_off"
    POLL = "poll"


# ── Hub ──────────────────────────────────────────────────────────────────────


class HubBase(SQLModel):
    name: str = Field(max_length=100)
    hub_type: HubType
    # KaKu ICS2000 fields
    mac_address: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    # Stored encrypted / hashed — never plaintext after setup
    password_hash: Optional[str] = Field(default=None, max_length=255)
    # MQTT fields
    mqtt_host: Optional[str] = Field(default=None, max_length=255)
    mqtt_port: Optional[int] = Field(default=1883)
    mqtt_username: Optional[str] = Field(default=None, max_length=255)
    mqtt_password_hash: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Hub(HubBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appliances: list["Appliance"] = Relationship(back_populates="hub")


class HubCreate(HubBase):
    password: Optional[str] = None  # Plaintext — only used at creation
    mqtt_password: Optional[str] = None


class HubRead(HubBase):
    id: int


# ── Energy Provider ──────────────────────────────────────────────────────────


class EnergyProviderBase(SQLModel):
    name: str = Field(max_length=100)
    provider_type: EnergyProviderType
    # SolarEdge fields
    solaredge_api_key: Optional[str] = Field(default=None, max_length=255)
    solaredge_site_id: Optional[str] = Field(default=None, max_length=100)
    # KaKu P1 — references a Hub
    hub_id: Optional[int] = Field(default=None, foreign_key="hub.id")
    is_active: bool = Field(default=True)
    is_primary: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EnergyProvider(EnergyProviderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EnergyProviderCreate(EnergyProviderBase):
    pass


class EnergyProviderRead(EnergyProviderBase):
    id: int


# ── Appliance ────────────────────────────────────────────────────────────────


class ApplianceBase(SQLModel):
    name: str = Field(max_length=100)
    icon: str = Field(default="mdi-power-plug", max_length=100)
    watt_draw: int = Field(ge=1, description="Expected power draw in watts")
    priority: int = Field(default=5, ge=1, le=10, description="1=highest, 10=lowest")
    schedule_mode: ScheduleMode = Field(default=ScheduleMode.SOLAR_ONLY)
    # Time window (only used when schedule_mode = TIME_WINDOW)
    time_window_start: Optional[str] = Field(
        default=None,
        description="HH:MM format, e.g. '09:00'",
        max_length=5,
    )
    time_window_end: Optional[str] = Field(
        default=None,
        description="HH:MM format, e.g. '18:00'",
        max_length=5,
    )
    # The smart plug this appliance is connected to
    plug_entity_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Provider-specific plug identifier (ICS2000 entity ID, MQTT topic, etc.)",
    )
    hub_id: Optional[int] = Field(default=None, foreign_key="hub.id")
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Appliance(ApplianceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: ApplianceStatus = Field(default=ApplianceStatus.IDLE)
    last_changed_at: Optional[datetime] = Field(default=None)
    hub: Optional[Hub] = Relationship(back_populates="appliances")
    power_logs: list["PowerLog"] = Relationship(back_populates="appliance")


class ApplianceCreate(ApplianceBase):
    pass


class ApplianceUpdate(SQLModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    watt_draw: Optional[int] = None
    priority: Optional[int] = None
    schedule_mode: Optional[ScheduleMode] = None
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    plug_entity_id: Optional[str] = None
    hub_id: Optional[int] = None
    is_enabled: Optional[bool] = None


class ApplianceRead(ApplianceBase):
    id: int
    status: ApplianceStatus
    last_changed_at: Optional[datetime]


# ── Power Log ────────────────────────────────────────────────────────────────


class PowerLogBase(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    event_type: PowerEventType
    solar_surplus_watts: Optional[int] = Field(default=None)
    solar_production_watts: Optional[int] = Field(default=None)
    grid_watts: Optional[int] = Field(default=None)
    appliance_id: Optional[int] = Field(default=None, foreign_key="appliance.id")
    note: Optional[str] = Field(default=None, max_length=500)


class PowerLog(PowerLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appliance: Optional[Appliance] = Relationship(back_populates="power_logs")


class PowerLogRead(PowerLogBase):
    id: int


# ── Setting ───────────────────────────────────────────────────────────────────


class Setting(SQLModel, table=True):
    """Key-value store for global app settings."""

    key: str = Field(primary_key=True, max_length=100)
    value: str = Field(max_length=1000)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Onboarding State ─────────────────────────────────────────────────────────


class OnboardingState(SQLModel, table=True):
    """Tracks how far through the onboarding wizard the user is."""

    id: Optional[int] = Field(default=None, primary_key=True)
    completed: bool = Field(default=False)
    current_step: int = Field(default=1)
    energy_source_configured: bool = Field(default=False)
    hub_configured: bool = Field(default=False)
    first_appliance_added: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
