"""Unit tests for ics2000/Cryptographer.py — AES-CBC encrypt/decrypt."""

from __future__ import annotations

import base64

import pytest

from ics2000.Cryptographer import _pad, decrypt, encrypt

# A 16-byte (128-bit) AES key expressed as a hex string
AES_KEY_128 = "00112233445566778899aabbccddeeff"
# A 32-byte (256-bit) AES key
AES_KEY_256 = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"


class TestPad:
    def test_short_string_padded_to_block(self):
        # "hello" = 5 chars → needs 11 bytes of padding to reach 16
        result = _pad("hello")
        assert len(result) == 16
        assert result[-1] == chr(11)

    def test_exact_block_size_adds_full_block(self):
        # 16-char string → pad adds 16 more bytes (PKCS#7 rule)
        s = "a" * 16
        result = _pad(s)
        assert len(result) == 32
        assert result[-1] == chr(16)

    def test_empty_string_padded(self):
        result = _pad("")
        assert len(result) == 16
        assert result[-1] == chr(16)


class TestEncryptDecrypt:
    def test_roundtrip_simple(self):
        plaintext = "hello world"
        ciphertext = encrypt(plaintext, AES_KEY_128)
        assert decrypt(base64.b64encode(ciphertext).decode(), AES_KEY_128) == plaintext

    def test_roundtrip_empty_string(self):
        plaintext = ""
        ciphertext = encrypt(plaintext, AES_KEY_128)
        assert decrypt(base64.b64encode(ciphertext).decode(), AES_KEY_128) == plaintext

    def test_roundtrip_exact_block_size(self):
        plaintext = "0123456789abcdef"  # exactly 16 bytes
        ciphertext = encrypt(plaintext, AES_KEY_128)
        assert decrypt(base64.b64encode(ciphertext).decode(), AES_KEY_128) == plaintext

    def test_roundtrip_long_string(self):
        plaintext = "x" * 100
        ciphertext = encrypt(plaintext, AES_KEY_128)
        assert decrypt(base64.b64encode(ciphertext).decode(), AES_KEY_128) == plaintext

    def test_encrypt_returns_bytearray(self):
        result = encrypt("test", AES_KEY_128)
        assert isinstance(result, bytearray)

    def test_encrypt_has_zero_iv_prefix(self):
        """Encrypt always uses a zero IV — first 16 bytes must be 0x00."""
        result = encrypt("test", AES_KEY_128)
        iv = result[:16]
        assert iv == bytearray(16)

    def test_encrypt_output_length(self):
        # IV (16) + padded plaintext (1 block minimum)
        result = encrypt("hi", AES_KEY_128)
        assert len(result) == 32  # 16 IV + 16 (padded "hi")

    def test_encrypt_256_bit_key(self):
        plaintext = "test with 256-bit key"
        ciphertext = encrypt(plaintext, AES_KEY_256)
        assert decrypt(base64.b64encode(ciphertext).decode(), AES_KEY_256) == plaintext

    def test_different_keys_produce_different_ciphertext(self):
        plaintext = "same message"
        key1 = AES_KEY_128
        key2 = "ffeeddccbbaa99887766554433221100"
        ct1 = encrypt(plaintext, key1)
        ct2 = encrypt(plaintext, key2)
        assert ct1 != ct2

    def test_deterministic_with_zero_iv(self):
        """Because IV is always zero, the same input must always produce the same output."""
        plaintext = "deterministic test"
        ct1 = encrypt(plaintext, AES_KEY_128)
        ct2 = encrypt(plaintext, AES_KEY_128)
        assert ct1 == ct2
