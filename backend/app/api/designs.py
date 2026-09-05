from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import DesignPatch, DesignStart
from app.db.base import get_session
from app.services import design_service

router = APIRouter(prefix="/designs", tags=["designs"])


@router.get("")
def list_designs(order_id: int | None = None, session: Session = Depends(get_session)) -> list[dict]:
    designs = design_service.list_designs(session, order_id=order_id)
    return [
        {
            "id": d.id,
            "name": d.name,
            "status": d.status,
            "order_id": d.order_id,
            "artwork_title": d.artwork.title,
            "width_in": float(d.artwork.width_in),
            "height_in": float(d.artwork.height_in),
            "subtotal_cents": (d.price_breakdown or {}).get("subtotal_cents"),
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in designs
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
