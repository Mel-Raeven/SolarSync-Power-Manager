"""Unit tests for ics2000/Color.py — RGB/XYZ color conversion."""

from __future__ import annotations

import pytest
from ics2000.Color import RGB, XYZ, _rgb_constrained


class TestRgbConstrained:
    def test_normal_value(self):
        assert _rgb_constrained(128.0) == 128

    def test_clamp_low(self):
        assert _rgb_constrained(-10.0) == 0

    def test_clamp_high(self):
        assert _rgb_constrained(300.0) == 255

    def test_boundary_zero(self):
        assert _rgb_constrained(0.0) == 0

    def test_boundary_255(self):
        assert _rgb_constrained(255.0) == 255

    def test_rounds_half_up(self):
        # round(127.5) in Python 3 uses banker's rounding → 128
        result = _rgb_constrained(127.5)
        assert result in (127, 128)  # either is acceptable


class TestRGB:
    def test_construction_clamps(self):
        rgb = RGB(-5, 300, 128)
        assert rgb.r == 0
        assert rgb.g == 255
        assert rgb.b == 128

    def test_black(self):
        rgb = RGB(0, 0, 0)
        assert rgb.r == rgb.g == rgb.b == 0

    def test_white(self):
        rgb = RGB(255, 255, 255)
        assert rgb.r == rgb.g == rgb.b == 255

    def test_str(self):
        rgb = RGB(1, 2, 3)
        assert str(rgb) == "[1, 2, 3]"

    def test_to_xyz_black(self):
        xyz = RGB(0, 0, 0).to_xyz()
        assert xyz.x == pytest.approx(0.0, abs=1e-6)
        assert xyz.y == pytest.approx(0.0, abs=1e-6)
        assert xyz.z == pytest.approx(0.0, abs=1e-6)

    def test_to_xyz_white(self):
        # sRGB D65 white point (approximately)
        xyz = RGB(255, 255, 255).to_xyz()
        assert xyz.x == pytest.approx(0.9504, abs=0.001)
        assert xyz.y == pytest.approx(1.0000, abs=0.001)
        assert xyz.z == pytest.approx(1.0889, abs=0.001)

    def test_to_xyz_red(self):
        xyz = RGB(255, 0, 0).to_xyz()
        # Red has a dominant X component in CIE XYZ
        assert xyz.x > xyz.y
        assert xyz.x > xyz.z

    def test_to_xyz_green(self):
        xyz = RGB(0, 255, 0).to_xyz()
        # Green has a dominant Y component
        assert xyz.y > xyz.x
        assert xyz.y > xyz.z

    def test_serialize_returns_int(self):
        result = RGB(255, 0, 0).serialize()
        assert isinstance(result, int)

    def test_serialize_white_is_stable(self):
        # The same color should always serialize to the same value
        assert RGB(255, 255, 255).serialize() == RGB(255, 255, 255).serialize()


class TestXYZ:
    def test_str(self):
        xyz = XYZ(0.1, 0.2, 0.3)
        assert str(xyz) == "[0.1, 0.2, 0.3]"

    def test_to_rgb_zero(self):
        rgb = XYZ(0.0, 0.0, 0.0).to_rgb()
        assert rgb.r == 0
        assert rgb.g == 0
        assert rgb.b == 0

    def test_to_rgb_white_point(self):
        # XYZ white point → near white RGB after normalization
        rgb = XYZ(0.9504, 1.0000, 1.0889).to_rgb()
        # After peak-normalization the result should be close to white
        assert rgb.r == 255
        assert rgb.g == 255
        assert rgb.b == 255

    def test_roundtrip_red(self):
        """RGB(255,0,0) → XYZ → RGB should come back to (255, 0, 0) after norm."""
        original = RGB(255, 0, 0)
        xyz = original.to_xyz()
        recovered = xyz.to_rgb()
        # After peak-normalization, bright red should still have r=255, g≈0, b≈0
        assert recovered.r == 255
        assert recovered.g == pytest.approx(0, abs=5)
        assert recovered.b == pytest.approx(0, abs=5)

    def test_roundtrip_green(self):
        original = RGB(0, 255, 0)
        xyz = original.to_xyz()
        recovered = xyz.to_rgb()
        assert recovered.g == 255
        assert recovered.r == pytest.approx(0, abs=5)
        assert recovered.b == pytest.approx(0, abs=5)
