"""Application settings.

Env-driven so the same code runs against SQLite locally and Postgres later.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRAMESHOP_", env_file=".env", extra="ignore")

    # A SQLAlchemy URL. SQLite for local dev; swap for postgresql+psycopg://... later.
    database_url: str = "sqlite+pysqlite:///./frameshop.db"

    # CORS origins for the Vite dev server.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Echo SQL to the console (debugging only).
    db_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
