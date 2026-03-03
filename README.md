# CognizantWeatherApp

A full-stack weather dashboard built with **Flask** (backend) and vanilla **JavaScript** (frontend), powered by the [OpenWeatherMap API](https://openweathermap.org/api).

---

## Features

- Real-time weather data by city name
- Temperature, humidity, wind speed, and conditions
- In-memory response caching (configurable TTL)
- CORS-enabled REST API under `/api/*`
- Frontend served directly by Flask (no separate web server needed)
- Health check endpoint at `/api/health`

---

## Project Structure

```
newcognizantapp/
├── backend/
│   ├── app.py                  # Application factory (entry point)
│   ├── config.py               # Environment-based configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Sample environment variables
│   ├── routes/
│   │   └── weather.py          # Weather API routes
│   └── services/
│       └── weather_service.py  # OpenWeatherMap integration + cache
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/app.js
```

---

## Prerequisites

- Python 3.11+
- An [OpenWeatherMap API key](https://home.openweathermap.org/api_keys) (free tier works)

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/ibnehussain/cognizantweatherapp.git
cd cognizantweatherapp
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
OWM_API_KEY=your_openweathermap_api_key
SECRET_KEY=your_flask_secret_key
FLASK_DEBUG=true
CACHE_TTL_SECONDS=600
```

### 5. Run the app

```bash
cd backend
python app.py
```

Open http://localhost:5000 in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check — returns `{ "status": "ok" }` |
| `GET` | `/api/weather?city={city}` | Current weather for the given city |

---

## Deployment

This app deploys to **Azure App Service** via GitHub Actions.  
See [`.github/workflows/azure-deploy.yml`](.github/workflows/azure-deploy.yml).

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Download from Azure Portal → App Service → Get publish profile |
| `AZURE_WEBAPP_NAME` | Your Azure App Service name |
| `OWM_API_KEY` | OpenWeatherMap API key |
| `SECRET_KEY` | Flask secret key |

---

## Environment Variables Reference

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OWM_API_KEY` | — | Yes | OpenWeatherMap API key |
| `SECRET_KEY` | `change-me-in-production` | Yes (prod) | Flask secret key |
| `FLASK_DEBUG` | `false` | No | Enable debug mode |
| `OWM_TIMEOUT` | `8` | No | API request timeout (seconds) |
| `CACHE_TTL_SECONDS` | `600` | No | Cache duration (seconds) |
| `CORS_ORIGINS` | `http://localhost:5500` | No | Allowed CORS origins (comma-separated) |

---

## License

MIT
