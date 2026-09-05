"""Catalog reads and product resolution.

This is the seam where live vendor catalog data enters the system. Real vendor
imports would land here (a future ``app/catalog/adapters/`` writing Product rows);
everything downstream just sees Product rows and ProductResolution value objects.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Product, Vendor
from app.domain.design.spec import ProductResolution


def list_vendors(session: Session) -> list[Vendor]:
    return list(session.scalars(select(Vendor).order_by(Vendor.name)))


def list_products(session: Session, *, kind: str | None = None) -> list[Product]:
    stmt = select(Product).order_by(Product.kind, Product.name)
    if kind:
        stmt = stmt.where(Product.kind == kind)
    return list(session.scalars(stmt))


def get_product(session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)


def resolve(session: Session, product_id: int | None) -> ProductResolution | None:
    """Resolve a product id against the *live* catalog.

    Draft/held designs always resolve live (so discontinued/unavailable warnings
    are current). An accepted design would instead read its immutable snapshot.
    """
    if product_id is None:
        return None
    product = session.get(Product, product_id)
    if product is None:
        return None
    return ProductResolution(
        product_id=product.id,
        name=product.name,
        description=product.description,
        vendor_name=product.vendor.name,
        sku=product.sku,
        unit_cost_cents=product.unit_cost_cents,
        unit_price_cents=product.unit_price_cents,
        price_uom=product.price_uom,
        available=product.available,
        discontinued=product.discontinued,
    )
