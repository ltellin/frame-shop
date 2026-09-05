"""Plain-data representation of a Design, independent of ORM and HTTP.

Services build these dataclasses from ORM rows (or request payloads) and hand
them to the geometry walk, the pricing engine, and the representation functions.
Nothing in this module imports SQLAlchemy or FastAPI.

A DesignSpec is only ever built when the design has real base dimensions — the
service layer guards that. So the geometry seed is always present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.measure import Dimensions

# Values a design's base rectangle can represent.
BASE_REFS = ("art", "sight", "glass", "rabbet", "outside")

BASE_REF_LABELS = {
    "art": "Art size",
    "sight": "Sight size",
    "glass": "Glass size",
    "rabbet": "Frame rabbet",
    "outside": "Outside size",
}


@dataclass(frozen=True, slots=True)
class ArtworkSpec:
    """Optional artwork *metadata*. Dimensions live on the DesignSpec base."""

    title: str | None = None
    art_type: str | None = None  # print_photo | canvas | works_on_paper | textile | object_3d
    depth_in: Decimal | None = None
    notes: str | None = None


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
    sequence: int  # 1 = outermost, ascending toward the base opening
    params: dict
    layer_role: str | None = None
    product: ProductResolution | None = None
    provenance: str = "shop"  # shop | customer
    parent_component_id: int | None = None


@dataclass(frozen=True, slots=True)
class DesignSpec:
    id: int | None
    base_width_in: Decimal
    base_height_in: Decimal
    base_ref: str = "art"
    type: str = "framing"
    quantity: int = 1
    artwork: ArtworkSpec | None = None
    components: tuple[ComponentSpec, ...] = field(default_factory=tuple)

    @property
    def base_dimensions(self) -> Dimensions:
        return Dimensions(self.base_width_in, self.base_height_in)

    @property
    def shows_artwork_layer(self) -> bool:
        return self.base_ref == "art"

    def ordered_outside_in(self) -> list[ComponentSpec]:
        return sorted(self.components, key=lambda c: c.sequence)

    def ordered_inside_out(self) -> list[ComponentSpec]:
        return sorted(self.components, key=lambda c: c.sequence, reverse=True)
