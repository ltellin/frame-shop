from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.catalog.product_kinds import parse_spec
from app.domain.design.geometry import estimated_stack_depth_in, frame_rabbet_height_in
from app.domain.design.representations import to_exploded_layout
from app.domain.design.spec import ArtworkSpec, ComponentSpec, DesignSpec, ProductResolution


def _resolution(**over) -> ProductResolution:
    base = dict(
        product_id=1,
        kind="moulding",
        name="Test Moulding",
        description="",
        vendor_name="House",
        vendor_is_house=True,
        sku="H-1",
        unit_cost_cents=100,
        unit_price_cents=600,
        price_uom="per_linear_ft",
        available=True,
        discontinued=False,
        spec={},
    )
    return ProductResolution(**{**base, **over})


def _design(components, w="16", h="20", art_depth=None):
    return DesignSpec(
        id=1,
        base_width_in=Decimal(w),
        base_height_in=Decimal(h),
        artwork=ArtworkSpec(title="A", depth_in=Decimal(art_depth)) if art_depth else None,
        components=tuple(components),
    )


def test_bad_spec_is_rejected():
    with pytest.raises(ValidationError):
        parse_spec("moulding", {"face_width_in": -1})
    with pytest.raises(ValidationError):
        parse_spec("moulding", {"unknown_key": 1})


def test_moulding_profile_drives_the_frame_size():
    # face_in param says 1"; the selected product's real profile says 2".
    spec = parse_spec("moulding", {"face_width_in": 2.0})
    comp = ComponentSpec(
        id=1,
        kind="moulding",
        sequence=1,
        params={"face_in": "1.0"},
        product=_resolution(spec=spec),
    )
    layout = to_exploded_layout(_design([comp]))
    # 16x20 base grown by 2" per side from the product profile, not the 1" param.
    assert layout["bounds"]["width_in"] == 20.0
    assert layout["bounds"]["height_in"] == 24.0


def test_no_product_falls_back_to_param():
    comp = ComponentSpec(id=1, kind="moulding", sequence=1, params={"face_in": "1.0"})
    layout = to_exploded_layout(_design([comp]))
    assert layout["bounds"]["width_in"] == 18.0  # grown by the 1" param


def test_rabbet_fit_helpers():
    spec = parse_spec("moulding", {"face_width_in": 1.0, "rabbet_height_in": 0.5})
    frame = ComponentSpec(
        id=1, kind="moulding", sequence=1, params={}, product=_resolution(spec=spec)
    )
    glass = ComponentSpec(id=2, kind="glazing", sequence=2, params={})
    spacer = ComponentSpec(id=3, kind="spacer", sequence=3, params={"depth_in": "0.75"})
    design = _design([frame, glass, spacer], art_depth="0.25")

    assert frame_rabbet_height_in(design) == Decimal("0.5")
    # 0.25 art + 0.10 glass + 0.75 spacer = 1.10 > 0.5 rabbet
    assert estimated_stack_depth_in(design) > Decimal("1.0")
