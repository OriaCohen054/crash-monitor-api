from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

EventType = Literal["crash", "non_fatal", "breadcrumb", "anr", "test"]

class EventIn(BaseModel):
    app_id: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    type: EventType
    message: str = Field(..., min_length=1)
    stacktrace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EventOut(BaseModel):
    id: str
    received_at: datetime
    event: EventIn
