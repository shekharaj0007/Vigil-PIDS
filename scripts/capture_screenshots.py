"""Capture Vigil PIDS dashboard screenshots using mocked API responses."""

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:5173"

LIVE_WEATHER = {
    "location_name": "New Delhi, Delhi, India",
    "latitude": 28.6139,
    "longitude": 77.209,
    "temperature_c": 31.2,
    "humidity_pct": 58,
    "wind_speed_kmh": 12.4,
    "rainfall_mm": 0.0,
    "weather_code": 1,
    "weather_label": "Mainly clear",
    "is_storm": False,
    "recorded_at": "2026-08-16T00:00:00",
}

LIVE_REC = {
    "weather": LIVE_WEATHER,
    "recommendation": {
        "sensitivity_level": "High",
        "sensitivity_score": 92,
        "risk_score": 0.08,
        "rationale": "Based on live conditions at New Delhi: wind 12.4 km/h, rain 0.0 mm, temp 31.2°C, humidity 58%, sky 'Mainly clear'. Composite environmental risk is 8%. Recommended sensor sensitivity: High (92/100).",
        "action_items": [
            "Restore high-sensitivity detection for maximum intrusion coverage.",
            "Clear any temporary weather-based sensitivity overrides.",
        ],
        "factor_breakdown": {
            "wind": {"impact": 0.05, "weight": 0.4, "note": "Calm wind"},
            "rain": {"impact": 0.0, "weight": 0.22, "note": "No rainfall"},
            "storm": {"impact": 0.0, "weight": 0.23, "note": "No storm activity"},
            "temperature": {"impact": 0.05, "weight": 0.08, "note": "Normal band"},
            "humidity": {"impact": 0.05, "weight": 0.07, "note": "Acceptable"},
        },
    },
    "snapshot_id": 1,
    "recommendation_id": 1,
}

WIND_REC = {
    "weather": {
        "location_name": "Demo — Windy Fence Line",
        "latitude": 19.07,
        "longitude": 72.87,
        "temperature_c": 31,
        "humidity_pct": 55,
        "wind_speed_kmh": 48,
        "rainfall_mm": 0,
        "weather_code": 3,
        "weather_label": "Overcast",
        "is_storm": False,
        "recorded_at": "2026-08-16T00:00:00",
    },
    "recommendation": {
        "sensitivity_level": "Medium",
        "sensitivity_score": 58,
        "risk_score": 0.42,
        "rationale": "Strong wind detected. Recommended sensor sensitivity: Medium (58/100).",
        "action_items": [
            "Apply medium sensitivity profile across perimeter zones.",
            "Prioritize windward fence lines for manual CCTV correlation.",
        ],
        "factor_breakdown": {
            "wind": {"impact": 0.95, "weight": 0.4, "note": "Strong wind"},
            "rain": {"impact": 0.0, "weight": 0.22, "note": "No rainfall"},
            "storm": {"impact": 0.0, "weight": 0.23, "note": "No storm"},
            "temperature": {"impact": 0.05, "weight": 0.08, "note": "Normal"},
            "humidity": {"impact": 0.05, "weight": 0.07, "note": "OK"},
        },
    },
    "snapshot_id": 2,
    "recommendation_id": 2,
}

STORM_REC = {
    "weather": {
        "location_name": "Demo — Storm Sector",
        "latitude": 22.57,
        "longitude": 88.36,
        "temperature_c": 26,
        "humidity_pct": 92,
        "wind_speed_kmh": 55,
        "rainfall_mm": 12,
        "weather_code": 95,
        "weather_label": "Thunderstorm",
        "is_storm": True,
        "recorded_at": "2026-08-16T00:00:00",
    },
    "recommendation": {
        "sensitivity_level": "Very Low",
        "sensitivity_score": 18,
        "risk_score": 0.85,
        "rationale": "Storm condition detected. Recommended sensor sensitivity: Very Low (18/100).",
        "action_items": [
            "Reduce fence / fiber / vibration sensor sensitivity immediately.",
            "Enable storm mode: dual-sensor confirmation required for alarms.",
            "Expect elevated ground / buried sensor noise; prefer video verification.",
        ],
        "factor_breakdown": {
            "wind": {"impact": 0.95, "weight": 0.4, "note": "Strong wind"},
            "rain": {"impact": 0.9, "weight": 0.22, "note": "Heavy rainfall"},
            "storm": {"impact": 1.0, "weight": 0.23, "note": "Thunderstorm"},
            "temperature": {"impact": 0.05, "weight": 0.08, "note": "Normal"},
            "humidity": {"impact": 0.55, "weight": 0.07, "note": "Very high"},
        },
    },
    "snapshot_id": 3,
    "recommendation_id": 3,
}

