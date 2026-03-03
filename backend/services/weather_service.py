"""
services/weather_service.py
Handles:
  - OpenWeatherMap API calls
  - Response parsing & transformation
  - Thread-safe in-memory cache with TTL
  - Retry logic for transient failures
"""

import time
import threading
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


# ─── In-memory cache ─────────────────────────────────────────────────────────
# Structure: { "london": {"data": {...}, "cached_at": <epoch>} }

_cache: dict = {}
_cache_lock = threading.Lock()


def _is_fresh(entry: dict, ttl: int) -> bool:
    return (time.time() - entry["cached_at"]) < ttl


def _get_cached(city_key: str, ttl: int) -> dict | None:
    with _cache_lock:
        entry = _cache.get(city_key)
        if entry and _is_fresh(entry, ttl):
            logger.debug("Cache HIT for '%s'", city_key)
            return entry["data"]
    return None


def _set_cache(city_key: str, data: dict) -> None:
    with _cache_lock:
        _cache[city_key] = {"data": data, "cached_at": time.time()}
    logger.debug("Cache SET for '%s'", city_key)


# ─── HTTP session with retry ──────────────────────────────────────────────────

def _build_session() -> requests.Session:
    """
    Returns a requests.Session with automatic retry on transient errors:
    - Retries up to 3 times on 500, 502, 503, 504
    - Exponential back-off: 0s, 0.5s, 1s
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_session = _build_session()


# ─── Public API ──────────────────────────────────────────────────────────────

class WeatherServiceError(Exception):
    """Raised when the weather service cannot fulfil a request."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


def get_weather(city: str, api_key: str, base_url: str,
                ttl: int, timeout: int) -> dict:
    """
    Returns structured weather data for *city*.

    Checks the in-memory cache first; only calls OpenWeatherMap on
    a cache miss.  Parsed response is cached for *ttl* seconds.

    Parameters
    ----------
    city     : city name as received from the route
    api_key  : OWM API key
    base_url : OWM endpoint URL
    ttl      : cache TTL in seconds
    timeout  : HTTP request timeout in seconds

    Returns
    -------
    dict with keys:
        city, country, temp_c, feels_like_c, humidity,
        wind_speed, condition, icon

    Raises
    ------
    WeatherServiceError  on city-not-found (404) or any backend problem
    """
    city_key = city.strip().lower()

    # 1. Cache lookup
    cached = _get_cached(city_key, ttl)
    if cached:
        return cached

    # 2. Call OpenWeatherMap
    params = {
        "q":     city.strip(),
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = _session.get(base_url, params=params, timeout=timeout)
    except requests.exceptions.Timeout:
        logger.error("OWM request timed out for city='%s'", city)
        raise WeatherServiceError(
            "Weather service timed out. Please try again.", status_code=503
        )
    except requests.exceptions.ConnectionError as exc:
        logger.error("OWM connection error: %s", exc)
        raise WeatherServiceError(
            "Cannot reach the weather service. Check your connection.", status_code=503
        )

    # 3. Handle OWM error codes
    if response.status_code == 404:
        raise WeatherServiceError(
            f"City '{city}' not found. Please check the spelling.",
            status_code=404,
        )
    if response.status_code == 401:
        logger.error("Invalid OWM API key")
        raise WeatherServiceError("Weather service authentication failed.", status_code=500)
    if response.status_code == 429:
        raise WeatherServiceError(
            "Too many requests to the weather service. Try again later.",
            status_code=429,
        )
    if not response.ok:
        logger.error("OWM returned %s for city='%s'", response.status_code, city)
        raise WeatherServiceError(
            "Unexpected error from weather service.", status_code=502
        )

    # 4. Parse & transform
    raw = response.json()
    data = _parse_owm_response(raw)

    # 5. Cache result
    _set_cache(city_key, data)

    return data


def _parse_owm_response(raw: dict) -> dict:
    """
    Transforms the raw OpenWeatherMap JSON into the shape
    expected by the frontend.
    """
    return {
        "city":        raw.get("name", ""),
        "country":     raw.get("sys", {}).get("country", ""),
        "temp_c":      round(raw["main"]["temp"], 1),
        "feels_like_c": round(raw["main"]["feels_like"], 1),
        "humidity":    raw["main"]["humidity"],
        "wind_speed":  round(raw.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s → km/h
        "condition":   raw["weather"][0]["description"].capitalize(),
        "icon":        raw["weather"][0]["icon"],
    }
