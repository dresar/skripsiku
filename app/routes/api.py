"""
REST API routes: /api/latest, /api/history, /api/statistics.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import LatexReading
from app.schemas import (
    LatestResponse,
    HistoryResponse,
    StatisticsResponse,
    LatexReadingResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


def db_session():
    """Dependency untuk inject session."""
    yield from get_db_session()


@router.get("/latest", response_model=LatestResponse)
def get_latest(db: Session = Depends(db_session)) -> LatestResponse:
    """Data pembacaan terbaru (satu record)."""
    row = db.query(LatexReading).order_by(LatexReading.created_at.desc()).first()
    if not row:
        from app.schemas import default_latest_response
        return default_latest_response()
    return LatestResponse.model_validate(row)


@router.get("/history", response_model=HistoryResponse)
def get_history(
    db: Session = Depends(db_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
) -> HistoryResponse:
    """Riwayat data dengan pagination dan filter tanggal."""
    q = db.query(LatexReading)
    if date_from:
        q = q.filter(LatexReading.created_at >= date_from)
    if date_to:
        q = q.filter(LatexReading.created_at <= date_to)
    total = q.count()
    q = q.order_by(LatexReading.created_at.desc())
    offset = (page - 1) * per_page
    items = q.offset(offset).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page if total else 1
    return HistoryResponse(
        items=[LatexReadingResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(db_session)) -> StatisticsResponse:
    """Statistik: rata-rata pH, TDS, suhu, total, status counts, status dominan."""
    agg = db.query(
        func.avg(LatexReading.ph).label("avg_ph"),
        func.avg(LatexReading.tds).label("avg_tds"),
        func.avg(LatexReading.suhu).label("avg_suhu"),
        func.count(LatexReading.id).label("total"),
    ).first()

    status_counts = (
        db.query(LatexReading.status, func.count(LatexReading.id))
        .group_by(LatexReading.status)
        .all()
    )
    status_dict = {s: c for s, c in status_counts}
    dominant = max(status_dict, key=status_dict.get) if status_dict else ""

    return StatisticsResponse(
        avg_ph=float(agg.avg_ph or 0),
        avg_tds=float(agg.avg_tds or 0),
        avg_suhu=float(agg.avg_suhu or 0),
        total_readings=int(agg.total or 0),
        status_counts=status_dict,
        dominant_status=dominant,
    )
