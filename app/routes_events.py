# app/routes_events.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.errors import PyMongoError

from app.db import events_collection
from app.models import EventIn, EventOut
from app.security import require_api_key


router = APIRouter(prefix="/events", tags=["events"])


def _now_iso() -> str:
    """Server-side creation time."""
    return datetime.now(timezone.utc).isoformat()


def _model_dump(obj) -> Dict[str, Any]:
    """
    Support both Pydantic v1 (.dict()) and v2 (.model_dump()).
    """
    if hasattr(obj, "model_dump"):  # Pydantic v2
        return obj.model_dump()
    return obj.dict()               # Pydantic v1


def _to_event_out(doc: Dict[str, Any]) -> EventOut:
    """Convert Mongo document to API response model."""
    return EventOut(
        id=str(doc["_id"]),
        created_at=doc.get("created_at", ""),
        **{k: v for k, v in doc.items() if k not in ("_id", "created_at")},
    )


@router.post("", response_model=EventOut, dependencies=[Depends(require_api_key)])
async def create_event(payload: EventIn):
    """
    Ingest a new crash/event (protected by API key).
    """
    try:
        doc = _model_dump(payload)
        doc["created_at"] = _now_iso()

        res = await events_collection().insert_one(doc)
        saved = await events_collection().find_one({"_id": res.inserted_id})
        return _to_event_out(saved)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


@router.get("", response_model=List[EventOut])
async def list_events(
    app_id: Optional[str] = Query(default=None),
    level: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
):
    """
    List events with optional filters and pagination.

    Examples:
    - /events?limit=20
    - /events?app_id=demo-app&level=error
    """
    q: Dict[str, Any] = {}
    if app_id:
        q["app_id"] = app_id
    if level:
        q["level"] = level
    if event_type:
        q["event_type"] = event_type

    docs = (
        await events_collection()
        .find(q)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )
    return [_to_event_out(d) for d in docs]


@router.get("/{event_id}", response_model=EventOut)
async def get_event_by_id(event_id: str):
    """
    Get single event by Mongo ObjectId.
    - 400 if the id format is invalid
    - 404 if not found
    """
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event_id format (expected Mongo ObjectId)",
        )

    doc = await events_collection().find_one({"_id": ObjectId(event_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return _to_event_out(doc)
