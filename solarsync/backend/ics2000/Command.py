"""
ICS2000 binary command builder.
Ported from original project.
"""

from __future__ import annotations

from ics2000.Cryptographer import encrypt
from ics2000.Bytes import insertbytes, insertint16, insertint32


class Command:
    """Builds the 43-byte binary header + AES-encrypted payload for ICS2000."""

    def __init__(self) -> None:
        self._header = bytearray(43)
        self._data: bytearray = bytearray()
        self._set_frame(1)

    def _set_frame(self, num: int) -> None:
        if 0 <= num <= 255:
            self._header[0] = num & 0xFF

    def settype(self, num: int) -> None:
        if 0 <= num <= 255:
            self._header[2] = num & 0xFF

    def setmac(self, mac: str) -> None:
        arr = bytes.fromhex(mac.replace(":", ""))
        if len(arr) == 6:
            insertbytes(self._header, arr, 3)

    def setmagic(self) -> None:
        insertint32(self._header, 653213, 9)

    def setentityid(self, entity_id: int) -> None:
        insertint32(self._header, entity_id, 29)

    def setdata(self, data: str, aes: str) -> None:
        self._data = encrypt(data, aes)

    def getcommand(self) -> str:
        insertint16(self._header, len(self._data), 41)
        return self._header.hex() + self._data.hex()
