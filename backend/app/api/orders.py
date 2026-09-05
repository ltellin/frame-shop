from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import OrderCreate
from app.db.base import get_session
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_dict(order) -> dict:
    return {
        "id": order.id,
        "number": order.number,
        "customer_id": order.customer_id,
        "customer_name": order.customer.name,
        "status": order.status,
        "due_date": order.due_date.isoformat() if order.due_date else None,
        "po_number": order.po_number,
        "designs": [
            {
                "id": d.id,
                "name": d.name,
                "type": d.type,
                "status": d.status,
                "art_title": d.art_title,
                "base_width_in": float(d.base_width_in) if d.base_width_in is not None else None,
                "base_height_in": float(d.base_height_in) if d.base_height_in is not None else None,
                "subtotal_cents": (d.price_breakdown or {}).get("subtotal_cents"),
            }
            for d in order.designs
        ],
    }


def _order_summary(order) -> dict:
    return {
        "id": order.id,
        "number": order.number,
        "status": order.status,
        "customer_id": order.customer_id,
        "customer_name": order.customer.name,
        "due_date": order.due_date.isoformat() if order.due_date else None,
        "design_count": len(order.designs),
    }


@router.get("")
def list_orders(session: Session = Depends(get_session)) -> list[dict]:
    return [_order_summary(o) for o in order_service.list_orders(session)]


@router.post("", status_code=201)
def create_order(body: OrderCreate, session: Session = Depends(get_session)) -> dict:
    order = order_service.create_order(
        session, customer_id=body.customer_id, due_date=body.due_date, po_number=body.po_number
    )
    session.commit()
    return _order_dict(order)


@router.get("/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_session)) -> dict:
    return _order_dict(order_service.get_order(session, order_id))
