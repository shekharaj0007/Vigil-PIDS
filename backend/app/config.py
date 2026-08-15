from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    default_latitude: float = 28.6139
    default_longitude: float = 77.2090
    default_location_name: str = "New Delhi"
    database_url: str = "sqlite+aiosqlite:///./pids_calibration.db"
    weather_api_base: str = "https://api.open-meteo.com/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
