# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, validate_settings
from app.db import init_db, close_db
from app.routes_events import router as events_router


def create_app() -> FastAPI:
    """
    App factory.
    Makes it easier to test and keeps the global module clean.
    """
    app = FastAPI(
        title="Crash Monitor API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )

    # CORS configuration (optional)
    # If ALLOWED_ORIGINS="*" -> allow all
    if settings.ALLOWED_ORIGINS == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup():
        # Validate env vars early (fail fast)
        validate_settings()
        # Prepare DB indexes
        await init_db()

    @app.on_event("shutdown")
    async def on_shutdown():
        await close_db()

    @app.get("/")
    def root():
        return {"status": "ok", "service": "crash-monitor-api"}

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    app.include_router(events_router)
    return app


app = create_app()
