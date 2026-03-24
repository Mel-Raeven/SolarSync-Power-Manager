from __future__ import annotations

import os

from fastapi import Header, HTTPException


async def verify_api_key(x_internal_api_key: str = Header(...)) -> None:
    expected = os.getenv("INTERNAL_API_KEY", "")
    if not expected:
        raise RuntimeError("INTERNAL_API_KEY environment variable is not set")
    if x_internal_api_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
