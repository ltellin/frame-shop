"""Design use-cases: create, load, edit, (re)price, attach to an order, and build
the read model the API returns.

A Design is the universal fabrication spec. It may be a loose draft (no order, no
customer). It is only priced / rendered once it has real base dimensions — until
then the read model reports ``complete: false``.

All framing/pricing behaviour is delegated to the domain layer. This module only
orchestrates: DB rows in, domain calls, DB rows + read model out.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Design, DesignComponent
from app.domain.design.kinds import DESIGN_TYPES, get_kind, starter_stack
from app.domain.design.representations import to_exploded_layout, to_outside_in_list
from app.domain.design.spec import ArtworkSpec, ComponentSpec, DesignSpec
from app.domain.measure import parse_inches
from app.domain.pricing.engine import price_design
from app.services import catalog_service, order_service
from app.services.errors import DomainValidationError, NotFoundError

EDITABLE_STATUSES = {"draft"}
ALL_STATUSES = {"draft", "accepted", "discarded"}

_ART_FIELDS = ("art_title", "art_description", "art_type", "art_notes")


# --- create / load --------------------------------------------------------


def start_design(session: Session, payload: dict) -> Design:
    """Create a draft design. Everything is optional — a loose draft with just a
    type is valid; components/price/representations appear once base dimensions
    are set."""
    design_type = payload.get("type") or "framing"
    if design_type not in DESIGN_TYPES:
        raise DomainValidationError(f"unknown design type: {design_type!r}")

    design = Design(
        name=payload.get("name") or "Design",
        type=design_type,
        status="draft",
        base_ref=payload.get("base_ref") or DESIGN_TYPES[design_type]["base_ref"],
        quantity=int(payload.get("quantity") or 1),
    )

    customer_id = payload.get("customer_id")
    if customer_id is not None:
        order_service.get_customer(session, customer_id)
        design.customer_id = customer_id

    order_id = payload.get("order_id")
    if order_id is not None:
        design.order_id = order_service.get_order(session, order_id).id

    _apply_base(design, payload)
    _apply_art(design, payload.get("art") or {})

    session.add(design)
    session.flush()

    components = payload.get("components")
    if components is None and payload.get("seed_starter"):
        components = starter_stack(design_type)
    if components:
        replace_components(session, design, components)

    _reprice_if_complete(session, design)
    return design


def get_design(session: Session, design_id: int) -> Design:
    design = session.get(Design, design_id)
    if design is None:
        raise NotFoundError(f"design {design_id} not found")
    return design


def list_designs(
    session: Session, *, order_id: int | None = None, loose: bool | None = None
) -> list[Design]:
    stmt = select(Design).order_by(Design.updated_at.desc(), Design.id.desc())
    if order_id is not None:
        stmt = stmt.where(Design.order_id == order_id)
    if loose:
        stmt = stmt.where(Design.order_id.is_(None), Design.status == "draft")
    return list(session.scalars(stmt))


# --- editing ------------------------------------------------------------


def _require_editable(design: Design) -> None:
    if design.status not in EDITABLE_STATUSES:
        raise DomainValidationError(f"design {design.id} is {design.status} and cannot be edited")


def update_design(session: Session, design: Design, patch: dict) -> Design:
    if patch.get("status") is not None:
        _set_status(design, patch["status"])

    editing_keys = (
        "name",
        "type",
        "base_ref",
        "base_width_in",
        "base_height_in",
        "art",
        "quantity",
        "customer_id",
        "components",
    )
    if any(k in patch for k in editing_keys):
        _require_editable(design)

    if patch.get("name") is not None:
        design.name = patch["name"]

    if patch.get("type") is not None:
        new_type = patch["type"]
        if new_type not in DESIGN_TYPES:
            raise DomainValidationError(f"unknown design type: {new_type!r}")
        reseed = design.type != new_type and not design.components and "components" not in patch
        design.type = new_type
        if "base_ref" not in patch:
            design.base_ref = DESIGN_TYPES[new_type]["base_ref"]
        if reseed:
            replace_components(session, design, starter_stack(new_type))

    if patch.get("base_ref") is not None:
        design.base_ref = patch["base_ref"]
    if "customer_id" in patch:
        cid = patch["customer_id"]
        if cid is not None:
            order_service.get_customer(session, cid)
        design.customer_id = cid
    if patch.get("quantity") is not None:
        design.quantity = max(1, int(patch["quantity"]))

    _apply_base(design, patch)
    if patch.get("art") is not None:
        _apply_art(design, patch["art"])

    if patch.get("components") is not None:
        replace_components(session, design, patch["components"])

    design.version += 1
    session.flush()
    _reprice_if_complete(session, design)
    return design


def _apply_base(design: Design, src: dict) -> None:
    if "base_width_in" in src:
        design.base_width_in = _opt_inches(src["base_width_in"])
    if "base_height_in" in src:
        design.base_height_in = _opt_inches(src["base_height_in"])


def _apply_art(design: Design, art: dict) -> None:
    for field in _ART_FIELDS:
        key = field.removeprefix("art_")
        if key in art:
            setattr(design, field, art[key] or None)
    if "depth_in" in art:
        design.art_depth_in = _opt_inches(art["depth_in"])


def _set_status(design: Design, new_status: str) -> None:
    if new_status not in ALL_STATUSES:
        raise DomainValidationError(f"unknown status: {new_status!r}")
    if design.status == "accepted" and new_status != "accepted":
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

        provenance = item.get("provenance") or "shop"
        if provenance not in ("shop", "customer"):
            raise DomainValidationError(f"unknown provenance: {provenance!r}")

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
        component.provenance = provenance
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


# --- add to order -----------------------------------------------------


def add_to_order(
    session: Session,
    design: Design,
    *,
    order_id: int | None = None,
    customer_id: int | None = None,
    customer: dict | None = None,
    due_date=None,
    po_number: str | None = None,
) -> object:
    if design.order_id is not None:
        raise DomainValidationError(f"design {design.id} is already on order {design.order_id}")

    if order_id is not None:
        order = order_service.get_order(session, order_id)
    else:
        if customer_id is None:
            customer = customer or {}
            if not customer.get("name"):
                raise DomainValidationError("order_id, customer_id, or customer.name is required")
            customer_id = order_service.create_customer(
                session,
                name=customer["name"],
                phone=customer.get("phone"),
                email=customer.get("email"),
            ).id
        order = order_service.get_or_create_open_order(
            session, customer_id=customer_id, due_date=due_date, po_number=po_number
        )

    design.order_id = order.id
    design.customer_id = order.customer_id
    session.flush()
    return order


# --- pricing / spec --------------------------------------------------


def _is_complete(design: Design) -> bool:
    return design.base_width_in is not None and design.base_height_in is not None


def build_spec(session: Session, design: Design) -> DesignSpec:
    art = None
    if any(getattr(design, f) for f in (*_ART_FIELDS, "art_depth_in")):
        art = ArtworkSpec(
            title=design.art_title,
            art_type=design.art_type,
            depth_in=design.art_depth_in,
            notes=design.art_notes,
        )
    components = tuple(
        ComponentSpec(
            id=c.id,
            kind=c.kind,
            sequence=c.sequence,
            params=c.params or {},
            layer_role=c.layer_role,
            product=catalog_service.resolve(session, c.product_id),
            provenance=c.provenance,
            parent_component_id=c.parent_component_id,
        )
        for c in sorted(design.components, key=lambda c: c.sequence)
    )
    return DesignSpec(
        id=design.id,
        base_width_in=design.base_width_in,
        base_height_in=design.base_height_in,
        base_ref=design.base_ref,
        type=design.type,
        quantity=design.quantity,
        artwork=art,
        components=components,
    )


def _reprice_if_complete(session: Session, design: Design) -> None:
    if not _is_complete(design):
        design.price_breakdown = None
        design.priced_at = None
        session.flush()
        return
    spec = build_spec(session, design)
    breakdown = price_design(spec)
    design.price_breakdown = breakdown.as_dict()
    design.priced_at = datetime.now(UTC)
    design.pricing_profile_id = breakdown.profile_id
    design.pricing_profile_version = breakdown.profile_version
    session.flush()


# --- read model --------------------------------------------------------


def _summary(spec: DesignSpec, exploded: dict) -> dict:
    bounds = exploded["bounds"]
    return {
        "finished_width_in": bounds["width_in"],
        "finished_height_in": bounds["height_in"],
        "base_width_in": float(spec.base_width_in),
        "base_height_in": float(spec.base_height_in),
        "quantity": spec.quantity,
    }


def to_read_model(session: Session, design: Design) -> dict:
    base = {
        "id": design.id,
        "name": design.name,
        "type": design.type,
        "status": design.status,
        "editable": design.status in EDITABLE_STATUSES,
        "version": design.version,
        "order_id": design.order_id,
        "customer_id": design.customer_id,
        "customer_name": design.customer.name if design.customer else None,
        "quantity": design.quantity,
        "base_ref": design.base_ref,
        "base_width_in": float(design.base_width_in) if design.base_width_in is not None else None,
        "base_height_in": float(design.base_height_in)
        if design.base_height_in is not None
        else None,
        "art": {
            "title": design.art_title,
            "description": design.art_description,
            "art_type": design.art_type,
            "depth_in": float(design.art_depth_in) if design.art_depth_in is not None else None,
            "notes": design.art_notes,
        },
        "updated_at": design.updated_at.isoformat() if design.updated_at else None,
        "images": [image_read_dict(design.id, img) for img in design.images],
        "components": [
            _component_dict(session, c) for c in sorted(design.components, key=lambda c: c.sequence)
        ],
    }

    if not _is_complete(design):
        base.update(complete=False, price=None, representations=None, summary=None, warnings=[])
        return base

    spec = build_spec(session, design)
    breakdown = price_design(spec)
    exploded = to_exploded_layout(spec)
    base.update(
        complete=True,
        price=breakdown.as_dict(),
        representations={"outside_in": to_outside_in_list(spec), "exploded": exploded},
        summary=_summary(spec, exploded),
        warnings=_warnings(spec),
    )
    return base


def _component_dict(session: Session, c: DesignComponent) -> dict:
    resolution = catalog_service.resolve(session, c.product_id)
    return {
        "id": c.id,
        "kind": c.kind,
        "sequence": c.sequence,
        "layer_role": c.layer_role or get_kind(c.kind).default_layer_role,
        "params": c.params or {},
        "product_id": c.product_id,
        "provenance": c.provenance,
        "parent_component_id": c.parent_component_id,
        "product": _product_summary(resolution),
    }


def image_read_dict(design_id: int, img) -> dict:
    return {
        "id": img.id,
        "image_id": img.image_id,
        "url": f"/api/designs/{design_id}/images/{img.image_id}",
        "source": img.source,
        "is_primary": img.is_primary,
        "content_type": img.content_type,
        "created_at": img.created_at.isoformat() if img.created_at else None,
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


def _warnings(spec: DesignSpec) -> list[str]:
    out: list[str] = []
    for comp in spec.components:
        if comp.provenance == "customer" or comp.product is None:
            continue
        if comp.product.discontinued:
            out.append(f"'{comp.product.name}' is discontinued but is used in this design.")
        elif not comp.product.available:
            out.append(f"'{comp.product.name}' is currently unavailable from the vendor.")
    if not spec.components:
        out.append("This design has no components yet.")
    return out


def _opt_inches(value):
    return None if value is None or value == "" else parse_inches(value)
