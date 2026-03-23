"""
ICS2000 AES-CBC encryption/decryption.
Ported from original project.
"""

from __future__ import annotations

import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

_ENCODING = "utf-8"
_BLOCK_SIZE = 16


def _pad(s: str) -> str:
    pad_len = _BLOCK_SIZE - len(s) % _BLOCK_SIZE
    return s + pad_len * chr(pad_len)


def decrypt(string: str, aes: str) -> str:
    """Decrypt a base64-encoded AES-CBC string using the given hex AES key."""
    raw = base64.b64decode(string)
    iv = raw[:16]
    ciphertext = raw[16:]
    cipher = AES.new(bytes.fromhex(aes), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), 16).decode(_ENCODING)


def encrypt(string: str, aes: str) -> bytearray:
    """Encrypt a string with AES-CBC using a zero IV, prepend IV to output."""
    padded = _pad(string).encode(_ENCODING)
    iv = bytearray(16)
    cipher = AES.new(bytes.fromhex(aes), AES.MODE_CBC, bytes(iv))
    return bytearray(iv) + bytearray(cipher.encrypt(padded))
