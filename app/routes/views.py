"""
View routes: halaman dashboard, history, statistics, settings.
Mengembalikan HTML via Jinja2 templates.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Path ke templates (root project)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["views"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Redirect ke dashboard."""
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "page_title": "Dashboard"},
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "page_title": "Dashboard"},
    )


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse(
        "pages/history.html",
        {"request": request, "page_title": "History Data"},
    )


@router.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request):
    return templates.TemplateResponse(
        "pages/statistics.html",
        {"request": request, "page_title": "Statistik"},
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    from app.config import settings as cfg
    return templates.TemplateResponse(
        "pages/settings.html",
        {
            "request": request,
            "page_title": "Pengaturan Sistem",
            "mqtt_broker": cfg.MQTT_BROKER,
            "mqtt_port": cfg.MQTT_PORT,
            "mqtt_topic": cfg.MQTT_TOPIC,
            "app_name": cfg.APP_NAME,
            "app_version": cfg.APP_VERSION,
        },
    )


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse(
        "pages/about.html",
        {"request": request, "page_title": "Tentang Sistem"},
    )
