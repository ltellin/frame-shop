from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import CustomerCreate, CustomerRead
from app.db.base import get_session
from app.services import order_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
def list_customers(session: Session = Depends(get_session)) -> list[dict]:
    return [
        {
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "email": c.email,
            "order_count": len(c.orders),
        }
        for c in order_service.list_customers(session)
    ]


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(body: CustomerCreate, session: Session = Depends(get_session)):
    customer = order_service.create_customer(
        session,
        name=body.name,
        phone=body.phone,
        email=body.email,
        notes=body.notes,
        is_trade=body.is_trade,
    )
    session.commit()
    return customer


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, session: Session = Depends(get_session)):
    return order_service.get_customer(session, customer_id)
