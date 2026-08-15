from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_name: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    temperature_c: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[float] = mapped_column(Float)
    wind_speed_kmh: Mapped[float] = mapped_column(Float)
    rainfall_mm: Mapped[float] = mapped_column(Float)
    weather_code: Mapped[int] = mapped_column(Integer)
    weather_label: Mapped[str] = mapped_column(String(80))
    is_storm: Mapped[int] = mapped_column(Integer, default=0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CalibrationRecommendation(Base):
    __tablename__ = "calibration_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weather_snapshot_id: Mapped[int] = mapped_column(Integer)
    location_name: Mapped[str] = mapped_column(String(120))
    sensitivity_level: Mapped[str] = mapped_column(String(40))
    sensitivity_score: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(Text)
    action_items: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
