"""
Model ORM untuk database.
Tabel: id, ph, tds, suhu, status, created_at
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime

from app.database import Base


class LatexReading(Base):
    """Model pembacaan mutu lateks dari sensor (pH, TDS, suhu, status)."""

    __tablename__ = "latex_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ph = Column(Float, nullable=False)
    tds = Column(Float, nullable=False)
    suhu = Column(Float, nullable=False)
    status = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<LatexReading(id={self.id}, ph={self.ph}, status={self.status})>"
