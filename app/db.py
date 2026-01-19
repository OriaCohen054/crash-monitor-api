# app/db.py
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from app.config import settings


_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    """Singleton Mongo client."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    """Singleton database handle."""
    global _db
    if _db is None:
        _db = get_client()[settings.MONGODB_DB_NAME]
    return _db


def events_collection():
    """Return the events collection."""
    return get_db()["events"]


async def init_db() -> None:
    """
    Create indexes for better query performance.
    This runs on application startup.
    """
    col = events_collection()

    # Common queries:
    # - list latest events
    # - filter by app_id / level / created_at
    await col.create_index([("created_at", DESCENDING)])
    await col.create_index([("app_id", ASCENDING), ("created_at", DESCENDING)])
    await col.create_index([("level", ASCENDING), ("created_at", DESCENDING)])


async def close_db() -> None:
    """Close Mongo client on shutdown."""
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None
