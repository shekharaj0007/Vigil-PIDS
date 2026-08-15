import json

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import CalibrationRecommendation, WeatherSnapshot
from app.schemas import (
    AnalyticsSummary,
    CalibrationResponse,
    HistoryItem,
    LocationQuery,
    RecommendationResult,
    WeatherData,
)
from app.services.geocoding import reverse_geocode, search_locations
from app.services.recommender import generate_recommendation
from app.services.weather import fetch_live_weather

router = APIRouter(prefix="/api", tags=["calibration"])

PRESETS = [
    {"name": "New Delhi", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
    {"name": "Kolkata", "latitude": 22.5726, "longitude": 88.3639},
    {"name": "Hyderabad", "latitude": 17.3850, "longitude": 78.4867},
]


@router.get("/health")
async def health():
    return {"status": "ok", "module": "Vigil PIDS Weather Calibration"}


@router.get("/presets")
async def location_presets():
    return PRESETS


@router.get("/locations/search")
async def location_search(q: str = Query(..., min_length=2, max_length=150)):
    try:
        return await search_locations(q)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Location search error: {exc}") from exc


@router.get("/locations/reverse")
async def location_reverse(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
):
    try:
        return await reverse_geocode(latitude, longitude)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Location lookup error: {exc}") from exc


@router.get("/weather/live", response_model=WeatherData)
async def live_weather(
    latitude: float = Query(None),
    longitude: float = Query(None),
    location_name: str = Query(None),
):
    lat = latitude if latitude is not None else settings.default_latitude
    lon = longitude if longitude is not None else settings.default_longitude
    name = location_name or settings.default_location_name
    try:
        data = await fetch_live_weather(lat, lon, name)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather API error: {exc}") from exc
    return WeatherData(**data)


@router.post("/calibrate", response_model=CalibrationResponse)
async def calibrate(
    body: LocationQuery | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    lat = body.latitude if body else settings.default_latitude
    lon = body.longitude if body else settings.default_longitude
    name = (body.location_name if body else None) or settings.default_location_name

    try:
        weather = await fetch_live_weather(lat, lon, name)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather API error: {exc}") from exc

    rec = generate_recommendation(weather)

    snapshot = WeatherSnapshot(
        location_name=weather["location_name"],
        latitude=weather["latitude"],
        longitude=weather["longitude"],
        temperature_c=weather["temperature_c"],
        humidity_pct=weather["humidity_pct"],
        wind_speed_kmh=weather["wind_speed_kmh"],
        rainfall_mm=weather["rainfall_mm"],
        weather_code=weather["weather_code"],
        weather_label=weather["weather_label"],
        is_storm=1 if weather["is_storm"] else 0,
        recorded_at=weather["recorded_at"],
    )
    db.add(snapshot)
    await db.flush()

    recommendation = CalibrationRecommendation(
        weather_snapshot_id=snapshot.id,
        location_name=weather["location_name"],
        sensitivity_level=rec["sensitivity_level"],
        sensitivity_score=rec["sensitivity_score"],
        risk_score=rec["risk_score"],
        rationale=rec["rationale"],
        action_items=json.dumps(rec["action_items"]),
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(snapshot)
    await db.refresh(recommendation)

    return CalibrationResponse(
        weather=WeatherData(**weather),
        recommendation=RecommendationResult(
            sensitivity_level=rec["sensitivity_level"],
            sensitivity_score=rec["sensitivity_score"],
            risk_score=rec["risk_score"],
            rationale=rec["rationale"],
            action_items=rec["action_items"],
            factor_breakdown=rec["factor_breakdown"],
        ),
        snapshot_id=snapshot.id,
        recommendation_id=recommendation.id,
    )


@router.post("/calibrate/simulate", response_model=CalibrationResponse)
async def calibrate_simulate(weather: WeatherData, db: AsyncSession = Depends(get_db)):
    """Run recommendation on provided/sample weather (offline demo)."""
    weather_dict = weather.model_dump()
    rec = generate_recommendation(weather_dict)

    snapshot = WeatherSnapshot(
        location_name=weather.location_name,
        latitude=weather.latitude,
        longitude=weather.longitude,
        temperature_c=weather.temperature_c,
        humidity_pct=weather.humidity_pct,
        wind_speed_kmh=weather.wind_speed_kmh,
        rainfall_mm=weather.rainfall_mm,
        weather_code=weather.weather_code,
        weather_label=weather.weather_label,
        is_storm=1 if weather.is_storm else 0,
        recorded_at=weather.recorded_at,
    )
    db.add(snapshot)
    await db.flush()

    recommendation = CalibrationRecommendation(
        weather_snapshot_id=snapshot.id,
        location_name=weather.location_name,
        sensitivity_level=rec["sensitivity_level"],
        sensitivity_score=rec["sensitivity_score"],
        risk_score=rec["risk_score"],
        rationale=rec["rationale"],
        action_items=json.dumps(rec["action_items"]),
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(snapshot)
    await db.refresh(recommendation)

    return CalibrationResponse(
        weather=weather,
        recommendation=RecommendationResult(
            sensitivity_level=rec["sensitivity_level"],
            sensitivity_score=rec["sensitivity_score"],
            risk_score=rec["risk_score"],
            rationale=rec["rationale"],
            action_items=rec["action_items"],
            factor_breakdown=rec["factor_breakdown"],
        ),
        snapshot_id=snapshot.id,
        recommendation_id=recommendation.id,
    )


async def _fetch_history(db: AsyncSession, limit: int) -> list[HistoryItem]:
    """Recent recommendations joined with their weather snapshots (newest first)."""
    rows = await db.execute(
        select(CalibrationRecommendation, WeatherSnapshot)
        .join(WeatherSnapshot, CalibrationRecommendation.weather_snapshot_id == WeatherSnapshot.id)
        .order_by(CalibrationRecommendation.id.desc())
        .limit(limit)
    )
    return [
        HistoryItem(
            id=r.id,
            location_name=r.location_name,
            temperature_c=s.temperature_c,
            humidity_pct=s.humidity_pct,
            wind_speed_kmh=s.wind_speed_kmh,
            rainfall_mm=s.rainfall_mm,
            weather_label=s.weather_label,
            is_storm=bool(s.is_storm),
            sensitivity_level=r.sensitivity_level,
            sensitivity_score=r.sensitivity_score,
            risk_score=r.risk_score,
            created_at=r.created_at,
        )
        for r, s in rows.all()
    ]


@router.get("/analytics", response_model=AnalyticsSummary)
async def analytics(limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    total, avg_risk = (
        await db.execute(
            select(
                func.count(CalibrationRecommendation.id),
                func.avg(CalibrationRecommendation.risk_score),
            )
        )
    ).one()

    if not total:
        return AnalyticsSummary(
            total_recommendations=0,
            avg_risk_score=0.0,
            sensitivity_distribution={},
            storm_events=0,
            avg_wind_speed=0.0,
            avg_rainfall=0.0,
            avg_temperature=0.0,
            avg_humidity=0.0,
            recent_history=[],
            risk_trend=[],
        )

    dist_rows = await db.execute(
        select(CalibrationRecommendation.sensitivity_level, func.count())
        .group_by(CalibrationRecommendation.sensitivity_level)
    )
    dist = dict(dist_rows.all())

    storms, avg_wind, avg_rain, avg_temp, avg_hum = (
        await db.execute(
            select(
                func.sum(WeatherSnapshot.is_storm),
                func.avg(WeatherSnapshot.wind_speed_kmh),
                func.avg(WeatherSnapshot.rainfall_mm),
                func.avg(WeatherSnapshot.temperature_c),
                func.avg(WeatherSnapshot.humidity_pct),
            ).join(
                CalibrationRecommendation,
                CalibrationRecommendation.weather_snapshot_id == WeatherSnapshot.id,
            )
        )
    ).one()

    history = await _fetch_history(db, limit)
    risk_trend = [
        {
            "id": item.id,
            "created_at": item.created_at.isoformat(),
            "risk_score": item.risk_score,
            "sensitivity_score": item.sensitivity_score,
            "location_name": item.location_name,
        }
        for item in reversed(history)
    ]

    return AnalyticsSummary(
        total_recommendations=total,
        avg_risk_score=round(avg_risk or 0.0, 3),
        sensitivity_distribution=dist,
        storm_events=int(storms or 0),
        avg_wind_speed=round(avg_wind or 0.0, 2),
        avg_rainfall=round(avg_rain or 0.0, 2),
        avg_temperature=round(avg_temp or 0.0, 2),
        avg_humidity=round(avg_hum or 0.0, 2),
        recent_history=history,
        risk_trend=risk_trend,
    )


@router.get("/history", response_model=list[HistoryItem])
async def history(limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    return await _fetch_history(db, limit)
