"""
routes/weather.py
Defines: GET /api/weather?city=<name>
"""

import re
import logging
from flask import Blueprint, request, jsonify, current_app

from services.weather_service import get_weather, WeatherServiceError

logger = logging.getLogger(__name__)

weather_bp = Blueprint("weather", __name__, url_prefix="/api")

# Allow letters (including accented), spaces, hyphens, apostrophes, dots
_CITY_PATTERN = re.compile(r"^[a-zA-Z\u00C0-\u024F\s\-'.]{1,100}$")


@weather_bp.get("/weather")
def get_weather_route():
    """
    GET /api/weather?city=London

    Returns 200 with weather JSON on success.
    Returns 400 / 404 / 429 / 500 with { "error": "..." } on failure.
    """
    city: str = request.args.get("city", "").strip()

    # ── Input validation ───────────────────────────────────────
    if not city:
        return jsonify({"error": "Query parameter 'city' is required."}), 400

    if not _CITY_PATTERN.match(city):
        return jsonify({"error": "Invalid city name. Use letters, spaces, or hyphens only."}), 400

    # ── Call service ───────────────────────────────────────────
    cfg = current_app.config

    try:
        data = get_weather(
            city=city,
            api_key=cfg["OWM_API_KEY"],
            base_url=cfg["OWM_BASE_URL"],
            ttl=cfg["CACHE_TTL_SECONDS"],
            timeout=cfg["OWM_TIMEOUT"],
        )
        logger.info("Weather fetched for city='%s'", city)
        return jsonify(data), 200

    except WeatherServiceError as exc:
        logger.warning("WeatherServiceError for city='%s': %s", city, exc)
        return jsonify({"error": str(exc)}), exc.status_code

    except Exception as exc:                          # pragma: no cover
        logger.exception("Unhandled error for city='%s': %s", city, exc)
        return jsonify({"error": "An unexpected server error occurred."}), 500
