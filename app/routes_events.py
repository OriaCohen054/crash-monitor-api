from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from .models import EventIn
from .db import get_db

router = APIRouter(prefix="/events", tags=["events"])

def _doc_to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "received_at": doc["received_at"],
        "event": doc["event"],
    }

@router.post("", summary="Create Event")
async def create_event(payload: EventIn):
    db = get_db()
    doc = {
        "received_at": datetime.utcnow(),
        "event": payload.model_dump(),
    }
    res = await db.events.insert_one(doc)
    created = await db.events.find_one({"_id": res.inserted_id})
    return _doc_to_out(created)

@router.get("", summary="List Events")
async def list_events(
    app_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    db = get_db()

    q = {}
    if app_id:
        q["event.app_id"] = app_id
    if user_id:
        q["event.user_id"] = user_id
    if type:
        q["event.type"] = type

    cursor = db.events.find(q).sort("received_at", -1).limit(limit)
    items = [_doc_to_out(doc) async for doc in cursor]

    return {"count": len(items), "items": items}

@router.get("/{event_id}", summary="Get Event By Id")
async def get_event(event_id: str):
    db = get_db()
    try:
        oid = ObjectId(event_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event_id")

    doc = await db.events.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Event not found")

    return _doc_to_out(doc)
