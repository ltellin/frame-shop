from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import base as db_base
from app.db.base import Base
from app.db.models import Product, Vendor
from app.main import create_app


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture()
def SessionFactory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


@pytest.fixture()
def session(SessionFactory):
    s = SessionFactory()
    try:
        yield s
    finally:
        s.rollback()
        s.close()


@pytest.fixture()
def client(engine, SessionFactory, monkeypatch):
    # Point the app's session machinery at the test engine.
    monkeypatch.setattr(db_base, "engine", engine)
    monkeypatch.setattr(db_base, "SessionLocal", SessionFactory)
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def seeded_catalog(session):
    vendor = Vendor(name="Test Vendor", code="TV")
    session.add(vendor)
    session.flush()
    products = {
        "moulding": Product(
            vendor_id=vendor.id,
            kind="moulding",
            sku="M1",
            name="Test Moulding",
            unit_cost_cents=300,
            unit_price_cents=1200,
            price_uom="per_linear_ft",
        ),
        "mat": Product(
            vendor_id=vendor.id,
            kind="mat",
            sku="MAT1",
            name="Test Mat",
            unit_cost_cents=0,
            unit_price_cents=30,
            price_uom="per_united_in",
        ),
        "glazing": Product(
            vendor_id=vendor.id,
            kind="glazing",
            sku="G1",
            name="Test Glass",
            unit_cost_cents=90,
            unit_price_cents=360,
            price_uom="per_sqft",
        ),
        "discontinued": Product(
            vendor_id=vendor.id,
            kind="moulding",
            sku="OLD1",
            name="Old Moulding",
            unit_cost_cents=300,
            unit_price_cents=1000,
            price_uom="per_linear_ft",
            discontinued=True,
        ),
    }
    session.add_all(products.values())
    session.commit()
    return {k: v.id for k, v in products.items()}
