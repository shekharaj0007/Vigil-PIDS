# System Architecture

## Overview

The Vigil PIDS weather calibration module is a three-tier prototype:

```
┌─────────────────────┐     HTTP/JSON      ┌──────────────────────┐
│  Operator Dashboard │ ◄────────────────► │  FastAPI Backend     │
│  (React + Vite)     │                    │  /api/calibrate      │
└─────────────────────┘                    │  /api/analytics      │
                                           └──────────┬───────────┘
                                                      │
                         ┌────────────────────────────┼────────────────────────────┐
                         ▼                            ▼                            ▼
               ┌─────────────────┐        ┌──────────────────┐        ┌─────────────────┐
               │ Open-Meteo API  │        │ Recommendation   │        │ SQLite          │
               │ Live weather    │        │ Engine (rules)   │        │ Snapshots +     │
               └─────────────────┘        └──────────────────┘        │ Recommendations │
                                                                      └─────────────────┘
```

## Components

### 1. Weather service (`services/weather.py`)

- Calls Open-Meteo `/v1/forecast` with `current` parameters
- Maps WMO weather codes to human-readable labels
- Flags storm conditions (codes 95, 96, 99, 82)

### 2. Recommendation engine (`services/recommender.py`)

Each environmental factor produces an **impact** in `[0, 1]`:

| Factor | Weight | Rationale for PIDS |
|--------|--------|--------------------|
| Wind | 0.40 | Fence / fiber vibration → false trips |
| Rain | 0.22 | Acoustic & buried sensor noise |
| Storm | 0.23 | Compound severe weather |
| Temperature | 0.08 | Mount / cable expansion |
| Humidity | 0.07 | Condensation / electronics |

**Composite risk** = weighted sum (storm applies a high-risk floor ≥ 0.8).

**Sensitivity score** ≈ `100 × (1 − risk)`, clamped to 15–95.

| Risk band | Sensitivity level |
|-----------|-------------------|
| ≥ 0.75 | Very Low |
| ≥ 0.55 | Low |
| ≥ 0.35 | Medium |
| ≥ 0.18 | Medium-High |
| else | High |

This matches the case-study examples:

- High wind → Lower sensitivity  
- Normal weather → Higher sensitivity  
- Heavy rain → Medium sensitivity  

### 3. Persistence

Every calibration run stores:

1. A `weather_snapshots` row (raw conditions)
2. A `calibration_recommendations` row (level, score, rationale, actions)

Analytics aggregates these rows for the dashboard report panel.

### 4. Operator dashboard

- Site presets (major Indian cities) + custom lat/lon
- Live calibrate action
- Demo scenarios for presentations without waiting for bad weather
- Factor impact bars, action list, risk trend chart, history table

## Security / ops notes (prototype)

- CORS open for local demo
- SQLite file created beside the backend process
- No authentication (add JWT / SSO before production PIDS integration)
