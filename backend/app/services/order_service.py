"""Customer / Order use-cases.

An Order groups the pieces (Designs) from one customer transaction. It carries
the customer, an optional due date / PO number, and — later — money. A Design is
attached to an Order via ``design_service.add_to_order``.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Customer, Order
from app.services.errors import NotFoundError

_FIRST_ORDER_NUMBER = 5271  # nod to the brief's example
_OPEN_ORDER_STATUSES = ("draft", "open")


def create_customer(
    session: Session,
    *,
    name: str,
    phone: str | None = None,
    email: str | None = None,
    notes: str | None = None,
    is_trade: bool = False,
) -> Customer:
    customer = Customer(name=name, phone=phone, email=email, notes=notes, is_trade=is_trade)
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


def create_order(
    session: Session, *, customer_id: int, due_date=None, po_number: str | None = None
) -> Order:
    get_customer(session, customer_id)
    order = Order(
        number=_next_order_number(session),
        customer_id=customer_id,
        status="draft",
        due_date=due_date,
        po_number=po_number,
    )
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


def get_or_create_open_order(
    session: Session, *, customer_id: int, due_date=None, po_number: str | None = None
) -> Order:
    """Reuse the customer's most recent still-open order, else start one."""
    existing = session.scalars(
        select(Order)
        .where(Order.customer_id == customer_id, Order.status.in_(_OPEN_ORDER_STATUSES))
        .order_by(Order.number.desc())
    ).first()
    if existing is not None:
        if due_date is not None and existing.due_date is None:
            existing.due_date = due_date
        if po_number and not existing.po_number:
            existing.po_number = po_number
        return existing
    return create_order(session, customer_id=customer_id, due_date=due_date, po_number=po_number)
