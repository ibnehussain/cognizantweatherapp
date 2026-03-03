# API Reference — CognizantWeatherApp

All API endpoints are served by the Flask backend at the base URL `http://localhost:5000` (development) or your Azure App Service URL (production).

---

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [GET /api/health](#get-apihealth)
  - [GET /api/weather](#get-apiweather)
- [Response Schemas](#response-schemas)
  - [Weather Object](#weather-object)
  - [Error Object](#error-object)
- [HTTP Status Codes](#http-status-codes)
- [cURL Examples](#curl-examples)

---

## Base URL

| Environment | URL |
|---|---|
| Local development | `http://localhost:5000` |
| Azure App Service | `https://<AZURE_WEBAPP_NAME>.azurewebsites.net` |

All API routes are prefixed with `/api`.

---

## Authentication

No authentication is required to call the API. The backend uses its own `OWM_API_KEY` (stored as an environment variable) to communicate with OpenWeatherMap — this key is never exposed to the client.

---

## Endpoints

### GET /api/health

Returns a simple liveness indicator. Use this endpoint to verify the service is running (e.g. in Azure health checks or a load balancer).

**Request**

```
GET /api/health
```

No parameters, no request body.

**Response — 200 OK**

```json
{
  "status": "ok"
}
```

**cURL**

```bash
curl http://localhost:5000/api/health
```

---

### GET /api/weather

Returns current weather data for a given city name, fetched from OpenWeatherMap (with in-memory caching).

**Request**

```
GET /api/weather?city={city}
```

**Query parameters**

| Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `city` | string | Yes | 1–100 characters; letters (including accented), spaces, hyphens, apostrophes, dots | City name to search |

**Success response — 200 OK**

```json
{
  "city":         "London",
  "country":      "GB",
  "temp_c":       12.3,
  "feels_like_c": 10.1,
  "humidity":     78,
  "wind_speed":   14.4,
  "condition":    "Overcast clouds",
  "icon":         "04d"
}
```

See [Weather Object](#weather-object) for field descriptions.

**Error responses**

| HTTP status | Trigger | `error` value |
|---|---|---|
| `400` | `city` parameter is missing or empty | `"Query parameter 'city' is required."` |
| `400` | `city` contains invalid characters | `"Invalid city name. Use letters, spaces, or hyphens only."` |
| `404` | City not found in OpenWeatherMap | `"City '{city}' not found. Please check the spelling."` |
| `429` | OpenWeatherMap rate limit exceeded | `"Too many requests to the weather service. Try again later."` |
| `500` | Invalid or revoked OWM API key | `"Weather service authentication failed."` |
| `502` | Unexpected non-OK response from OWM | `"Unexpected error from weather service."` |
| `503` | OWM request timed out | `"Weather service timed out. Please try again."` |
| `503` | Cannot reach OWM (network error) | `"Cannot reach the weather service. Check your connection."` |
| `500` | Unhandled server exception | `"An unexpected server error occurred."` |

All error bodies follow the [Error Object](#error-object) schema.

---

## Response Schemas

### Weather Object

| Field | Type | Unit | Description |
|---|---|---|---|
| `city` | string | — | City name as returned by OpenWeatherMap |
| `country` | string | — | ISO 3166-1 alpha-2 country code (e.g. `"GB"`) |
| `temp_c` | number | °C | Current temperature, rounded to 1 decimal place |
| `feels_like_c` | number | °C | "Feels like" temperature, rounded to 1 decimal place |
| `humidity` | integer | % | Relative humidity (0–100) |
| `wind_speed` | number | km/h | Wind speed converted from m/s, rounded to 1 decimal place |
| `condition` | string | — | Weather condition description, capitalised (e.g. `"Overcast clouds"`) |
| `icon` | string | — | OpenWeatherMap icon code; use with `https://openweathermap.org/img/wn/{icon}@2x.png` |

**Icon URL example**

```
https://openweathermap.org/img/wn/04d@2x.png
```

**Temperature conversion (client-side)**

The API always returns temperatures in Celsius. The frontend converts to Fahrenheit using:

```
°F = round((°C × 9/5) + 32)
```

### Error Object

```json
{
  "error": "Human-readable error message."
}
```

| Field | Type | Description |
|---|---|---|
| `error` | string | A human-readable message describing what went wrong |

---

## HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad request — invalid or missing input |
| `404` | City not found |
| `429` | Rate limit exceeded |
| `500` | Server-side error (auth failure or unhandled exception) |
| `502` | Bad gateway — unexpected upstream error |
| `503` | Service unavailable — OWM timeout or connection failure |

---

## cURL Examples

### Health check

```bash
curl -s http://localhost:5000/api/health | python -m json.tool
```

```json
{
    "status": "ok"
}
```

### Successful weather lookup

```bash
curl -s "http://localhost:5000/api/weather?city=Tokyo" | python -m json.tool
```

```json
{
    "city": "Tokyo",
    "country": "JP",
    "temp_c": 18.5,
    "feels_like_c": 17.8,
    "humidity": 65,
    "wind_speed": 10.8,
    "condition": "Clear sky",
    "icon": "01d"
}
```

### City not found (404)

```bash
curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/weather?city=Atlantis"
# 404

curl -s "http://localhost:5000/api/weather?city=Atlantis"
```

```json
{
    "error": "City 'Atlantis' not found. Please check the spelling."
}
```

### Missing city parameter (400)

```bash
curl -s "http://localhost:5000/api/weather"
```

```json
{
    "error": "Query parameter 'city' is required."
}
```

### Invalid city characters (400)

```bash
curl -s "http://localhost:5000/api/weather?city=L0nd0n!!!"
```

```json
{
    "error": "Invalid city name. Use letters, spaces, or hyphens only."
}
```

### City with spaces (URL-encoded)

```bash
curl -s "http://localhost:5000/api/weather?city=New%20York"
```

### City with accented characters

```bash
curl -s "http://localhost:5000/api/weather?city=M%C3%BCnchen"   # München
```
