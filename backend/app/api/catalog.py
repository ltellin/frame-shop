from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.domain.catalog.product_kinds import spec_schema_catalog
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


@router.get("/product-kinds")
def product_kinds() -> list[dict]:
    """Per-kind physical-spec JSON schemas (for a future catalog-entry form)."""
    return spec_schema_catalog()


@router.get("/vendors")
def vendors(session: Session = Depends(get_session)) -> list[dict]:
    return [
        {"id": v.id, "name": v.name, "code": v.code, "is_house": v.is_house}
        for v in catalog_service.list_vendors(session)
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
            "vendor_is_house": p.vendor.is_house,
            "unit_price_cents": p.unit_price_cents,
            "unit_cost_cents": p.unit_cost_cents,
            "price_uom": p.price_uom,
            "available": p.available,
            "discontinued": p.discontinued,
            "spec": catalog_service.safe_spec(p.kind, p.spec),
        }
        for p in catalog_service.list_products(session, kind=kind)
    ]
