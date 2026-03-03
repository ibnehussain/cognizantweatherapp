"""
config.py — Load and expose all environment-based configuration.
All sensitive values (API keys, connection strings) are read from
the .env file via python-dotenv and never hardcoded.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask ──────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # ── CORS ───────────────────────────────────────────────────
    # Comma-separated list of allowed frontend origins
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")
        if o.strip()
    ]

    # ── OpenWeatherMap ─────────────────────────────────────────
    OWM_API_KEY: str = os.getenv("OWM_API_KEY", "")
    OWM_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
    OWM_TIMEOUT: int = int(os.getenv("OWM_TIMEOUT", "8"))   # seconds

    # ── In-memory cache ────────────────────────────────────────
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "600"))   # 10 min


def validate_config(cfg: Config) -> None:
    """Raise at startup if any required value is missing."""
    if not cfg.OWM_API_KEY:
        raise RuntimeError(
            "OWM_API_KEY is not set. "
            "Add it to your .env file: OWM_API_KEY=your_api_key_here"
        )
