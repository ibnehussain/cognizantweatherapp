# CognizantWeatherApp

> A full-stack weather dashboard — search current conditions for any city worldwide, with live unit switching and persistent search history.

Built with **Flask** (Python backend) and **vanilla JavaScript** (frontend), powered by the [OpenWeatherMap API](https://openweathermap.org/api). Deploys to **Azure App Service** via GitHub Actions.

---

## Table of Contents

- [Features](#features)
- [Live Demo / Screenshots](#live-demo--screenshots)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Local)](#quick-start-local)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [CI/CD & Deployment](#cicd--deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Category | Details |
|---|---|
| **Weather data** | Real-time temperature, humidity, wind speed, "feels like", weather condition and icon |
| **Unit toggle** | Switch between °C and °F instantly without re-fetching |
| **Search history** | Last 5 searches persisted in `localStorage`; one-click re-search |
| **Caching** | Thread-safe in-memory TTL cache (default 10 min) on the backend to reduce API calls |
| **Error handling** | Human-readable error messages for invalid input, city-not-found, timeouts, and rate limits |
| **Accessibility** | WCAG 2.1 AA — ARIA labels, live regions, focus management, visible focus rings |
| **Responsive UI** | Glassmorphism design works on mobile (360 px+), tablet, and desktop |
| **Zero JS framework** | Pure HTML + CSS + vanilla JS — no build step required for the frontend |

---

## Live Demo / Screenshots

> Deploy your own copy in minutes — see [CI/CD & Deployment](#cicd--deployment).

```
http://localhost:5000    ← after local setup
```

The UI shows a sky-blue animated gradient background with a glassmorphism weather card:

```
┌─────────────────────────────────────┐
│  ☁️ WeatherDash              °C  °F  │  ← header with unit toggle
├─────────────────────────────────────┤
│  [ 🔍  Search city…  e.g. London  ] │  ← search bar
│                                     │
│  London                 Mon, 2 Mar  │
│  GB                                 │
│  🌤️  Partly Cloudy        12 °C     │
│  💧 Humidity  💨 Wind  🌡 Feels Like │
│     78%        14 km/h    10°C      │
│                                     │
│  Recent: London  Paris  Tokyo       │  ← history chips
└─────────────────────────────────────┘
```

---

## Architecture

```
┌─────────────────── Browser ──────────────────────┐
│  index.html  ──  styles.css  ──  app.js           │
│  (search form, weather card, history chips)       │
└──────────────┬───────────────────────────────────┘
               │  GET /api/weather?city=London
               ▼
┌─────────────────── Flask (Python) ───────────────┐
│  app.py  (application factory, CORS, static)     │
│    └── routes/weather.py  (input validation)     │
│          └── services/weather_service.py         │
│                ├── in-memory TTL cache           │
│                └── OpenWeatherMap REST API       │
└──────────────────────────────────────────────────┘
               │  JSON { city, temp_c, humidity … }
               ▼
         Azure App Service  (gunicorn)
```

Full Mermaid diagrams — including sequence and error-flow diagrams — are in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Project Structure

```
cognizantweatherapp/
├── .github/
│   └── workflows/
│       └── azure-deploy.yml      # GitHub Actions — build & deploy to Azure
├── backend/
│   ├── app.py                    # Application factory (Flask entry point)
│   ├── config.py                 # Environment-based configuration class
│   ├── requirements.txt          # Python runtime dependencies
│   ├── .env.example              # Template for local environment variables
│   ├── routes/
│   │   ├── __init__.py
│   │   └── weather.py            # GET /api/weather route + input validation
│   └── services/
│       ├── __init__.py
│       └── weather_service.py    # OWM integration, response parsing, TTL cache
├── frontend/
│   ├── index.html                # Single-page app shell
│   ├── css/
│   │   └── styles.css            # Responsive glassmorphism styles + animations
│   └── js/
│       └── app.js                # Fetch, DOM updates, unit toggle, history
├── docs/
│   ├── ARCHITECTURE.md           # Detailed architecture + Mermaid diagrams
│   ├── API.md                    # Full API reference with examples
│   ├── DEPLOYMENT.md             # Step-by-step Azure deployment guide
│   └── CONTRIBUTING.md           # Contributing guide & coding standards
└── README.md
```

---

## Prerequisites

| Requirement | Minimum version | Notes |
|---|---|---|
| Python | 3.11 | Uses `list[str]` type hints |
| pip | latest | `python -m pip install --upgrade pip` |
| OpenWeatherMap API key | free tier | [Sign up](https://home.openweathermap.org/api_keys) |

No Node.js or front-end build tools are required.

---

## Quick Start (Local)

### 1. Clone the repository

```bash
git clone https://github.com/ibnehussain/cognizantweatherapp.git
cd cognizantweatherapp
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in your values:

```env
OWM_API_KEY=your_openweathermap_api_key   # required
SECRET_KEY=replace-with-a-long-random-string
FLASK_DEBUG=true
CACHE_TTL_SECONDS=600
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```

> **Tip:** Generate a strong secret key with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 5. Run the development server

```bash
cd backend
python app.py
```

Open **http://localhost:5000** in your browser.  
The Flask process serves both the API (`/api/*`) and the static frontend from `frontend/`.

---

## API Reference

### Health check

```
GET /api/health
```

**Response — 200 OK**
```json
{ "status": "ok" }
```

---

### Get current weather

```
GET /api/weather?city={city}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `city` | string | Yes | City name (1–100 chars, letters / spaces / hyphens / apostrophes / dots) |

**Success — 200 OK**
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

> `wind_speed` is in **km/h**. `icon` maps to `https://openweathermap.org/img/wn/{icon}@2x.png`.

**Error responses**

| HTTP status | Condition | `error` message |
|---|---|---|
| `400` | Missing or invalid `city` parameter | `"Query parameter 'city' is required."` / `"Invalid city name…"` |
| `404` | City not found in OpenWeatherMap | `"City 'XYZ' not found. Please check the spelling."` |
| `429` | OWM rate limit reached | `"Too many requests to the weather service. Try again later."` |
| `500` | Invalid or missing API key | `"Weather service authentication failed."` |
| `502` | Unexpected OWM error | `"Unexpected error from weather service."` |
| `503` | OWM timeout or unreachable | `"Weather service timed out. Please try again."` |

All error responses have the shape:
```json
{ "error": "Human-readable message." }
```

Full cURL examples and Postman collection: [`docs/API.md`](docs/API.md).

---

## Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `OWM_API_KEY` | — | **Yes** | OpenWeatherMap API key |
| `SECRET_KEY` | `change-me-in-production` | **Yes** (prod) | Flask session secret |
| `FLASK_DEBUG` | `false` | No | Enable Flask debug mode (`true`/`false`) |
| `OWM_TIMEOUT` | `8` | No | HTTP timeout for OWM requests (seconds) |
| `CACHE_TTL_SECONDS` | `600` | No | How long weather responses are cached (seconds) |
| `CORS_ORIGINS` | `http://localhost:5500,http://127.0.0.1:5500` | No | Comma-separated list of allowed frontend origins |

> ⚠️ Never commit your real `.env` file — it is in `.gitignore`.  
> See `backend/.env.example` for a full template.

---

## CI/CD & Deployment

Every push to `main` triggers the GitHub Actions workflow in [`.github/workflows/azure-deploy.yml`](.github/workflows/azure-deploy.yml), which:

1. Checks out the code and sets up Python 3.11.
2. Installs dependencies + `gunicorn`.
3. Writes a `.env` from GitHub Secrets.
4. Zips the artifact (excluding `.git`, `__pycache__`, `venv`).
5. Deploys to **Azure App Service** using the publish profile.

### Required GitHub Secrets

| Secret | Where to get it |
|---|---|
| `AZURE_WEBAPP_NAME` | Your Azure App Service resource name |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Azure Portal → App Service → **Get publish profile** |
| `OWM_API_KEY` | [openweathermap.org/api_keys](https://home.openweathermap.org/api_keys) |
| `SECRET_KEY` | Any long random string |

For a full step-by-step guide including Azure resource creation, see [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

---

## Documentation

| Document | Contents |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Component breakdown, Mermaid system / sequence / error-flow diagrams |
| [`docs/API.md`](docs/API.md) | Full API reference, cURL examples, response schemas |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Local setup, Azure App Service deployment walk-through, gunicorn config, troubleshooting |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Branch strategy, code style, pull request checklist |

---

## Contributing

Contributions are welcome! Please read [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) before opening a pull request.

---

## License

[MIT](LICENSE)
