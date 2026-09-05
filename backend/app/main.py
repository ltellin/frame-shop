"""FastAPI application factory and wiring."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import catalog, customers, designs, health, orders
from app.config import get_settings
from app.services.errors import DomainValidationError, NotFoundError


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Frame Shop API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = "/api"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(catalog.router, prefix=api_prefix)
    app.include_router(customers.router, prefix=api_prefix)
    app.include_router(orders.router, prefix=api_prefix)
    app.include_router(designs.router, prefix=api_prefix)

    @app.exception_handler(NotFoundError)
    async def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DomainValidationError)
    async def _bad_request(_: Request, exc: DomainValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    return app


app = create_app()
