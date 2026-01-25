from typing import List, Optional, Dict, Any, Union
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
    limit: Union[int, str] = Query(default=50),
    skip: Union[int, str] = Query(default=0),
):
    # Retool (or clients) sometimes send skip/limit as strings.
    # This keeps the endpoint stable instead of returning 422.
    def _to_int(v, default: int) -> int:
        try:
            if v is None:
                return default
            if isinstance(v, int):
                return v
            return int(str(v).strip())
        except Exception:
            return default

    limit_i = _to_int(limit, 50)
    skip_i = _to_int(skip, 0)

    # Keep the same safety bounds as before (1..200) and non-negative skip
    if limit_i < 1:
        limit_i = 50
    if limit_i > 200:
        limit_i = 200
    if skip_i < 0:
        skip_i = 0

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
            .skip(skip_i)
            .limit(limit_i)
        )

        docs = await cursor.to_list(length=limit_i)
        return [_to_event_out(d) for d in docs]

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

