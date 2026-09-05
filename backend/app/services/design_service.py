"""Design use-cases: create, load, edit components, (re)price, and build the
read model the API returns.

All framing/pricing behaviour is delegated to the domain layer. This module only
orchestrates: DB rows in, domain calls, DB rows + read model out.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artwork, Design, DesignComponent
from app.domain.design.kinds import get_kind
from app.domain.design.representations import to_exploded_layout, to_outside_in_list
from app.domain.design.spec import ArtworkSpec, ComponentSpec, DesignSpec
from app.domain.pricing.engine import price_design
from app.services import catalog_service, order_service
from app.services.errors import DomainValidationError, NotFoundError

EDITABLE_STATUSES = {"draft", "held", "quoted"}
ALL_STATUSES = {"draft", "held", "quoted", "accepted", "discarded"}


# --- create / load --------------------------------------------------------


def start_design(session: Session, payload: dict) -> Design:
    """Convenience entry point for the counter: resolve/creates customer ->
    order -> artwork -> design in one call."""
    customer_id = payload.get("customer_id")
    if customer_id is None:
        cust = payload.get("customer") or {}
        if not cust.get("name"):
            raise DomainValidationError("customer_id or customer.name is required")
        customer = order_service.create_customer(
            session, name=cust["name"], phone=cust.get("phone"), email=cust.get("email")
        )
        customer_id = customer.id
    else:
        order_service.get_customer(session, customer_id)

    order_id = payload.get("order_id")
    if order_id is None:
        order = order_service.get_or_create_draft_order(session, customer_id=customer_id)
        order_id = order.id
    else:
        order_service.get_order(session, order_id)

    art = payload.get("artwork") or {}
    artwork_id = payload.get("artwork_id")
    if artwork_id is None:
        if art.get("width_in") is None or art.get("height_in") is None:
            raise DomainValidationError("artwork.width_in and artwork.height_in are required")
        artwork = order_service.add_artwork(
            session,
            order_id=order_id,
            title=art.get("title") or "Untitled",
            width_in=art["width_in"],
            height_in=art["height_in"],
            depth_in=art.get("depth_in"),
            description=art.get("description"),
            notes=art.get("notes"),
        )
        artwork_id = artwork.id
    else:
        if session.get(Artwork, artwork_id) is None:
            raise NotFoundError(f"artwork {artwork_id} not found")

    design = Design(
        order_id=order_id,
        artwork_id=artwork_id,
        name=payload.get("name") or "Design",
        status="draft",
    )
    session.add(design)
    session.flush()

    if payload.get("components"):
        replace_components(session, design, payload["components"])
    recompute_price(session, design)
    return design


def get_design(session: Session, design_id: int) -> Design:
    design = session.get(Design, design_id)
    if design is None:
        raise NotFoundError(f"design {design_id} not found")
    return design


def list_designs(session: Session, *, order_id: int | None = None) -> list[Design]:
    stmt = select(Design).order_by(Design.id.desc())
    if order_id is not None:
        stmt = stmt.where(Design.order_id == order_id)
    return list(session.scalars(stmt))


# --- editing ------------------------------------------------------------


def _require_editable(design: Design) -> None:
    if design.status not in EDITABLE_STATUSES:
        raise DomainValidationError(
            f"design {design.id} is {design.status} and cannot be edited"
        )


def update_design(session: Session, design: Design, patch: dict) -> Design:
    if "status" in patch and patch["status"] is not None:
        _set_status(design, patch["status"])

    if any(k in patch for k in ("name", "artwork", "components")):
        _require_editable(design)

    if patch.get("name") is not None:
        design.name = patch["name"]

    if patch.get("artwork") is not None:
        order_service.update_artwork(session, design.artwork, patch["artwork"])

    if patch.get("components") is not None:
        replace_components(session, design, patch["components"])

    design.version += 1
    session.flush()
    recompute_price(session, design)
    return design


def _set_status(design: Design, new_status: str) -> None:
    if new_status not in ALL_STATUSES:
        raise DomainValidationError(f"unknown status: {new_status!r}")
    if design.status in ("accepted",) and new_status != "accepted":
        raise DomainValidationError("an accepted design is locked")
    design.status = new_status


def replace_components(session: Session, design: Design, items: list[dict]) -> None:
    """Replace the whole component list from the desired end-state.

    Array order defines ``sequence`` (1 = outermost). Items with a known ``id``
    are updated in place; others are created; omitted ids are deleted.
    """
    existing: dict[int, DesignComponent] = {c.id: c for c in design.components}
    seen_ids: set[int] = set()
    ordered: list[DesignComponent] = []

    for position, item in enumerate(items, start=1):
        kind_key = item.get("kind")
        try:
            kind = get_kind(kind_key)
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from None

        try:
            params = kind.parse_params(item.get("params")).model_dump(mode="json")
        except Exception as exc:  # pydantic ValidationError
            raise DomainValidationError(f"invalid params for {kind_key}: {exc}") from None

        product_id = item.get("product_id")
        if product_id is not None and catalog_service.get_product(session, product_id) is None:
            raise DomainValidationError(f"product {product_id} not found")

        comp_id = item.get("id")
        component = existing.get(comp_id) if comp_id is not None else None
        if component is None:
            component = DesignComponent(design_id=design.id)
            design.components.append(component)
        else:
            seen_ids.add(component.id)

        component.kind = kind_key
        component.sequence = position
        component.layer_role = item.get("layer_role")
        component.params = params
        component.product_id = product_id
        ordered.append(component)

    for comp_id, component in existing.items():
        if comp_id not in seen_ids:
            design.components.remove(component)

    session.flush()

    # Second pass: optional single parent pointer by array index.
    for position, item in enumerate(items):
        parent_index = item.get("parent_index")
        component = ordered[position]
        if parent_index is None:
            component.parent_component_id = None
            continue
        if not isinstance(parent_index, int) or not (0 <= parent_index < len(ordered)):
            raise DomainValidationError(f"parent_index out of range: {parent_index}")
        if parent_index == position:
            raise DomainValidationError("a component cannot be its own parent")
        component.parent_component_id = ordered[parent_index].id

    session.flush()


# --- pricing ------------------------------------------------------------


def build_spec(session: Session, design: Design) -> DesignSpec:
    artwork = design.artwork
    art_spec = ArtworkSpec(
        title=artwork.title,
        width_in=artwork.width_in,
        height_in=artwork.height_in,
        depth_in=artwork.depth_in,
    )
    components = tuple(
        ComponentSpec(
            id=c.id,
            kind=c.kind,
            sequence=c.sequence,
            params=c.params or {},
            layer_role=c.layer_role,
            product=catalog_service.resolve(session, c.product_id),
            parent_component_id=c.parent_component_id,
        )
        for c in sorted(design.components, key=lambda c: c.sequence)
    )
    return DesignSpec(id=design.id, artwork=art_spec, components=components)


def recompute_price(session: Session, design: Design) -> dict:
    spec = build_spec(session, design)
    breakdown = price_design(spec)
    design.price_breakdown = breakdown.as_dict()
    design.priced_at = datetime.now(timezone.utc)
    design.pricing_profile_id = breakdown.profile_id
    design.pricing_profile_version = breakdown.profile_version
    session.flush()
    return design.price_breakdown


# --- read model --------------------------------------------------------


def to_read_model(session: Session, design: Design) -> dict:
    spec = build_spec(session, design)
    breakdown = price_design(spec)

    components = []
    for c in sorted(design.components, key=lambda c: c.sequence):
        resolution = catalog_service.resolve(session, c.product_id)
        components.append(
            {
                "id": c.id,
                "kind": c.kind,
                "sequence": c.sequence,
                "layer_role": c.layer_role or get_kind(c.kind).default_layer_role,
                "params": c.params or {},
                "product_id": c.product_id,
                "parent_component_id": c.parent_component_id,
                "product": _product_summary(resolution),
            }
        )

    return {
        "id": design.id,
        "order_id": design.order_id,
        "artwork_id": design.artwork_id,
        "name": design.name,
        "status": design.status,
        "version": design.version,
        "editable": design.status in EDITABLE_STATUSES,
        "updated_at": design.updated_at.isoformat() if design.updated_at else None,
        "artwork": {
            "id": design.artwork.id,
            "title": design.artwork.title,
            "description": design.artwork.description,
            "width_in": float(design.artwork.width_in),
            "height_in": float(design.artwork.height_in),
            "depth_in": float(design.artwork.depth_in) if design.artwork.depth_in else None,
            "notes": design.artwork.notes,
        },
        "components": components,
        "price": breakdown.as_dict(),
        "representations": {
            "outside_in": to_outside_in_list(spec),
            "exploded": to_exploded_layout(spec),
        },
        "warnings": _warnings(session, spec),
    }


def _product_summary(resolution) -> dict | None:
    if resolution is None:
        return None
    return {
        "id": resolution.product_id,
        "name": resolution.name,
        "vendor_name": resolution.vendor_name,
        "sku": resolution.sku,
        "price_uom": resolution.price_uom,
        "unit_price_cents": resolution.unit_price_cents,
        "available": resolution.available,
        "discontinued": resolution.discontinued,
    }


def _warnings(session: Session, spec: DesignSpec) -> list[str]:
    out: list[str] = []
    for comp in spec.components:
        if comp.product is None:
            continue
        if comp.product.discontinued:
            out.append(
                f"'{comp.product.name}' is discontinued but is used in this design."
            )
        elif not comp.product.available:
            out.append(f"'{comp.product.name}' is currently unavailable from the vendor.")
    if not spec.components:
        out.append("This design has no components yet.")
    return out
