from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.auth import verify_api_key
from core.database import create_db_and_tables
from core.scheduler import start_scheduler, stop_scheduler
from api.routes import appliances, hubs, power, settings, onboarding

logger = logging.getLogger(__name__)

# ── Application lifespan ──────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("SolarSync backend starting up...")
    create_db_and_tables()
    start_scheduler()
    yield
    logger.info("SolarSync backend shutting down...")
    stop_scheduler()


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="SolarSync API",
    description="Solar-powered appliance scheduler API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    dependencies=[Depends(verify_api_key)],
)

# ── CORS origins ─────────────────────────────────────────────────────────────
# Read from ALLOWED_ORIGINS env var (comma-separated). Defaults to localhost
# only. Set this to your actual hostname(s) in .env — wildcard "*" is rejected.
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost,https://localhost")
allowed_origins: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# CORS — Laravel frontend talks to this API via Nginx proxy at /api/*
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(appliances.router, prefix="/appliances", tags=["Appliances"])
app.include_router(hubs.router, prefix="/hubs", tags=["Hubs"])
app.include_router(power.router, prefix="/power", tags=["Power"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])


# ── Health check ──────────────────────────────────────────────────────────────


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "solarsync-backend"}
