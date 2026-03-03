# Weather Dashboard App — Plan

## Functional Requirements

### Frontend (HTML + CSS + JavaScript)
- **FR1** — User can type a city name into an input field and submit it.
- **FR2** — App displays current weather data for the searched city, including:
  - Temperature (°C / °F)
  - Weather condition (e.g., Sunny, Rainy)
  - Humidity percentage
  - Wind speed
  - Weather icon
  - City name and country code
- **FR3** — User can toggle between Celsius and Fahrenheit.
- **FR4** — App displays a loading indicator while fetching data.
- **FR5** — App displays a user-friendly error message for invalid city names.
- **FR6** — Search history is shown (last 5 searches) for quick re-access.

### Backend (Flask)
- **FR7** — Flask exposes a REST API endpoint `GET /api/weather?city={cityName}`.
- **FR8** — Backend fetches weather data from a third-party API (e.g., OpenWeatherMap).
- **FR9** — Backend validates the city name input (non-empty, no special characters).
- **FR10** — Backend returns a structured JSON response to the frontend.
- **FR11** — Backend returns meaningful HTTP error codes (`400`, `404`, `500`).

---

## Non-Functional Requirements

### Performance
- **NFR1** — API response time should be **under 2 seconds** for 95% of requests.
- **NFR2** — Backend should **cache** recent city weather responses (e.g., TTL of 10 minutes) to reduce third-party API calls.

### Reliability
- **NFR3** — App should handle third-party API failures gracefully with a fallback error message.
- **NFR4** — Flask backend should implement **retry logic** for transient third-party API failures.

### Security
- **NFR5** — Third-party API keys must be stored in **environment variables**, never hardcoded.
- **NFR6** — Backend must **sanitize and validate** all user inputs to prevent injection attacks.
- **NFR7** — CORS should be **restricted** to allowed origins only.

### Usability
- **NFR8** — UI must be **responsive** and work on mobile, tablet, and desktop.
- **NFR9** — Error messages must be **human-readable** and clearly visible.
- **NFR10** — App should be accessible (**WCAG 2.1 AA**) — proper labels, contrast ratios.

### Maintainability
- **NFR11** — Code should follow a **clear folder structure** separating frontend and backend.
- **NFR12** — Backend logic should be modular (routes, services, config separated).

### Scalability
- **NFR13** — Backend should be **stateless** to allow horizontal scaling if needed.

---

## Suggested Project Structure

```
weather-dashboard/
├── backend/
│   ├── app.py                      # Flask entry point
│   ├── routes/
│   │   └── weather.py              # /api/weather route
│   ├── services/
│   │   └── weather_service.py      # Third-party API calls + caching
│   ├── config.py                   # Env vars & config
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── .env                            # API keys (never commit this)
```

---

## System Architecture (Mermaid)

```mermaid
graph TB
    subgraph CLIENT["🖥️ Client Layer (Browser)"]
        HTML["index.html\n(Structure)"]
        CSS["styles.css\n(Responsive UI)"]
        JS["app.js\nfetch() + DOM Updates"]
    end

    subgraph FLASK["⚙️ Backend Layer (Flask)"]
        ROUTE["routes/weather.py\nGET /api/weather"]
        SERVICE["services/weather_service.py\nBusiness Logic + Cache"]
        CONFIG["config.py\n.env API Keys"]
    end

    subgraph COSMOS["🗄️ Azure Cosmos DB (NoSQL)"]
        CACHE["weather-cache\nPartition: /city\n_ttl: 600s"]
        HISTORY["search-history\nPartition: /userId"]
    end

    EXT["🌐 OpenWeatherMap API\n(External)"]

    JS -->|"GET /api/weather?city=London"| ROUTE
    ROUTE --> SERVICE
    SERVICE --> CONFIG
    SERVICE <-->|"Cache Lookup / Write"| CACHE
    SERVICE <-->|"External API Call"| EXT
    JS -->|"Save search"| HISTORY
    ROUTE -->|"JSON Response"| JS
```

---

## Request Data Flow (Mermaid)

```mermaid
sequenceDiagram
    actor User
    participant JS as app.js (Browser)
    participant Flask as Flask /api/weather
    participant CosmosCache as Cosmos DB<br/>weather-cache
    participant OWM as OpenWeatherMap API
    participant CosmosHistory as Cosmos DB<br/>search-history

    User->>JS: Types "London" + submits
    JS->>JS: Validate input, show loader
    JS->>Flask: GET /api/weather?city=London

    Flask->>Flask: Sanitize & validate input
    Flask->>CosmosCache: Query city="London" WHERE _ttl valid

    alt Cache HIT
        CosmosCache-->>Flask: Return cached weather JSON
    else Cache MISS
        Flask->>OWM: GET /weather?q=London&appid=KEY
        OWM-->>Flask: Raw weather JSON
        Flask->>Flask: Parse & transform data
        Flask->>CosmosCache: Write item (city, temp, humidity...)\n_ttl = 600
    end

    Flask-->>JS: 200 OK — Structured JSON
    JS->>JS: Hide loader, render weather card
    JS->>CosmosHistory: POST search record\n(userId, city, searchedAt)
    JS-->>User: Weather card displayed
```

---

## Error Flow (Mermaid)

```mermaid
flowchart TD
    A[User submits city] --> B{JS: Input empty?}
    B -- Yes --> C[Show: 'Please enter a city name']
    B -- No --> D[Call Flask API]
    D --> E{Flask: Valid input?}
    E -- No --> F[Return 400 Bad Request]
    E -- Yes --> G{Cosmos DB Cache Hit?}
    G -- Yes --> H[Return cached data]
    G -- No --> I[Call OpenWeatherMap]
    I --> J{OWM: City found?}
    J -- No --> K[Return 404 City Not Found]
    J -- Yes --> L[Parse + Cache + Return 200]
    F --> M[JS renders error message]
    K --> M
    L --> N[JS renders weather card]
    H --> N
```

---

## Azure Cosmos DB Data Model

### Container 1 — `weather-cache`

| Field        | Type   | Description                      |
|---|---|---|
| `id`         | string | City name (unique)               |
| `city`       | string | **Partition Key**                |
| `country`    | string | Country code                     |
| `temp_c`     | float  | Temp in Celsius                  |
| `humidity`   | int    | Humidity %                       |
| `wind_speed` | float  | Wind in km/h                     |
| `condition`  | string | Weather description               |
| `icon`       | string | Icon code                        |
| `cachedAt`   | string | ISO timestamp                    |
| `_ttl`       | int    | `600` (10 min auto-expire)       |

### Container 2 — `search-history`

| Field            | Type   | Description                        |
|---|---|---|
| `id`             | string | UUID                               |
| `userId`         | string | **Partition Key** (high cardinality) |
| `city`           | string | Searched city                      |
| `searchedAt`     | string | ISO timestamp                      |
| `result_summary` | object | Embedded temp + condition          |

---

## Tech Stack Summary

| Layer          | Technology                         |
|---|---|
| Frontend       | HTML5 + CSS3 + Vanilla JavaScript  |
| Backend        | Python + Flask                     |
| External API   | OpenWeatherMap REST API            |
| Database/Cache | Azure Cosmos DB (NoSQL, SQL API)   |
| Auth/Config    | `.env` + `python-dotenv`           |
| Local Dev DB   | Azure Cosmos DB Emulator           |
| Dev Tooling    | VS Code + Cosmos DB Extension      |
