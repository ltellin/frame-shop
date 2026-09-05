"""The layer walk: turn a DesignSpec into an ordered list of resolved layers.

Both the pricing engine and the representation functions consume this so that
geometry logic lives in exactly one place.
"""

from __future__ import annotations

from app.domain.design.kinds import get_kind
from app.domain.design.layers import LayerView
from app.domain.design.spec import DesignSpec


def walk_layers(design: DesignSpec) -> list[LayerView]:
    """Walk components from the artwork outward, accumulating package size.

    Returns layers in outside-to-inside order (sequence ascending).
    """
    running = design.artwork.dimensions
    inside_out: list[LayerView] = []

    for comp in design.ordered_inside_out():
        kind = get_kind(comp.kind)
        params = kind.parse_params(comp.params)
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
            )
        )
        running = geom.outer

    return list(reversed(inside_out))
