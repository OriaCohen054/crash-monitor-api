from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes_events import router as events_router
from .db import connect_db, close_db

app = FastAPI(title="Crash Monitor API", version="0.1.0")

# CORS: for future React admin portal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later we can restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await connect_db()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db()

@app.get("/")
def root():
    return {"status": "ok", "service": "crash-monitor-api"}

@app.get("/health")
async def health():
    # If we reached here and startup didn't crash, DB is configured.
    return {"ok": True}

app.include_router(events_router)
