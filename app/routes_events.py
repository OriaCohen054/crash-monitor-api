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
    """Server-side creation time (UTC ISO format)."""
    return datetime.now(timezone.utc).isoformat()


def _model_dump(obj) -> Dict[str, Any]:
    """
    Support both Pydantic v1 (.dict()) and v2 (.model_dump()).
    """
    if hasattr(obj, "model_dump"):  # Pydantic v2
        return obj.model_dump()
    return obj.dict()               # Pydantic v1


def _doc_to_payload(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the event payload fields from a Mongo document."""
    return {k: v for k, v in doc.items() if k not in ("_id", "created_at")}


def _to_event_out(doc: Dict[str, Any]) -> EventOut:
    """
    Convert Mongo document to API response model:
    returns { id, created_at, payload: {...} }
    """
    return EventOut(
        id=str(doc["_id"]),
        created_at=doc.get("created_at", ""),
        payload=_doc_to_payload(doc),
    )


@router.post("", response_model=EventOut, dependencies=[Depends(require_api_key)])
async def create_event(payload: EventIn):
    """
    Ingest a new crash/event (protected by API key).
    Stores payload fields flat in Mongo (as you already do),
    but returns EventOut wrapper with payload.
    """
    try:
        doc = _model_dump(payload)          # <-- flat fields
        doc["created_at"] = _now_iso()

        res = await events_collection().insert_one(doc)
        saved = await events_collection().find_one({"_id": res.inserted_id})

        if not saved:
            raise HTTPException(status_code=500, detail="Failed to read inserted event")

        return _to_event_out(saved)

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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
    """
    q: Dict[str, Any] = {}
    if app_id:
        q["app_id"] = app_id
    if level:
        q["level"] = level
    if event_type:
        q["event_type"] = event_type

    try:
        cursor = (
            events_collection()
            .find(q)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        docs = await cursor.to_list(length=limit)
        return [_to_event_out(d) for d in docs]

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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

    try:
        doc = await events_collection().find_one({"_id": ObjectId(event_id)})
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return _to_event_out(doc)
