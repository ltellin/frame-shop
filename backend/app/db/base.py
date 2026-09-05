"""Database engine, session factory, and declarative base.

This is the only place that knows how to talk to the database. Domain code never
imports from here.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

_settings = get_settings()

_connect_args = {}
if _settings.database_url.startswith("sqlite"):
    # Allow use across FastAPI's threadpool; fine for a single-process prototype.
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    _settings.database_url,
    echo=_settings.db_echo,
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_session() -> Iterator[Session]:
    """FastAPI dependency: yields a session and always closes it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
