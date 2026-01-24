from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import PyMongoError

from app.db import events_collection
from app.models import EventIn, EventOut
from app.security import require_api_key

router = APIRouter(prefix="/events", tags=["events"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _model_dump(obj) -> Dict[str, Any]:
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    # Pydantic v1
    return obj.dict()


def _to_event_out(doc: Dict[str, Any]) -> EventOut:
    return EventOut(
        id=str(doc["_id"]),
        created_at=doc.get("created_at", ""),
        **{k: v for k, v in doc.items() if k not in ("_id", "created_at")},
    )


@router.post("", response_model=EventOut, dependencies=[Depends(require_api_key)])
async def create_event(payload: EventIn):
    try:
        doc = _model_dump(payload)
        doc["created_at"] = _now_iso()

        res = await events_collection().insert_one(doc)
        saved = await events_collection().find_one({"_id": res.inserted_id})

        if not saved:
            raise HTTPException(status_code=500, detail="Failed to read inserted event")

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
