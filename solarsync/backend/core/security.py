from __future__ import annotations

import hashlib
import os


def hash_password(plaintext: str) -> str:
    """One-way hash a password for storage.
    Uses SHA-256 with a salt derived from APP_KEY.
    For a production system, consider bcrypt (passlib).
    """
    salt = os.getenv("APP_KEY", "solarsync-default-salt")
    return hashlib.sha256(f"{salt}{plaintext}".encode()).hexdigest()


def verify_password(plaintext: str, hashed: str) -> bool:
    return hash_password(plaintext) == hashed
