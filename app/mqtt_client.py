"""
MQTT Client: subscribe topic, validasi payload, simpan ke DB.
Auto-reconnect, async-safe (callback di thread terpisah), logging.
"""
import json
import logging
import threading
import time
from typing import Callable, Optional

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.config import settings
from app.database import get_db
from app.models import LatexReading
from app.schemas import LatexPayload

logger = logging.getLogger(__name__)


class MQTTService:
    """Service MQTT dengan auto-reconnect dan integrasi database."""

    def __init__(self) -> None:
        self._client: Optional[mqtt.Client] = None
        self._running = False
        self._reconnect_delay = 5
        self._lock = threading.Lock()
        self._on_message_callback: Optional[Callable[[dict], None]] = None

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int) -> None:
        if rc == 0:
            logger.info("MQTT connected to %s:%s", settings.MQTT_BROKER, settings.MQTT_PORT)
            client.subscribe(settings.MQTT_TOPIC, qos=1)
            logger.info("Subscribed to topic: %s", settings.MQTT_TOPIC)
        else:
            logger.warning("MQTT connect failed, rc=%s", rc)

    def _on_disconnect(self, client: mqtt.Client, userdata, rc: int) -> None:
        logger.warning("MQTT disconnected (rc=%s). Will reconnect.", rc)

    def _on_message(self, client: mqtt.Client, userdata, msg) -> None:
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("Invalid JSON from MQTT: %s", e)
            return

        try:
            validated = LatexPayload(**data)
        except ValidationError as e:
            logger.error("Payload validation failed: %s", e)
            return

        # Simpan ke database (sync, di thread MQTT)
        try:
            with get_db() as db:
                reading = LatexReading(
                    ph=validated.ph,
                    tds=validated.tds,
                    suhu=validated.suhu,
                    status=validated.status,
                )
                db.add(reading)
                db.flush()
                db.refresh(reading)
            logger.debug("Saved reading id=%s ph=%.2f status=%s", reading.id, reading.ph, reading.status)
        except Exception as e:
            logger.exception("Failed to save reading: %s", e)
            return

        # Optional: callback untuk WebSocket broadcast
        if self._on_message_callback:
            try:
                self._on_message_callback({
                    "id": reading.id,
                    "ph": validated.ph,
                    "tds": validated.tds,
                    "suhu": validated.suhu,
                    "status": validated.status,
                    "created_at": reading.created_at.isoformat() if reading.created_at else None,
                })
            except Exception as e:
                logger.warning("Callback error: %s", e)

    def set_message_callback(self, callback: Callable[[dict], None]) -> None:
        """Set callback dipanggil setiap ada message valid (untuk WebSocket)."""
        with self._lock:
            self._on_message_callback = callback

    def start(self) -> None:
        """Jalankan MQTT client di background thread."""
        with self._lock:
            if self._running:
                logger.warning("MQTT already running")
                return
            self._running = True

        def run() -> None:
            while self._running:
                try:
                    self._client = mqtt.Client(
                        client_id=settings.MQTT_CLIENT_ID,
                        protocol=mqtt.MQTTv311,
                    )
                    if settings.mqtt_has_auth:
                        self._client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
                    if settings.MQTT_USE_TLS:
                        self._client.tls_set()

                    self._client.on_connect = self._on_connect
                    self._client.on_disconnect = self._on_disconnect
                    self._client.on_message = self._on_message

                    self._client.connect(
                        settings.MQTT_BROKER,
                        settings.MQTT_PORT,
                        keepalive=settings.MQTT_KEEPALIVE,
                    )
                    self._client.loop_forever(retry_first_connection=True)
                except Exception as e:
                    logger.exception("MQTT loop error: %s", e)
                if self._running:
                    logger.info("Reconnecting in %s seconds...", self._reconnect_delay)
                    time.sleep(self._reconnect_delay)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        logger.info("MQTT service started (topic=%s)", settings.MQTT_TOPIC)

    def stop(self) -> None:
        """Stop MQTT client."""
        with self._lock:
            self._running = False
        if self._client:
            self._client.disconnect()
            self._client = None
        logger.info("MQTT service stopped")


# Singleton
mqtt_service = MQTTService()
