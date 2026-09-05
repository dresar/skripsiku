"""
Database connection dan session management.
SQLAlchemy async-ready, auto create tables.
"""
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from app.config import settings

logger = logging.getLogger(__name__)

# Engine (sync untuk SQLite; async bisa ditambah nanti dengan asyncpg)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Buat semua tabel jika belum ada (migration-ready)."""
    from app.models import LatexReading  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager untuk session database (digunakan MQTT dll)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """Generator untuk FastAPI Depends()."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
