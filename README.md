# Vigil PIDS — Weather-Based Sensor Calibration Suggestion System

Smart module for the **Vigil Perimeter Intrusion Detection System (PIDS)** that fetches live weather data, analyzes environmental risk, and recommends sensor sensitivity settings so operators can reduce weather-driven false alarms.

## Features

1. **Live weather integration** via [Open-Meteo](https://open-meteo.com/) (open-source, no API key)
2. **Analysis** of wind, rainfall, temperature, humidity, and storm conditions
3. **Calibration recommendations** (High → Very Low sensitivity) with actionable operator steps
4. **Operator dashboard** with live metrics, factor breakdown, analytics, and history
5. **Demo scenarios** for offline/presentation use when weather is calm

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy (async), httpx |
| Frontend | React 18, Vite, Recharts |
| Database | SQLite |
| Weather API | Open-Meteo Forecast API |

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # optional
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://127.0.0.1:5173

### 3. Tests

```bash
cd backend
python -m unittest tests.test_recommender -v
```

## Project structure

```
├── backend/                 # FastAPI service
│   ├── app/
│   │   ├── main.py
│   │   ├── services/        # weather + recommender
│   │   └── routers/api.py
│   ├── tests/
│   └── requirements.txt
├── frontend/                # Operator dashboard
├── docs/                    # Architecture, API, schema, setup
├── sample_data/             # Demo weather scenarios
└── README.md
```

## Recommendation logic (summary)

| Condition | Typical guidance |
|-----------|------------------|
| High wind (≥40 km/h) | Lower sensitivity |
| Normal / calm weather | Higher sensitivity |
| Heavy rain | Medium sensitivity |
| Thunderstorm / violent showers | Very low + dual-sensor confirmation |

Full logic: `docs/ARCHITECTURE.md` and `backend/app/services/recommender.py`.

## Documentation

- [System architecture](docs/ARCHITECTURE.md)
- [API integration](docs/API_INTEGRATION.md)
- [Database schema](docs/DATABASE_SCHEMA.md)
- [Setup instructions](docs/SETUP.md)
- [Presentation outline](docs/PRESENTATION.md)
- [Deploy to Render](docs/DEPLOY_RENDER.md)

## Acknowledgements

- **Open-Meteo** — open-source weather API ([https://open-meteo.com/](https://open-meteo.com/))
- **FastAPI**, **SQLAlchemy**, **React**, **Vite**, **Recharts**

## License

Prototype for academic case study / Launchpad evaluation.
