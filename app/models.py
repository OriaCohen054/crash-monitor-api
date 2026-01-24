from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    locale: Optional[str] = None


class AppInfo(BaseModel):
    version_name: Optional[str] = None
    # accept both "123" and 123 (avoid 422)
    version_code: Optional[Union[str, int]] = None
    build_type: Optional[str] = None
    package_name: Optional[str] = None
    display_name: Optional[str] = None


class SdkInfo(BaseModel):
    name: str = Field(default="crash-monitor-sdk")
    version: Optional[str] = None


class Breadcrumb(BaseModel):
    ts: Optional[str] = None
    category: Optional[str] = None
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


class EventIn(BaseModel):
    app_id: str
    message: str
    level: str
    event_type: str
    stacktrace: Optional[str] = None
    timestamp: str

    device: DeviceInfo
    app: AppInfo
    sdk: SdkInfo

    user_id: Optional[str] = None
    device_id: str

    tags: Dict[str, str] = Field(default_factory=dict)
    breadcrumbs: List[Breadcrumb] = Field(default_factory=list)

    # allow any shape here (fits "additionalPropX" וגם meta שלך מה-SDK)
    meta: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")


class EventOut(EventIn):
    """Event model returned to clients (flat)."""
    id: str
    created_at: str
