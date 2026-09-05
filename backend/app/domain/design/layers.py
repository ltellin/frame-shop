"""Geometry primitives shared by the component-kind registry and the layer walk.

Kept separate from ``kinds`` and ``geometry`` to avoid an import cycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.measure import Dimensions


@dataclass(frozen=True, slots=True)
class LayerGeometry:
    """What one component contributes, given the running size of everything
    physically inside it."""

    inner: Dimensions  # opening this component received
    outer: Dimensions  # running size after this component
    self_size: Dimensions  # this layer's own footprint (for the schematic)
    opening: Dimensions | None  # visible window, for framed/matted layers
    linear_in: Decimal  # linear material consumed (moulding, fillet)
    area_sqin: Decimal  # sheet material consumed (mat, glass, backing)


@dataclass(frozen=True, slots=True)
class LayerView:
    """A resolved layer: the component plus its computed geometry and role."""

    component_id: int
    kind: str
    sequence: int
    layer_role: str
    label: str
    params: dict
    geometry: LayerGeometry
