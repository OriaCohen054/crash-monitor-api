from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load .env from project root (C:\crash-monitor-api\.env)
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

client: AsyncIOMotorClient | None = None


def get_db():
    if client is None:
        raise RuntimeError("Mongo client not initialized")
    db_name = os.getenv("DB_NAME", "crash_monitor")
    return client[db_name]


async def connect_db():
    global client

    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise RuntimeError("MONGODB_URI is missing (set it in .env)")

    client = AsyncIOMotorClient(mongodb_uri)


async def close_db():
    global client
    if client is not None:
        client.close()
        client = None
