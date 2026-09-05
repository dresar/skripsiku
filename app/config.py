"""
Konfigurasi aplikasi dari environment variables.
Semua nilai dibaca dari .env via python-dotenv.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env dari root project
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    """Settings aplikasi Latex Smart Monitoring."""

    # App
    APP_NAME: str = os.getenv("APP_NAME", "Latex Smart Monitoring")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # MQTT
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "broker.hivemq.com")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_TOPIC: str = os.getenv("MQTT_TOPIC", "latex/monitoring")
    MQTT_CLIENT_ID: str = os.getenv("MQTT_CLIENT_ID", "latex-backend-01")
    MQTT_KEEPALIVE: int = int(os.getenv("MQTT_KEEPALIVE", "60"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "")
    MQTT_USE_TLS: bool = os.getenv("MQTT_USE_TLS", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./monitoring.db",
    )

    @property
    def mqtt_has_auth(self) -> bool:
        return bool(self.MQTT_USERNAME and self.MQTT_PASSWORD)


settings = Settings()
