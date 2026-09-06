"""The layer walk: turn a DesignSpec into an ordered list of resolved layers.

Both the pricing engine and the representation functions consume this so that
geometry logic lives in exactly one place.
"""

from __future__ import annotations

from decimal import Decimal

from app.domain.design.kinds import get_kind
from app.domain.design.layers import LayerView
from app.domain.design.spec import DesignSpec


def walk_layers(design: DesignSpec) -> list[LayerView]:
    """Walk components from the base opening outward, accumulating package size.

    Returns layers in outside-to-inside order (sequence ascending).
    """
    running = design.base_dimensions
    inside_out: list[LayerView] = []

    for comp in design.ordered_inside_out():
        kind = get_kind(comp.kind)
        params = kind.effective_params(kind.parse_params(comp.params), comp.product)
        geom = kind.geometry(params, running)
        product_name = comp.product.name if comp.product else None
        inside_out.append(
            LayerView(
                component_id=comp.id,
                kind=comp.kind,
                sequence=comp.sequence,
                layer_role=comp.layer_role or kind.default_layer_role,
                label=kind.outside_in_label(params, product_name),
                params=params.model_dump(mode="json"),
                geometry=geom,
                provenance=comp.provenance,
            )
        )
        running = geom.outer

    return list(reversed(inside_out))


# --- "will it fit?" -----------------------------------------------------
#
# Rough placeholder depths, in inches — like the rest of the geometry, good
# enough to catch an obvious mismatch, not a real cut sheet.
_DEPTH_BY_KIND = {
    "glazing": Decimal("0.10"),
    "mat": Decimal("0.06"),
    "mount": Decimal("0.05"),
    "backing": Decimal("0.12"),
}


def estimated_stack_depth_in(design: DesignSpec) -> Decimal:
    """How thick everything the frame has to hold is, front to back."""
    total = Decimal(0)
    if design.artwork and design.artwork.depth_in:
        total += design.artwork.depth_in
    for comp in design.components:
        if comp.kind == "spacer":
            total += Decimal(str(comp.params.get("depth_in") or "0.125"))
        else:
            total += _DEPTH_BY_KIND.get(comp.kind, Decimal(0))
    return total


def frame_rabbet_height_in(design: DesignSpec) -> Decimal | None:
    """The channel depth of the outermost real moulding, if it declares one."""
    for comp in design.ordered_outside_in():
        if comp.kind in ("moulding", "fillet") and comp.product:
            value = comp.product.spec.get("rabbet_height_in")
            if value is not None:
                return Decimal(str(value))
    return None
