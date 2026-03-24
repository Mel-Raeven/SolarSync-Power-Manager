"""Unit tests for core/security.py — password hashing."""

from __future__ import annotations

import pytest

from core.security import hash_password, verify_password


class TestHashPassword:
    def test_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_bcrypt_hash_format(self):
        result = hash_password("mypassword")
        # bcrypt hashes start with $2b$ and are 60 characters long
        assert result.startswith("$2b$")
        assert len(result) == 60

    def test_different_passwords_different_hashes(self):
        assert hash_password("pw1") != hash_password("pw2")

    def test_each_call_produces_unique_hash(self):
        # bcrypt generates a new random salt on every call
        assert hash_password("pw") != hash_password("pw")

    def test_empty_password(self):
        result = hash_password("")
        assert result.startswith("$2b$")


class TestVerifyPassword:
    def test_correct_password(self):
        hashed = hash_password("secret")
        assert verify_password("secret", hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("secret")
        assert verify_password("wrong", hashed) is False

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False
