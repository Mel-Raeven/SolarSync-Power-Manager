"""
ICS2000 color deserialization utility.
Ported from original project.
"""

from __future__ import annotations

from ics2000.Bytes import MAX_UINT_16, byte_to_int2, insertint32
from ics2000.Color import XYZ


def deserialize_yxy_to_rgb(f: int):
    """Unpack a uint32 Yxy value from ICS2000 back into an RGB color object."""
    arr = bytearray(4)
    insertint32(arr, f, 0)
    x = byte_to_int2(arr[2], arr[3]) / MAX_UINT_16
    y = byte_to_int2(arr[0], arr[1]) / MAX_UINT_16

    y2 = 1.0
    xyz = XYZ((x * y2) / y, y2, (1.0 - x - y) * (y2 / y))
    return xyz.to_rgb()
