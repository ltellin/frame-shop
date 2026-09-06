"""Typed physical specs for catalog products, one Pydantic model per kind.

Same idea as the component-kind param models in ``domain/design/kinds.py``:
``Product.spec`` is stored as loose JSON but validated on write through the model
for that product's ``kind``. A moulding's spec describes its profile; a mat's
describes its board; etc. Keeping this per-kind means ``Product`` stays a narrow
table and each kind owns its own shape.

A richer profile description (curved / ogee / slanted) would be an optional
nested ``profile`` field added to ``MouldingSpec`` later — no migration needed.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

MATERIALS = ("wood", "polystyrene", "aluminum", "mdf", "composite", "other")


class MouldingSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Width you see from the front. Drives the frame's outer size + linear feet.
    # Optional at the model level so a half-entered row never crashes a design
    # read; the catalog loader rejects a moulding row that's missing it.
    face_width_in: Decimal | None = Field(default=None, gt=0)
    # How far the profile projects from the wall (front to back). Optional.
    height_in: Decimal | None = Field(default=None, gt=0)
    # The lip that overlaps the opening — the difference between sight and glass size.
    rabbet_width_in: Decimal = Field(default=Decimal("0.25"), ge=0)
    # Depth of the channel behind the lip: how thick a stack (glass + mats +
    # art + backing) the frame can hold. Optional; used by the "will it fit" check.
    rabbet_height_in: Decimal | None = Field(default=None, gt=0)
    material: str | None = None
    finish: str | None = None


class MatSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    core_color: str | None = None  # "white core", "black core", "cream core"
    thickness_in: Decimal | None = Field(default=None, gt=0)
    conservation: bool | None = None


class GlazingSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uv_pct: int | None = Field(default=None, ge=0, le=100)
    anti_reflective: bool | None = None
    acrylic: bool | None = None  # True = acrylic, False = glass
    thickness_in: Decimal | None = Field(default=None, gt=0)


class GenericSpec(BaseModel):
    """Fallback for product kinds without a dedicated model yet."""

    model_config = ConfigDict(extra="allow")


_SPEC_MODELS: dict[str, type[BaseModel]] = {
    "moulding": MouldingSpec,
    "fillet": MouldingSpec,  # a fillet is a mini moulding — same profile fields
    "mat": MatSpec,
    "glazing": GlazingSpec,
}


def spec_model(kind: str) -> type[BaseModel]:
    return _SPEC_MODELS.get(kind, GenericSpec)


def parse_spec(kind: str, raw: dict | None) -> dict:
    """Validate a raw spec dict for ``kind``; return it normalised to JSON types.

    Raises pydantic ``ValidationError`` on a bad spec — callers decide whether
    that's fatal (loader) or should fall back to ``{}`` (a live design read).
    """
    return spec_model(kind).model_validate(raw or {}).model_dump(mode="json", exclude_none=True)


def spec_schema_catalog() -> list[dict]:
    """JSON-schema per kind, for a future catalog-entry form."""
    return [
        {"kind": kind, "spec_schema": model.model_json_schema()}
        for kind, model in _SPEC_MODELS.items()
    ]
