"""Customer / Order / Artwork use-cases.

Minimal for the first slice. The Order exists so that multiple pieces from one
visit group correctly later; for now it is a lightweight container created on
demand.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Artwork, Customer, Order
from app.domain.measure import parse_inches
from app.services.errors import NotFoundError

_FIRST_ORDER_NUMBER = 5271  # nod to the brief's example


def create_customer(
    session: Session,
    *,
    name: str,
    phone: str | None = None,
    email: str | None = None,
    notes: str | None = None,
) -> Customer:
    customer = Customer(name=name, phone=phone, email=email, notes=notes)
    session.add(customer)
    session.flush()
    return customer


def list_customers(session: Session) -> list[Customer]:
    return list(session.scalars(select(Customer).order_by(Customer.name)))


def get_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError(f"customer {customer_id} not found")
    return customer


def _next_order_number(session: Session) -> int:
    current = session.scalar(select(func.max(Order.number)))
    return _FIRST_ORDER_NUMBER if current is None else current + 1


def create_order(session: Session, *, customer_id: int) -> Order:
    get_customer(session, customer_id)
    order = Order(number=_next_order_number(session), customer_id=customer_id, status="draft")
    session.add(order)
    session.flush()
    return order


def get_order(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise NotFoundError(f"order {order_id} not found")
    return order


def list_orders(session: Session) -> list[Order]:
    return list(session.scalars(select(Order).order_by(Order.number.desc())))


def get_or_create_draft_order(session: Session, *, customer_id: int) -> Order:
    existing = session.scalars(
        select(Order)
        .where(Order.customer_id == customer_id, Order.status == "draft")
        .order_by(Order.number.desc())
    ).first()
    return existing or create_order(session, customer_id=customer_id)


def add_artwork(
    session: Session,
    *,
    order_id: int,
    title: str,
    width_in,
    height_in,
    depth_in=None,
    description: str | None = None,
    notes: str | None = None,
) -> Artwork:
    get_order(session, order_id)
    artwork = Artwork(
        order_id=order_id,
        title=title or "Untitled",
        description=description,
        width_in=parse_inches(width_in),
        height_in=parse_inches(height_in),
        depth_in=_opt_inches(depth_in),
        notes=notes,
    )
    session.add(artwork)
    session.flush()
    return artwork


def update_artwork(session: Session, artwork: Artwork, patch: dict) -> Artwork:
    if "title" in patch and patch["title"] is not None:
        artwork.title = patch["title"]
    if "description" in patch:
        artwork.description = patch["description"]
    if "notes" in patch:
        artwork.notes = patch["notes"]
    if patch.get("width_in") is not None:
        artwork.width_in = parse_inches(patch["width_in"])
    if patch.get("height_in") is not None:
        artwork.height_in = parse_inches(patch["height_in"])
    if "depth_in" in patch:
        artwork.depth_in = _opt_inches(patch["depth_in"])
    session.flush()
    return artwork


def _opt_inches(value) -> Decimal | None:
    return None if value is None or value == "" else parse_inches(value)
