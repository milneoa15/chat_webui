"""Database engine and session utilities."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from backend.app.config import settings

_engine: Engine | None = None


def configure_engine(database_url: str | None = None) -> None:
    """Recreate the SQLAlchemy engine (useful for tests)."""
    global _engine
    url = database_url or settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    _engine = create_engine(url, echo=False, connect_args=connect_args)


def get_engine() -> Engine:
    """Return the configured engine, creating it on first use."""
    global _engine
    if _engine is None:
        configure_engine()
    assert _engine is not None
    return _engine


def init_db() -> None:
    """Create tables if this is the first run (migrations should handle future changes)."""
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a Session per request."""
    with Session(get_engine()) as session:
        yield session
