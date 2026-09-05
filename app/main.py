"""
Latex Smart Monitoring - Entry point.
FastAPI app dengan MQTT, REST API, WebSocket, dan dashboard.
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.mqtt_client import mqtt_service
from app.routes import api, views

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ws_connections: List[WebSocket] = []


async def broadcast_to_websockets(data: dict) -> None:
    """Kirim data ke semua WebSocket client."""
    payload = json.dumps(data, default=str)
    for ws in ws_connections[:]:
        try:
            await ws.send_text(payload)
        except Exception:
            pass


def mqtt_to_websocket_callback(data: dict) -> None:
    """Dipanggil dari thread MQTT; schedule broadcast di event loop utama."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(broadcast_to_websockets(data), loop)
    except Exception as e:
        logger.warning("WebSocket broadcast failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    mqtt_service.set_message_callback(mqtt_to_websocket_callback)
    mqtt_service.start()
    logger.info("Application started: %s", settings.APP_NAME)
    yield
    mqtt_service.stop()
    logger.info("Application stopped.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(views.router)
app.include_router(api.router)


@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    logger.debug("WebSocket client connected. Total: %s", len(ws_connections))
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        if websocket in ws_connections:
            ws_connections.remove(websocket)
        logger.debug("WebSocket disconnected. Total: %s", len(ws_connections))
    except Exception as e:
        if websocket in ws_connections:
            ws_connections.remove(websocket)
        logger.warning("WebSocket error: %s", e)
