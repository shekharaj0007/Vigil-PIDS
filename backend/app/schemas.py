from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LocationQuery(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: Optional[str] = "Custom Location"


class WeatherData(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    rainfall_mm: float
    weather_code: int
    weather_label: str
    is_storm: bool
    recorded_at: datetime


class RecommendationResult(BaseModel):
    sensitivity_level: str
    sensitivity_score: int
    risk_score: float
    rationale: str
    action_items: list[str]
    factor_breakdown: dict[str, dict]


class CalibrationResponse(BaseModel):
    weather: WeatherData
    recommendation: RecommendationResult
    snapshot_id: int
    recommendation_id: int


class HistoryItem(BaseModel):
    id: int
    location_name: str
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    rainfall_mm: float
    weather_label: str
    is_storm: bool
    sensitivity_level: str
    sensitivity_score: int
    risk_score: float
    created_at: datetime


class AnalyticsSummary(BaseModel):
    total_recommendations: int
    avg_risk_score: float
    sensitivity_distribution: dict[str, int]
    storm_events: int
    avg_wind_speed: float
    avg_rainfall: float
    avg_temperature: float
    avg_humidity: float
    recent_history: list[HistoryItem]
    risk_trend: list[dict]
