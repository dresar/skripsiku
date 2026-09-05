"""
Pydantic schemas untuk validasi request/response API.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# --- Payload dari MQTT (ESP32) ---
class LatexPayload(BaseModel):
    """Payload JSON dari ESP32 via MQTT."""

    ph: float = Field(..., ge=0, le=14, description="Nilai pH (0-14)")
    tds: float = Field(..., ge=0, description="Nilai TDS (ppm)")
    suhu: float = Field(..., ge=-40, le=85, description="Suhu (°C)")
    status: str = Field(..., min_length=1, max_length=64)

    class Config:
        extra = "forbid"


# --- API Response ---
class LatexReadingBase(BaseModel):
    ph: float
    tds: float
    suhu: float
    status: str


class LatexReadingCreate(LatexReadingBase):
    pass


class LatexReadingResponse(LatexReadingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LatestResponse(LatexReadingResponse):
    """Response untuk GET /api/latest."""

    pass


# Default when no data
def default_latest_response() -> "LatestResponse":
    from datetime import datetime
    return LatestResponse(
        id=0,
        ph=0.0,
        tds=0.0,
        suhu=0.0,
        status="Belum ada data",
        created_at=datetime.utcnow(),
    )


class HistoryResponse(BaseModel):
    """Response untuk GET /api/history (list + pagination)."""

    items: List[LatexReadingResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class StatisticsResponse(BaseModel):
    """Response untuk GET /api/statistics."""

    avg_ph: float
    avg_tds: float
    avg_suhu: float
    total_readings: int
    status_counts: dict
    dominant_status: str
