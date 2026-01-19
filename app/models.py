# app/models.py
from typing import Any, Dict, List, Optional
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
    version_code: Optional[str] = None
    build_type: Optional[str] = None       # debug/release
    package_name: Optional[str] = None


class SdkInfo(BaseModel):
    """SDK metadata."""
    name: str = Field(default="crash-monitor-sdk")
    version: Optional[str] = None


class Breadcrumb(BaseModel):
    """Small timeline records before crash."""
    ts: Optional[str] = None
    category: Optional[str] = None
    message: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


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

    # Useful additional data
    user_id: Optional[str] = None
    device_id: Optional[str] = None

    tags: Dict[str, str] = Field(default_factory=dict, description="Key-value tags")
    breadcrumbs: List[Breadcrumb] = Field(default_factory=list)

    # Free-form extras
    meta: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")


class EventOut(EventIn):
    """Event model returned to clients."""
    id: str
    created_at: str
