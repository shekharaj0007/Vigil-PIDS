"""Live weather fetch via Open-Meteo (open-source, no API key required)."""

from datetime import datetime, timezone

from app.config import settings
from app.services.http_client import TTLCache, get_client

# Current conditions change slowly; a short cache avoids hammering Open-Meteo
# when operators re-run calibration for the same site.
_weather_cache = TTLCache(ttl_seconds=300, max_items=128)

# WMO Weather interpretation codes (Open-Meteo)
WEATHER_CODE_LABELS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

STORM_CODES = {95, 96, 99, 82}


def weather_label(code: int) -> str:
    return WEATHER_CODE_LABELS.get(code, f"Unknown ({code})")


def is_storm_condition(code: int) -> bool:
    return code in STORM_CODES


async def fetch_live_weather(
    latitude: float,
    longitude: float,
    location_name: str,
) -> dict:
    """Fetch current weather from Open-Meteo API (cached for 5 minutes per site)."""
    cache_key = (round(latitude, 3), round(longitude, 3))
    cached = _weather_cache.get(cache_key)
    if cached is not None:
        return {**cached, "location_name": location_name}

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ]
        ),
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    url = f"{settings.weather_api_base}/forecast"

    response = await get_client().get(url, params=params)
    response.raise_for_status()
    payload = response.json()

    current = payload["current"]
    code = int(current["weather_code"])

    data = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_c": float(current["temperature_2m"]),
        "humidity_pct": float(current["relative_humidity_2m"]),
        "wind_speed_kmh": float(current["wind_speed_10m"]),
        "rainfall_mm": float(current["precipitation"]),
        "weather_code": code,
        "weather_label": weather_label(code),
        "is_storm": is_storm_condition(code),
        "recorded_at": datetime.now(timezone.utc).replace(tzinfo=None),
    }
    _weather_cache.set(cache_key, data)
    return {**data, "location_name": location_name}