ANALYTICS = {
    "total_recommendations": 12,
    "avg_risk_score": 0.31,
    "sensitivity_distribution": {"High": 5, "Medium": 4, "Very Low": 3},
    "storm_events": 3,
    "avg_wind_speed": 22.5,
    "avg_rainfall": 2.1,
    "avg_temperature": 28.4,
    "avg_humidity": 64.0,
    "recent_history": [
        {
            "id": 3,
            "location_name": "Demo — Storm Sector",
            "temperature_c": 26,
            "humidity_pct": 92,
            "wind_speed_kmh": 55,
            "rainfall_mm": 12,
            "weather_label": "Thunderstorm",
            "is_storm": True,
            "sensitivity_level": "Very Low",
            "sensitivity_score": 18,
            "risk_score": 0.85,
            "created_at": "2026-08-16T00:30:00",
        },
        {
            "id": 2,
            "location_name": "Demo — Windy Fence Line",
            "temperature_c": 31,
            "humidity_pct": 55,
            "wind_speed_kmh": 48,
            "rainfall_mm": 0,
            "weather_label": "Overcast",
            "is_storm": False,
            "sensitivity_level": "Medium",
            "sensitivity_score": 58,
            "risk_score": 0.42,
            "created_at": "2026-08-16T00:20:00",
        },
        {
            "id": 1,
            "location_name": "New Delhi, Delhi, India",
            "temperature_c": 31.2,
            "humidity_pct": 58,
            "wind_speed_kmh": 12.4,
            "rainfall_mm": 0,
            "weather_label": "Mainly clear",
            "is_storm": False,
            "sensitivity_level": "High",
            "sensitivity_score": 92,
            "risk_score": 0.08,
            "created_at": "2026-08-16T00:10:00",
        },
    ],
    "risk_trend": [
        {"id": 1, "created_at": "2026-08-16T00:10:00", "risk_score": 0.08, "sensitivity_score": 92, "location_name": "New Delhi"},
        {"id": 2, "created_at": "2026-08-16T00:20:00", "risk_score": 0.42, "sensitivity_score": 58, "location_name": "Windy"},
        {"id": 3, "created_at": "2026-08-16T00:30:00", "risk_score": 0.85, "sensitivity_score": 18, "location_name": "Storm"},
    ],
}

SEARCH = [
    {
        "name": "Agra, Uttar Pradesh, India",
        "display_name": "Agra, Uttar Pradesh, India",
        "latitude": 27.1767,
        "longitude": 78.0081,
    },
    {
        "name": "Agra Cantonment, Uttar Pradesh, India",
        "display_name": "Agra Cantonment, Agra, Uttar Pradesh, India",
        "latitude": 27.15,
        "longitude": 78.0,
    },
]

PRESETS = [
    {"name": "New Delhi", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946},
]


def shot(page, name: str) -> None:
    path = ASSETS / name
    page.screenshot(path=str(path), full_page=True)
    print(f"saved {path.name}")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        state = {"mode": "home"}

        def handle(route, request):
            url = request.url
            method = request.method
            if "/api/health" in url:
                return route.fulfill(json={"status": "ok", "module": "Vigil PIDS Weather Calibration"})
            if "/api/presets" in url:
                return route.fulfill(json=PRESETS)
            if "/api/locations/search" in url:
                return route.fulfill(json=SEARCH)
            if "/api/locations/reverse" in url:
                return route.fulfill(
                    json={
                        "name": "New Delhi, Delhi, India",
                        "display_name": "New Delhi, Delhi, India",
                        "latitude": 28.6139,
                        "longitude": 77.209,
                    }
                )
            if "/api/analytics" in url:
                return route.fulfill(json=ANALYTICS if state["mode"] != "home" else {
                    **ANALYTICS,
                    "total_recommendations": 0,
                    "recent_history": [],
                    "risk_trend": [],
                    "sensitivity_distribution": {},
                })
            if "/api/calibrate/simulate" in url and method == "POST":
                body = request.post_data or ""
                if "Thunderstorm" in body or "95" in body:
                    return route.fulfill(json=STORM_REC)
                if "48" in body or "Windy" in body:
                    return route.fulfill(json=WIND_REC)
                return route.fulfill(json=LIVE_REC)
            if "/api/calibrate" in url and method == "POST":
                return route.fulfill(json=LIVE_REC)
            return route.continue_()

        page.route("**/api/**", handle)
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(1500)

        shot(page, "01-dashboard-home.png")

        page.fill('input[placeholder="City, district, landmark or address"]', "Agra")
        page.get_by_role("button", name="Search").click()
        page.wait_for_timeout(800)
        shot(page, "02-location-search-agra.png")

        page.locator(".location-results button").first.click()
        page.wait_for_timeout(800)
        shot(page, "03-location-selected.png")

        state["mode"] = "live"
        page.get_by_role("button", name="Fetch weather & recommend").click()
        page.wait_for_timeout(1200)
        shot(page, "04-live-weather-recommendation.png")

        page.get_by_role("button", name="High Wind").click()
        page.wait_for_timeout(1200)
        shot(page, "05-high-wind-scenario.png")

        page.get_by_role("button", name="Thunderstorm").click()
        page.wait_for_timeout(1200)
        shot(page, "06-thunderstorm-scenario.png")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        shot(page, "07-analytics-and-history.png")

        browser.close()
        print(f"done -> {ASSETS}")


if __name__ == "__main__":
    main()
