import unittest
from datetime import datetime

from app.services.recommender import generate_recommendation


def base_weather(**overrides):
    data = {
        "location_name": "Test Site",
        "latitude": 28.6,
        "longitude": 77.2,
        "temperature_c": 28,
        "humidity_pct": 50,
        "wind_speed_kmh": 10,
        "rainfall_mm": 0,
        "weather_code": 0,
        "weather_label": "Clear sky",
        "is_storm": False,
        "recorded_at": datetime.utcnow(),
    }
    data.update(overrides)
    return data


class RecommenderTests(unittest.TestCase):
    def test_calm_weather_high_sensitivity(self):
        rec = generate_recommendation(base_weather())
        self.assertIn(rec["sensitivity_level"], ("High", "Medium-High"))
        self.assertGreaterEqual(rec["sensitivity_score"], 70)

    def test_high_wind_lowers_sensitivity(self):
        rec = generate_recommendation(base_weather(wind_speed_kmh=50))
        self.assertIn(rec["sensitivity_level"], ("Low", "Medium", "Very Low"))
        self.assertLess(rec["sensitivity_score"], 70)

    def test_storm_forces_very_low(self):
        rec = generate_recommendation(
            base_weather(
                wind_speed_kmh=55,
                rainfall_mm=12,
                humidity_pct=95,
                is_storm=True,
                weather_label="Thunderstorm",
                weather_code=95,
            )
        )
        self.assertEqual(rec["sensitivity_level"], "Very Low")
        self.assertGreaterEqual(rec["risk_score"], 0.75)

    def test_heavy_rain_medium_band(self):
        rec = generate_recommendation(base_weather(rainfall_mm=8, humidity_pct=85))
        self.assertIn(rec["sensitivity_level"], ("Medium", "Medium-High", "Low"))


if __name__ == "__main__":
    unittest.main()
