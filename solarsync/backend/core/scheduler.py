from __future__ import annotations

import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler() -> None:
    """Start the background scheduler that runs the solar engine loop."""
    interval = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
    _scheduler.add_job(
        _run_engine,
        trigger=IntervalTrigger(seconds=interval),
        id="solar_engine",
        name="Solar Engine Poll",
        replace_existing=True,
        next_run_time=datetime.utcnow(),  # Run immediately on startup
    )
    _scheduler.start()
    logger.info(f"Scheduler started — solar engine will run every {interval}s")


def stop_scheduler() -> None:
    """Gracefully stop the scheduler on application shutdown."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def _run_engine() -> None:
    """Wrapper called by the scheduler — imports engine here to avoid circular deps."""
    try:
        from core.engine import run_solar_engine  # noqa: PLC0415

        run_solar_engine()
    except Exception:
        logger.exception("Unhandled error in solar engine run")
