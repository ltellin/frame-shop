"""Plain-data representation of a Design, independent of ORM and HTTP.

Services build these dataclasses from ORM rows (or request payloads) and hand
them to the geometry walk, the pricing engine, and the representation functions.
Nothing in this module imports SQLAlchemy or FastAPI.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.measure import Dimensions


@dataclass(frozen=True, slots=True)
class ArtworkSpec:
    title: str
    width_in: Decimal
    height_in: Decimal
    depth_in: Decimal | None = None

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.width_in, self.height_in)


@dataclass(frozen=True, slots=True)
class ProductResolution:
    """A component's product resolved against the catalog at a point in time.

    For a live/draft Design this reflects current catalog data. For an accepted
    Design (later slice) it comes from the immutable snapshot.
    """

    product_id: int
    name: str
    description: str
    vendor_name: str
    sku: str
    unit_cost_cents: int
    unit_price_cents: int
    price_uom: str  # per_linear_ft | per_united_in | per_sqft | each | sheet
    available: bool
    discontinued: bool


@dataclass(frozen=True, slots=True)
class ComponentSpec:
    id: int
    kind: str
    sequence: int  # 1 = outermost, ascending toward the artwork
    params: dict
    layer_role: str | None = None
    product: ProductResolution | None = None
    parent_component_id: int | None = None


@dataclass(frozen=True, slots=True)
class DesignSpec:
    id: int | None
    artwork: ArtworkSpec
    components: tuple[ComponentSpec, ...] = field(default_factory=tuple)

    def ordered_outside_in(self) -> list[ComponentSpec]:
        return sorted(self.components, key=lambda c: c.sequence)

    def ordered_inside_out(self) -> list[ComponentSpec]:
        return sorted(self.components, key=lambda c: c.sequence, reverse=True)
