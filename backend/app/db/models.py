"""SQLAlchemy ORM models.

Table set for the first slice: Customer, Order, Artwork, Design, DesignComponent,
Vendor, Product.

Money is integer cents. Measurements are Numeric(inches). JSON columns map to
JSONB on Postgres later. Statuses are plain strings validated in the domain/
service layer so the vocabulary can evolve without a migration per value.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    JSON,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    # draft = still being built at the counter; open = has accepted work.
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())

    customer: Mapped[Customer] = relationship(back_populates="orders")
    artworks: Mapped[list["Artwork"]] = relationship(back_populates="order")
    designs: Mapped[list["Design"]] = relationship(back_populates="order")


class Artwork(Base):
    __tablename__ = "artwork"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    title: Mapped[str] = mapped_column(String(300), default="Untitled")
    description: Mapped[str | None] = mapped_column(String(2000))
    width_in: Mapped[Decimal] = mapped_column(Numeric(7, 3))
    height_in: Mapped[Decimal] = mapped_column(Numeric(7, 3))
    depth_in: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    notes: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())

    order: Mapped[Order] = relationship(back_populates="artworks")


class Design(Base):
    __tablename__ = "design"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    artwork_id: Mapped[int] = mapped_column(ForeignKey("artwork.id"))
    name: Mapped[str] = mapped_column(String(200), default="Design")
    # draft | held | quoted | accepted | discarded
    status: Mapped[str] = mapped_column(String(20), default="draft")

    # Reserved for future optimistic concurrency and revision lineage.
    version: Mapped[int] = mapped_column(default=1)
    supersedes_id: Mapped[int | None] = mapped_column(ForeignKey("design.id"))

    # Display-only cache of the last computed price. Never authoritative.
    price_breakdown: Mapped[dict | None] = mapped_column(JSON)
    priced_at: Mapped[datetime | None] = mapped_column()
    pricing_profile_id: Mapped[str | None] = mapped_column(String(50))
    pricing_profile_version: Mapped[int | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, server_default=func.now(), onupdate=_utcnow
    )

    order: Mapped[Order] = relationship(back_populates="designs")
    artwork: Mapped[Artwork] = relationship()
    components: Mapped[list["DesignComponent"]] = relationship(
        back_populates="design",
        cascade="all, delete-orphan",
        order_by="DesignComponent.sequence",
    )


class DesignComponent(Base):
    __tablename__ = "design_component"

    id: Mapped[int] = mapped_column(primary_key=True)
    design_id: Mapped[int] = mapped_column(ForeignKey("design.id"))
    kind: Mapped[str] = mapped_column(String(40))
    sequence: Mapped[int] = mapped_column()  # 1 = outermost, contiguous
    layer_role: Mapped[str | None] = mapped_column(String(40))
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("product.id"))
    # Used only where framing genuinely nests (stacked moulding, fillet in a mat).
    parent_component_id: Mapped[int | None] = mapped_column(ForeignKey("design_component.id"))

    design: Mapped[Design] = relationship(back_populates="components")
    product: Mapped["Product | None"] = relationship()


class Vendor(Base):
    __tablename__ = "vendor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    code: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(String(2000))

    products: Mapped[list["Product"]] = relationship(back_populates="vendor")


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (UniqueConstraint("vendor_id", "sku", name="uq_product_vendor_sku"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id"))
    kind: Mapped[str] = mapped_column(String(40), index=True)  # moulding | mat | glazing | ...
    sku: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000), default="")
    unit_cost_cents: Mapped[int] = mapped_column(default=0)
    unit_price_cents: Mapped[int] = mapped_column(default=0)
    # per_linear_ft | per_united_in | per_sqft | each | sheet
    price_uom: Mapped[str] = mapped_column(String(20), default="each")
    available: Mapped[bool] = mapped_column(default=True)
    discontinued: Mapped[bool] = mapped_column(default=False)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)

    vendor: Mapped[Vendor] = relationship(back_populates="products")
