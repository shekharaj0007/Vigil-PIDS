# API Integration Documentation

## External weather API — Open-Meteo

| Property | Value |
|----------|-------|
| Provider | Open-Meteo |
| Base URL | `https://api.open-meteo.com/v1` |
| Auth | None (open-source / free for non-commercial) |
| Docs | https://open-meteo.com/en/docs |

### Request used by this project

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}
  &longitude={lon}
  &current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m
  &wind_speed_unit=kmh
  &timezone=auto
```

### Field mapping

| Open-Meteo field | Internal field | Unit |
|------------------|----------------|------|
| temperature_2m | temperature_c | °C |
| relative_humidity_2m | humidity_pct | % |
| precipitation | rainfall_mm | mm |
| wind_speed_10m | wind_speed_kmh | km/h |
| weather_code | weather_code / weather_label / is_storm | WMO code |

Storm detection uses WMO codes: **95, 96, 99** (thunderstorms) and **82** (violent rain showers).

### Acknowledgement

Weather data © Open-Meteo.com — please credit Open-Meteo in academic submissions.

---

## Internal REST API (this module)

Base URL (local): `http://127.0.0.1:8000`

Interactive Swagger UI: `/docs`

### `GET /api/health`

Health check.

### `GET /api/presets`

Returns preset site coordinates for the dashboard.

### `GET /api/weather/live`

Query params: `latitude`, `longitude`, `location_name` (optional).

Returns current weather only (no recommendation, no DB write).

### `POST /api/calibrate`

Body:

```json
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "location_name": "New Delhi"
}
```

Fetches live weather, generates recommendation, persists both, returns:

```json
{
  "weather": { "...": "..." },
  "recommendation": {
    "sensitivity_level": "Medium",
    "sensitivity_score": 62,
    "risk_score": 0.38,
    "rationale": "...",
    "action_items": ["..."],
    "factor_breakdown": { "wind": { "impact": 0.55, "weight": 0.35, "note": "..." } }
  },
  "snapshot_id": 1,
  "recommendation_id": 1
}
```

### `POST /api/calibrate/simulate`

Accepts a full weather payload (see `sample_data/weather_scenarios.json`) for offline demos.

### `GET /api/analytics?limit=30`

Aggregated stats, sensitivity distribution, risk trend, recent history.

### `GET /api/history?limit=50`

Recent recommendation history rows.
