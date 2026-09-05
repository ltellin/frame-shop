from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.domain.design.kinds import design_type_catalog, kind_catalog
from app.services import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/component-kinds")
def component_kinds() -> list[dict]:
    """Metadata + param schemas for the design editor's 'add component' picker."""
    return kind_catalog()


@router.get("/design-types")
def design_types() -> list[dict]:
    """The design-type list + starter stacks for the 'what are you making?' picker."""
    return design_type_catalog()


@router.get("/vendors")
def vendors(session: Session = Depends(get_session)) -> list[dict]:
    return [
        {"id": v.id, "name": v.name, "code": v.code} for v in catalog_service.list_vendors(session)
    ]


@router.get("/products")
def products(kind: str | None = None, session: Session = Depends(get_session)) -> list[dict]:
    return [
        {
            "id": p.id,
            "kind": p.kind,
            "sku": p.sku,
            "name": p.name,
            "description": p.description,
            "vendor_name": p.vendor.name,
            "unit_price_cents": p.unit_price_cents,
            "unit_cost_cents": p.unit_cost_cents,
            "price_uom": p.price_uom,
            "available": p.available,
            "discontinued": p.discontinued,
        }
        for p in catalog_service.list_products(session, kind=kind)
    ]
