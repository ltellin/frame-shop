from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import AddToOrder, DesignPatch, DesignStart
from app.db.base import get_session
from app.services import design_service

router = APIRouter(prefix="/designs", tags=["designs"])


def _list_dict(d) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "type": d.type,
        "status": d.status,
        "order_id": d.order_id,
        "customer_name": d.customer.name if d.customer else None,
        "base_ref": d.base_ref,
        "base_width_in": float(d.base_width_in) if d.base_width_in is not None else None,
        "base_height_in": float(d.base_height_in) if d.base_height_in is not None else None,
        "subtotal_cents": (d.price_breakdown or {}).get("subtotal_cents"),
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


@router.get("")
def list_designs(
    order_id: int | None = None,
    loose: bool = False,
    session: Session = Depends(get_session),
) -> list[dict]:
    return [
        _list_dict(d) for d in design_service.list_designs(session, order_id=order_id, loose=loose)
    ]


@router.post("", status_code=201)
def start_design(body: DesignStart, session: Session = Depends(get_session)) -> dict:
    design = design_service.start_design(session, body.model_dump(exclude_none=True))
    session.commit()
    return design_service.to_read_model(session, design)


@router.get("/{design_id}")
def get_design(design_id: int, session: Session = Depends(get_session)) -> dict:
    design = design_service.get_design(session, design_id)
    return design_service.to_read_model(session, design)


@router.patch("/{design_id}")
def patch_design(
    design_id: int, body: DesignPatch, session: Session = Depends(get_session)
) -> dict:
    design = design_service.get_design(session, design_id)
    design_service.update_design(session, design, body.model_dump(exclude_unset=True))
    session.commit()
    return design_service.to_read_model(session, design)


@router.post("/{design_id}/add-to-order")
def add_to_order(design_id: int, body: AddToOrder, session: Session = Depends(get_session)) -> dict:
    design = design_service.get_design(session, design_id)
    order = design_service.add_to_order(
        session,
        design,
        order_id=body.order_id,
        customer_id=body.customer_id,
        customer=body.customer.model_dump() if body.customer else None,
        due_date=body.due_date,
        po_number=body.po_number,
    )
    session.commit()
    return {
        "order_id": order.id,
        "order_number": order.number,
        "design": design_service.to_read_model(session, design),
    }
