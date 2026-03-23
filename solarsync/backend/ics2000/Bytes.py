"""
ICS2000 low-level byte utilities.
Ported from original project — numpy dependency replaced with pure Python
for better portability on arm64/Pi.
"""

from __future__ import annotations

MAX_UINT_16 = (2**16) - 1


def _uint8(n: int) -> int:
    return n & 0xFF


def insertint32(arr: bytearray, num: int, start: int) -> None:
    arr[start] = _uint8(num)
    arr[start + 1] = _uint8(num >> 8)
    arr[start + 2] = _uint8(num >> 16)
    arr[start + 3] = _uint8(num >> 24)


def insertint16(arr: bytearray, num: int, start: int) -> None:
    arr[start] = _uint8(num)
    arr[start + 1] = _uint8(num >> 8)


def insertbytes(arr: bytearray, inp: bytes, start: int) -> None:
    for i in range(len(inp)):
        arr[i + start] = inp[i]


def byte_to_int2(byte1: int, byte2: int) -> int:
    return (byte1 & 0xFF | (byte2 & 0xFF) << 8) & 0xFFFF


def byte_to_int4(byte1: int, byte2: int, byte3: int, byte4: int) -> int:
    return (
        byte1 & 0xFF | (byte2 & 0xFF) << 8 | (byte3 & 0xFF) << 16 | (byte4 & 0xFF) << 24
    ) & 0xFFFF
