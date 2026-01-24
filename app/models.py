# app/models.py
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    """Client device information."""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    os_name: Optional[str] = None          # Android/iOS
    os_version: Optional[str] = None
    locale: Optional[str] = None


class AppInfo(BaseModel):
    """App build/version details."""
    version_name: Optional[str] = None
    # accept both "123" and 123 from clients (avoid 422 on stricter parsing)
    version_code: Optional[Union[str, int]] = None
    build_type: Optional[str] = None       # debug/release
    package_name: Optional[str] = None
    display_name: Optional[str] = None


class SdkInfo(BaseModel):
    """SDK metadata."""
    name: str = Field(default="crash-monitor-sdk")
    version: Optional[str] = None


class Breadcrumb(BaseModel):
    """Small timeline record."""
    ts: Optional[str] = None
    category: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None


class MetaInfo(BaseModel):
    """Client metadata + custom props."""
    client_event_id: Optional[str] = None
    name: Optional[str] = None
    props: Optional[Dict[str, Any]] = None


class EventIn(BaseModel):
    """
    Incoming crash/event payload.
    Keep it flexible: allow meta/custom fields for future expansion.
    """

    # Required minimal fields
    app_id: str = Field(..., description="Application identifier (e.g. demo-app)")
    message: str = Field(..., description="Main message for the crash/event")

    # Optional fields
    level: str = Field(default="error", description="error/warn/info")
    event_type: str = Field(default="crash", description="crash/exception/log/anr")
    stacktrace: Optional[str] = Field(default=None, description="Stack trace if available")

    # Time
    timestamp: Optional[str] = Field(default=None, description="Client timestamp (ISO)")

    # Structured info
    device: Optional[DeviceInfo] = None
    app: Optional[AppInfo] = None
    sdk: Optional[SdkInfo] = None

    # Identity
    user_id: Optional[str] = None
    device_id: Optional[str] = None

    # Flexible key/values
    tags: Optional[Dict[str, str]] = None

    # Timeline
    breadcrumbs: Optional[List[Breadcrumb]] = None

    # Arbitrary meta
    meta: Optional[Dict[str, Any]] = None


class EventOut(BaseModel):
    """Outgoing event record from DB."""
    id: str
    created_at: str
    payload: EventIn
