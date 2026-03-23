"""Unit tests for core/engine.py — _within_time_window (pure logic)."""

from __future__ import annotations

from datetime import time

import pytest

from core.engine import _within_time_window


class TestWithinTimeWindow:
    # ── Normal (daytime) windows ─────────────────────────────────────────────

    def test_inside_normal_window(self):
        assert _within_time_window(time(12, 0), "09:00", "18:00") is True

    def test_exactly_at_start(self):
        assert _within_time_window(time(9, 0), "09:00", "18:00") is True

    def test_exactly_at_end(self):
        assert _within_time_window(time(18, 0), "09:00", "18:00") is True

    def test_before_window(self):
        assert _within_time_window(time(8, 59), "09:00", "18:00") is False

    def test_after_window(self):
        assert _within_time_window(time(18, 1), "09:00", "18:00") is False

    # ── Overnight windows ────────────────────────────────────────────────────

    def test_overnight_inside_after_midnight(self):
        # Window 22:00–06:00, check 03:00 → inside
        assert _within_time_window(time(3, 0), "22:00", "06:00") is True

    def test_overnight_inside_evening(self):
        # Window 22:00–06:00, check 23:30 → inside
        assert _within_time_window(time(23, 30), "22:00", "06:00") is True

    def test_overnight_exactly_at_start(self):
        assert _within_time_window(time(22, 0), "22:00", "06:00") is True

    def test_overnight_exactly_at_end(self):
        assert _within_time_window(time(6, 0), "22:00", "06:00") is True

    def test_overnight_outside_middle_of_day(self):
        # Window 22:00–06:00, check 12:00 → outside
        assert _within_time_window(time(12, 0), "22:00", "06:00") is False

    def test_overnight_just_before_start(self):
        assert _within_time_window(time(21, 59), "22:00", "06:00") is False

    def test_overnight_just_after_end(self):
        assert _within_time_window(time(6, 1), "22:00", "06:00") is False

    # ── Missing / invalid window strings → fail open ─────────────────────────

    def test_none_start_returns_true(self):
        assert _within_time_window(time(3, 0), None, "06:00") is True

    def test_none_end_returns_true(self):
        assert _within_time_window(time(3, 0), "22:00", None) is True

    def test_both_none_returns_true(self):
        assert _within_time_window(time(12, 0), None, None) is True

    def test_invalid_format_returns_true(self):
        # Bad format → logs a warning and returns True (fail open)
        assert _within_time_window(time(12, 0), "not-a-time", "18:00") is True

    def test_empty_string_returns_true(self):
        assert _within_time_window(time(12, 0), "", "") is True
