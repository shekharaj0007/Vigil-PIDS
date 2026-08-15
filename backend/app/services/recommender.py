"""
Sensor calibration recommendation engine for Vigil PIDS.

Maps environmental risk factors to perimeter sensor sensitivity so operators
can reduce weather-driven false intrusion alarms.
"""

from __future__ import annotations


def _wind_factor(wind_kmh: float) -> tuple[float, str]:
    """High wind vibrates fences/cables → lower sensitivity."""
    if wind_kmh >= 60:
        return 1.0, "Extreme wind — vibration risk very high"
    if wind_kmh >= 40:
        return 0.95, "Strong wind — significant vibration expected"
    if wind_kmh >= 25:
        return 0.65, "Moderate wind — elevated false-alarm risk"
    if wind_kmh >= 15:
        return 0.35, "Light breeze — minor vibration possible"
    return 0.05, "Calm wind — vibration risk low"


def _rain_factor(rain_mm: float) -> tuple[float, str]:
    """Heavy rain affects acoustic/fiber and ground sensors."""
    if rain_mm >= 10:
        return 0.9, "Heavy rainfall — high acoustic/ground noise"
    if rain_mm >= 4:
        return 0.65, "Moderate rain — medium environmental noise"
    if rain_mm >= 1:
        return 0.35, "Light rain — slight noise increase"
    if rain_mm > 0:
        return 0.15, "Trace precipitation"
    return 0.0, "No rainfall"


def _temp_factor(temp_c: float) -> tuple[float, str]:
    """Temperature extremes expand/contract sensor mounts and cables."""
    if temp_c >= 42 or temp_c <= -5:
        return 0.7, "Extreme temperature — material stress likely"
    if temp_c >= 35 or temp_c <= 5:
        return 0.4, "Elevated temperature stress"
    return 0.05, "Temperature within normal operating band"


def _humidity_factor(humidity: float) -> tuple[float, str]:
    """Very high humidity can affect electronics and condensation."""
    if humidity >= 90:
        return 0.55, "Very high humidity — condensation risk"
    if humidity >= 75:
        return 0.3, "Elevated humidity"
    return 0.05, "Humidity acceptable"


def _storm_factor(is_storm: bool, weather_label: str) -> tuple[float, str]:
    if is_storm:
        return 1.0, f"Storm condition detected ({weather_label})"
    if "Thunder" in weather_label or "hail" in weather_label.lower():
        return 0.95, f"Severe weather ({weather_label})"
    return 0.0, "No storm activity"


def _score_to_sensitivity(risk: float) -> tuple[str, int]:
    """
    Map composite risk [0–1] to sensitivity level and 0–100 score.
    Higher score = more sensitive sensors.
    """
    sensitivity = int(round(100 * (1.0 - risk)))
    sensitivity = max(15, min(95, sensitivity))

    if risk >= 0.75:
        return "Very Low", sensitivity
    if risk >= 0.55:
        return "Low", sensitivity
    if risk >= 0.35:
        return "Medium", sensitivity
    if risk >= 0.18:
        return "Medium-High", sensitivity
    return "High", sensitivity


def generate_recommendation(weather: dict) -> dict:
    wind_w, wind_msg = _wind_factor(weather["wind_speed_kmh"])
    rain_w, rain_msg = _rain_factor(weather["rainfall_mm"])
    temp_w, temp_msg = _temp_factor(weather["temperature_c"])
    hum_w, hum_msg = _humidity_factor(weather["humidity_pct"])
    storm_w, storm_msg = _storm_factor(weather["is_storm"], weather["weather_label"])

    # Weighted composite risk (storm and wind dominate false alarms)
    weights = {
        "wind": 0.40,
        "rain": 0.22,
        "storm": 0.23,
        "temperature": 0.08,
        "humidity": 0.07,
    }
    factors = {
        "wind": wind_w,
        "rain": rain_w,
        "storm": storm_w,
        "temperature": temp_w,
        "humidity": hum_w,
    }
    risk = sum(factors[k] * weights[k] for k in weights)
    # Storm override: force high risk floor
    if storm_w >= 0.95:
        risk = max(risk, 0.8)

    risk = min(1.0, round(risk, 3))
    level, score = _score_to_sensitivity(risk)

    messages = [wind_msg, rain_msg, temp_msg, hum_msg, storm_msg]
    rationale = (
        f"Based on live conditions at {weather['location_name']}: "
        f"wind {weather['wind_speed_kmh']:.1f} km/h, "
        f"rain {weather['rainfall_mm']:.1f} mm, "
        f"temp {weather['temperature_c']:.1f}°C, "
        f"humidity {weather['humidity_pct']:.0f}%, "
        f"sky '{weather['weather_label']}'. "
        f"Composite environmental risk is {risk:.0%}. "
        f"Recommended sensor sensitivity: {level} ({score}/100)."
    )

    actions: list[str] = []
    if level in ("Very Low", "Low"):
        actions.append("Reduce fence / fiber / vibration sensor sensitivity immediately.")
        actions.append("Increase operator verification threshold before dispatching response.")
        actions.append("Log weather-related alarm suppression for post-event review.")
    elif level == "Medium":
        actions.append("Apply medium sensitivity profile across perimeter zones.")
        actions.append("Monitor high-exposure zones (open stretches, gates) more closely.")
    else:
        actions.append("Restore high-sensitivity detection for maximum intrusion coverage.")
        actions.append("Clear any temporary weather-based sensitivity overrides.")

    if weather["is_storm"]:
        actions.append("Enable storm mode: dual-sensor confirmation required for alarms.")
    if weather["wind_speed_kmh"] >= 40:
        actions.append("Prioritize windward fence lines for manual CCTV correlation.")
    if weather["rainfall_mm"] >= 4:
        actions.append("Expect elevated ground / buried sensor noise; prefer video verification.")

    breakdown = {
        "wind": {"impact": wind_w, "weight": weights["wind"], "note": wind_msg},
        "rain": {"impact": rain_w, "weight": weights["rain"], "note": rain_msg},
        "storm": {"impact": storm_w, "weight": weights["storm"], "note": storm_msg},
        "temperature": {
            "impact": temp_w,
            "weight": weights["temperature"],
            "note": temp_msg,
        },
        "humidity": {
            "impact": hum_w,
            "weight": weights["humidity"],
            "note": hum_msg,
        },
    }

    return {
        "sensitivity_level": level,
        "sensitivity_score": score,
        "risk_score": risk,
        "rationale": rationale,
        "action_items": actions,
        "factor_breakdown": breakdown,
        "_messages": messages,
    }
