from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import ArtworkCreate, OrderCreate
from app.db.base import get_session
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_dict(order) -> dict:
    return {
        "id": order.id,
        "number": order.number,
        "customer_id": order.customer_id,
        "status": order.status,
        "artworks": [
            {
                "id": a.id,
                "title": a.title,
                "width_in": float(a.width_in),
                "height_in": float(a.height_in),
                "depth_in": float(a.depth_in) if a.depth_in else None,
            }
            for a in order.artworks
        ],
        "design_ids": [d.id for d in order.designs],
    }


@router.post("", status_code=201)
def create_order(body: OrderCreate, session: Session = Depends(get_session)) -> dict:
    order = order_service.create_order(session, customer_id=body.customer_id)
    session.commit()
    return _order_dict(order)


@router.get("/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_session)) -> dict:
    return _order_dict(order_service.get_order(session, order_id))


@router.post("/{order_id}/artworks", status_code=201)
def add_artwork(
    order_id: int, body: ArtworkCreate, session: Session = Depends(get_session)
) -> dict:
    artwork = order_service.add_artwork(
        session,
        order_id=order_id,
        title=body.title,
        width_in=body.width_in,
        height_in=body.height_in,
        depth_in=body.depth_in,
        description=body.description,
        notes=body.notes,
    )
    session.commit()
    return {
        "id": artwork.id,
        "order_id": artwork.order_id,
        "title": artwork.title,
        "width_in": float(artwork.width_in),
        "height_in": float(artwork.height_in),
        "depth_in": float(artwork.depth_in) if artwork.depth_in else None,
    }
