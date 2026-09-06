"""SQLAlchemy ORM models.

Tables: Customer, Order, Design, DesignComponent, DesignImage, Vendor, Product.

A Design is the universal fabrication spec (art framing, mat-only, glass-only,
assembled frame, swap, repair, ...). Artwork is optional and its fields live on
the Design (there is no Artwork table). A Design may be a loose draft with no
Order and no Customer.

Money is integer cents. Measurements are Numeric(inches). JSON columns map to
JSONB on Postgres later. Statuses / types are plain strings validated in the
domain / service layer so the vocabulary can evolve without a migration per
value.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Date,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(String(2000))
    # A wholesale / B2B customer (another shop). Unrelated to design type "swap".
    is_trade: Mapped[bool] = mapped_column(default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())

    orders: Mapped[list[Order]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    # draft = still being built at the counter; open = has accepted work.
    status: Mapped[str] = mapped_column(String(20), default="draft")
    due_date: Mapped[date | None] = mapped_column(Date)
    po_number: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())

    customer: Mapped[Customer] = relationship(back_populates="orders")
    designs: Mapped[list[Design]] = relationship(back_populates="order")


class Design(Base):
    __tablename__ = "design"

    id: Mapped[int] = mapped_column(primary_key=True)
    # A loose draft has neither.
    order_id: Mapped[int | None] = mapped_column(ForeignKey("order.id"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customer.id"))

    name: Mapped[str] = mapped_column(String(200), default="Design")
    # framing | mat_only | glazing_only | frame_only | canvas_stretch |
    # object_box | swap | repair | other
    type: Mapped[str] = mapped_column(String(30), default="framing", server_default="framing")
    # draft | accepted | discarded
    status: Mapped[str] = mapped_column(String(20), default="draft")

    # The rectangle the component walk is built around, and what it represents:
    # art | sight | glass | rabbet | outside
    base_ref: Mapped[str] = mapped_column(String(20), default="art", server_default="art")
    base_width_in: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    base_height_in: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))

    # Optional artwork metadata (dimensions are base_* above).
    art_title: Mapped[str | None] = mapped_column(String(300))
    art_description: Mapped[str | None] = mapped_column(String(2000))
    # print_photo | canvas | works_on_paper | textile | object_3d
    art_type: Mapped[str | None] = mapped_column(String(30))
    art_depth_in: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    art_notes: Mapped[str | None] = mapped_column(String(2000))

    # Number of identical physical pieces this spec produces (trade batches).
    quantity: Mapped[int] = mapped_column(default=1, server_default="1")

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

    order: Mapped[Order | None] = relationship(back_populates="designs")
    customer: Mapped[Customer | None] = relationship()
    components: Mapped[list[DesignComponent]] = relationship(
        back_populates="design",
        cascade="all, delete-orphan",
        order_by="DesignComponent.sequence",
    )
    images: Mapped[list[DesignImage]] = relationship(
        back_populates="design",
        cascade="all, delete-orphan",
        order_by="DesignImage.created_at",
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
    # shop = the shop provides the material; customer = customer-supplied (a
    # handling fee instead of material cost, distinct visualization).
    provenance: Mapped[str] = mapped_column(String(20), default="shop", server_default="shop")
    # Used only where framing genuinely nests (stacked moulding, fillet in a mat).
    parent_component_id: Mapped[int | None] = mapped_column(ForeignKey("design_component.id"))

    design: Mapped[Design] = relationship(back_populates="components")
    product: Mapped[Product | None] = relationship()


class DesignImage(Base):
    __tablename__ = "design_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    design_id: Mapped[int] = mapped_column(ForeignKey("design.id"))
    # Opaque id used in the URL and as the on-disk filename stem.
    image_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    filename: Mapped[str | None] = mapped_column(String(300))
    content_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    byte_size: Mapped[int] = mapped_column(default=0)
    source: Mapped[str] = mapped_column(String(20), default="upload")  # upload | camera
    is_primary: Mapped[bool] = mapped_column(default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, server_default=func.now())

    design: Mapped[Design] = relationship(back_populates="images")


class Vendor(Base):
    __tablename__ = "vendor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    code: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(String(2000))
    # The shop itself, for mouldings it mills in-house. Its unit_cost_cents is
    # the cost to produce, and its products have no external SKU to reconcile.
    is_house: Mapped[bool] = mapped_column(default=False, server_default="0")

    products: Mapped[list[Product]] = relationship(back_populates="vendor")


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
    # The physical specification, validated per-kind (domain/catalog/product_kinds.py).
    spec: Mapped[dict] = mapped_column(JSON, default=dict)

    vendor: Mapped[Vendor] = relationship(back_populates="products")
