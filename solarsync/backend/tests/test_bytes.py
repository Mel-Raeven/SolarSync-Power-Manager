"""Unit tests for ics2000/Bytes.py — pure byte-manipulation utilities."""

from __future__ import annotations

import pytest
from ics2000.Bytes import (
    MAX_UINT_16,
    _uint8,
    byte_to_int2,
    byte_to_int4,
    insertbytes,
    insertint16,
    insertint32,
)


class TestUint8:
    def test_zero(self):
        assert _uint8(0) == 0

    def test_max_byte(self):
        assert _uint8(255) == 255

    def test_overflow_masked(self):
        # 256 should wrap to 0
        assert _uint8(256) == 0

    def test_large_value_masked(self):
        assert _uint8(0x1FF) == 0xFF

    def test_negative_masked(self):
        # -1 in two's complement 8-bit = 0xFF
        assert _uint8(-1) == 0xFF


class TestInsertInt32:
    def test_zero(self):
        arr = bytearray(4)
        insertint32(arr, 0, 0)
        assert arr == bytearray([0, 0, 0, 0])

    def test_one(self):
        arr = bytearray(4)
        insertint32(arr, 1, 0)
        assert arr == bytearray([1, 0, 0, 0])

    def test_little_endian_multi_byte(self):
        arr = bytearray(4)
        insertint32(arr, 0x12345678, 0)
        assert arr == bytearray([0x78, 0x56, 0x34, 0x12])

    def test_offset(self):
        arr = bytearray(8)
        insertint32(arr, 0x01020304, 4)
        assert arr[:4] == bytearray([0, 0, 0, 0])
        assert arr[4:] == bytearray([0x04, 0x03, 0x02, 0x01])

    def test_max_uint32(self):
        arr = bytearray(4)
        insertint32(arr, 0xFFFFFFFF, 0)
        assert arr == bytearray([0xFF, 0xFF, 0xFF, 0xFF])


class TestInsertInt16:
    def test_zero(self):
        arr = bytearray(2)
        insertint16(arr, 0, 0)
        assert arr == bytearray([0, 0])

    def test_one(self):
        arr = bytearray(2)
        insertint16(arr, 1, 0)
        assert arr == bytearray([1, 0])

    def test_little_endian(self):
        arr = bytearray(2)
        insertint16(arr, 0xABCD, 0)
        assert arr == bytearray([0xCD, 0xAB])

    def test_offset(self):
        arr = bytearray(4)
        insertint16(arr, 0x0102, 2)
        assert arr[:2] == bytearray([0, 0])
        assert arr[2:] == bytearray([0x02, 0x01])


class TestInsertBytes:
    def test_simple(self):
        arr = bytearray(5)
        insertbytes(arr, b"\x01\x02\x03", 1)
        assert arr == bytearray([0, 1, 2, 3, 0])

    def test_at_zero(self):
        arr = bytearray(3)
        insertbytes(arr, b"\xaa\xbb\xcc", 0)
        assert arr == bytearray([0xAA, 0xBB, 0xCC])


class TestByteToInt2:
    def test_zero(self):
        assert byte_to_int2(0, 0) == 0

    def test_low_byte_only(self):
        assert byte_to_int2(0xFF, 0) == 0xFF

    def test_high_byte_only(self):
        assert byte_to_int2(0, 0xFF) == 0xFF00

    def test_both_bytes(self):
        # 0x34 | (0x12 << 8) = 0x1234
        assert byte_to_int2(0x34, 0x12) == 0x1234

    def test_max_value(self):
        assert byte_to_int2(0xFF, 0xFF) == MAX_UINT_16

    def test_masks_to_16_bits(self):
        # Even if we pass values > 255, the mask should constrain the result
        result = byte_to_int2(0x1FF, 0)
        assert result == 0xFF  # high bits of byte1 are masked


class TestByteToInt4:
    def test_zero(self):
        assert byte_to_int4(0, 0, 0, 0) == 0

    def test_low_byte(self):
        assert byte_to_int4(0x42, 0, 0, 0) == 0x42

    def test_result_truncated_to_16_bits(self):
        # The function assembles 4 bytes into a 32-bit int but then masks to 0xFFFF.
        # bytes [0x00, 0x00, 0xFF, 0xFF] → 0xFFFF0000 & 0xFFFF == 0
        result = byte_to_int4(0x00, 0x00, 0xFF, 0xFF)
        assert result == 0  # upper 16 bits are discarded

    def test_only_lower_16_bits_survive(self):
        # bytes [0xAB, 0xCD, 0x00, 0x00] → 0x0000CDAB & 0xFFFF == 0xCDAB
        result = byte_to_int4(0xAB, 0xCD, 0x00, 0x00)
        assert result == 0xCDAB
