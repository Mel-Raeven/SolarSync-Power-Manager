"""
ICS2000 RGB/XYZ color conversion for Zigbee light control.
Ported from original project.
"""

from __future__ import annotations

from ics2000.Bytes import MAX_UINT_16, byte_to_int4, insertint16


def _rgb_constrained(inp: float) -> int:
    if inp < 0:
        return 0
    elif inp > 255:
        return 255
    else:
        return round(inp)


class RGB:
    def __init__(self, r: float, g: float, b: float) -> None:
        self.r = _rgb_constrained(r)
        self.g = _rgb_constrained(g)
        self.b = _rgb_constrained(b)

    def to_xyz(self) -> "XYZ":
        lower = 0.04045
        div = 12.92
        f5, f6, f7 = 0.055, 1.055, 2.4

        def linearize(c: float) -> float:
            v = c / 255
            if v < lower:
                return v / div
            return pow((v + f5) / f6, f7)

        r = linearize(self.r)
        g = linearize(self.g)
        b = linearize(self.b)

        return XYZ(
            0.4124564 * r + 0.3575761 * g + 0.1804375 * b,
            0.2126729 * r + 0.7151522 * g + 0.0721750 * b,
            r * 0.0193339 + g * 0.1191920 + b * 0.9503041,
        )

    def serialize(self) -> int:
        xyz = self.to_xyz()
        total = xyz.x + 1 + xyz.z
        x = xyz.x / total
        y = 1 / total
        f1 = int(x * MAX_UINT_16)
        f2 = int(y * MAX_UINT_16)
        arr = bytearray(4)
        insertint16(arr, f1 * 100, 0)
        insertint16(arr, f2 * 100, 2)
        return byte_to_int4(arr[2], arr[3], arr[0], arr[1])

    def __str__(self) -> str:
        return str([self.r, self.g, self.b])


class XYZ:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def to_rgb(self) -> RGB:
        limit = 0.0031308
        f6, f7, f8, mul = 0.42, 1.055, 0.055, 12.92

        f1 = 3.2404542 * self.x - 1.5371385 * self.y - 0.4985314 * self.z
        f2 = -0.9692660 * self.x + 1.8760108 * self.y + 0.0415560 * self.z
        f3 = 0.0556434 * self.x - 0.2040259 * self.y + 1.0572252 * self.z

        def gamma(c: float) -> float:
            if c > limit:
                return pow(c, f6) * f7 - f8
            return c * mul

        f1, f2, f3 = gamma(f1), gamma(f2), gamma(f3)

        peak = max(f1, f2, f3)
        if peak > 0:
            f1, f2, f3 = f1 / peak, f2 / peak, f3 / peak

        return RGB(
            _rgb_constrained(f1 * 255),
            _rgb_constrained(f2 * 255),
            _rgb_constrained(f3 * 255),
        )

    def __str__(self) -> str:
        return str([self.x, self.y, self.z])
