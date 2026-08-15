# Database Schema

Engine: **SQLite** (file `pids_calibration.db`, created on first backend start).

ORM: SQLAlchemy 2.x async (`sqlite+aiosqlite`).

## ER overview

```
weather_snapshots 1 ──── * calibration_recommendations
        (id)                    (weather_snapshot_id)
```

## Table: `weather_snapshots`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| location_name | VARCHAR(120) | Site label |
| latitude | FLOAT | Degrees |
| longitude | FLOAT | Degrees |
| temperature_c | FLOAT | °C |
| humidity_pct | FLOAT | % |
| wind_speed_kmh | FLOAT | km/h |
| rainfall_mm | FLOAT | mm |
| weather_code | INTEGER | WMO code |
| weather_label | VARCHAR(80) | Human label |
| is_storm | INTEGER | 0/1 |
| recorded_at | DATETIME | UTC snapshot time |

## Table: `calibration_recommendations`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| weather_snapshot_id | INTEGER | FK to snapshot |
| location_name | VARCHAR(120) | Denormalized site |
| sensitivity_level | VARCHAR(40) | High / Medium-High / Medium / Low / Very Low |
| sensitivity_score | INTEGER | 15–95 |
| risk_score | FLOAT | 0–1 |
| rationale | TEXT | Narrative explanation |
| action_items | TEXT | JSON array of strings |
| created_at | DATETIME | Recommendation time |

## Notes

- Schema is created automatically via `Base.metadata.create_all` on startup.
- For production PIDS, migrate to PostgreSQL and add foreign-key constraints + indexes on `created_at` and `location_name`.
