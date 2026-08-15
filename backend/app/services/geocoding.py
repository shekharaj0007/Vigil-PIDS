"""Forward and reverse geocoding through OpenStreetMap Nominatim."""

from app.services.http_client import TTLCache, get_client

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
HEADERS = {
    "User-Agent": "Vigil-PIDS-Weather-Calibration/1.0 (academic prototype)",
    "Accept-Language": "en",
}

# Place names are static; long cache keeps the UI fast and respects
# Nominatim's usage policy (max 1 request/second).
_reverse_cache = TTLCache(ttl_seconds=86400, max_items=512)
_search_cache = TTLCache(ttl_seconds=86400, max_items=256)


def _short_name(result: dict) -> str:
    address = result.get("address", {})
    place = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or result.get("name")
    )
    state = address.get("state")
    country = address.get("country")
    parts = [part for part in (place, state, country) if part]
    return ", ".join(dict.fromkeys(parts)) or result.get("display_name", "Unknown location")


async def reverse_geocode(latitude: float, longitude: float) -> dict:
    cache_key = (round(latitude, 4), round(longitude, 4))
    cached = _reverse_cache.get(cache_key)
    if cached is not None:
        return cached

    response = await get_client().get(
        f"{NOMINATIM_BASE}/reverse",
        params={"lat": latitude, "lon": longitude, "format": "jsonv2", "zoom": 10},
        headers=HEADERS,
    )
    response.raise_for_status()
    result = response.json()

    data = {
        "name": _short_name(result),
        "display_name": result.get("display_name", ""),
        "latitude": float(result.get("lat", latitude)),
        "longitude": float(result.get("lon", longitude)),
    }
    _reverse_cache.set(cache_key, data)
    return data


async def search_locations(query: str, limit: int = 6) -> list[dict]:
    cache_key = (query.strip().lower(), limit)
    cached = _search_cache.get(cache_key)
    if cached is not None:
        return cached

    response = await get_client().get(
        f"{NOMINATIM_BASE}/search",
        params={
            "q": query,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": limit,
        },
        headers=HEADERS,
    )
    response.raise_for_status()
    results = response.json()

    data = [
        {
            "name": _short_name(result),
            "display_name": result.get("display_name", ""),
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
        }
        for result in results
    ]
    _search_cache.set(cache_key, data)
    return data
