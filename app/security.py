# app/security.py
from typing import Optional
import hmac

from fastapi import Header, HTTPException, status

from app.config import settings


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    """
    API-key guard dependency.

    Client must send:
      X-API-Key: <value>

    Notes:
    - In production you typically require this for ingestion endpoints (POST /events).
    - You can disable it locally by setting REQUIRE_API_KEY=0.
    """
    if not settings.REQUIRE_API_KEY:
        return True

    if not settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API_KEY is not set",
        )

    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    # Constant-time comparison to reduce timing attacks
    if not hmac.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return True
