"""Unit tests for core/security.py — password hashing."""

from __future__ import annotations

import os

import pytest

from core.security import hash_password, verify_password


class TestHashPassword:
    def test_returns_hex_string(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        result = hash_password("mypassword")
        assert isinstance(result, str)
        # SHA-256 hex digest is always 64 characters
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_input_same_output(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        assert hash_password("pw") == hash_password("pw")

    def test_different_passwords_different_hashes(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        assert hash_password("pw1") != hash_password("pw2")

    def test_salt_affects_hash(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "salt-a")
        hash_a = hash_password("password")
        monkeypatch.setenv("APP_KEY", "salt-b")
        hash_b = hash_password("password")
        assert hash_a != hash_b

    def test_default_salt_used_when_env_missing(self, monkeypatch):
        monkeypatch.delenv("APP_KEY", raising=False)
        result = hash_password("anything")
        assert len(result) == 64  # still produces a valid hash

    def test_empty_password(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        result = hash_password("")
        assert len(result) == 64


class TestVerifyPassword:
    def test_correct_password(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        hashed = hash_password("secret")
        assert verify_password("secret", hashed) is True

    def test_wrong_password(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        hashed = hash_password("secret")
        assert verify_password("wrong", hashed) is False

    def test_empty_password(self, monkeypatch):
        monkeypatch.setenv("APP_KEY", "test-salt")
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False
