# app/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv


# Load .env if exists (local dev). On Koyeb you set env vars in the UI.
load_dotenv()


def _get_env(name: str, default: str = "") -> str:
    """Read environment variable with a default fallback."""
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.
    Keep this file dependency-free (besides dotenv) to avoid startup issues.
    """

    # Mongo
    MONGODB_URI: str = _get_env("MONGODB_URI")
    MONGODB_DB_NAME: str = _get_env("MONGODB_DB_NAME", "crash_monitor")

    # Security
    API_KEY: str = _get_env("API_KEY")

    # Optional: allow disabling API-key requirement locally
    # e.g. REQUIRE_API_KEY=0
    REQUIRE_API_KEY: bool = _get_env("REQUIRE_API_KEY", "1") not in ("0", "false", "False", "")

    # CORS (optional)
    # e.g. ALLOWED_ORIGINS="http://localhost:3000,https://my-dashboard.com"
    ALLOWED_ORIGINS: str = _get_env("ALLOWED_ORIGINS", "*")

    # General
    ENV: str = _get_env("ENV", "prod")  # dev/prod


settings = Settings()


def validate_settings() -> None:
    """
    Validate required settings early, so we fail fast with a clear error.
    """
    if not settings.MONGODB_URI:
        raise RuntimeError("MONGODB_URI is missing. Set it in .env or Koyeb env vars.")

    # API_KEY can be optional if REQUIRE_API_KEY=0
    if settings.REQUIRE_API_KEY and not settings.API_KEY:
        raise RuntimeError("API_KEY is missing while REQUIRE_API_KEY=1.")
