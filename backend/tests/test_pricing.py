from __future__ import annotations

from decimal import Decimal

from app.domain.design.spec import ArtworkSpec, ComponentSpec, DesignSpec
from app.domain.pricing.engine import price_design
from app.domain.pricing.profiles import PlaceholderProfile


def _design(components):
    return DesignSpec(
        id=1,
        artwork=ArtworkSpec(title="Art", width_in=Decimal("16"), height_in=Decimal("20")),
        components=tuple(components),
    )


def test_empty_design_only_has_fitting_fee():
    breakdown = price_design(_design([]))
    assert breakdown.profile_id == "placeholder"
    assert len(breakdown.lines) == 1
    assert breakdown.lines[0].label == "Fitting & assembly"
    assert breakdown.subtotal_cents == PlaceholderProfile().FITTING_FEE * 100


def test_mat_then_moulding_accumulates_size():
    # 16x20 art, 2" mat -> 20x24 opening, then 1" moulding.
    design = _design(
        [
            ComponentSpec(id=10, kind="moulding", sequence=1, params={"face_in": "1.0"}),
            ComponentSpec(id=11, kind="mat", sequence=2, params={"border_in": "2.0"}),
        ]
    )
    breakdown = price_design(design)
    labels = [line.kind for line in breakdown.lines]
    assert labels == ["moulding", "mat", "fee"]

    mat_line = next(line for line in breakdown.lines if line.kind == "mat")
    # mat self size 20x24 -> 44 united in * 0.35 + 12 cut = 27.40
    assert mat_line.amount_cents == 2740


def test_bigger_art_costs_more():
    small = price_design(_design([ComponentSpec(id=1, kind="glazing", sequence=1, params={})]))
    design_big = DesignSpec(
        id=2,
        artwork=ArtworkSpec(title="Art", width_in=Decimal("40"), height_in=Decimal("60")),
        components=(ComponentSpec(id=1, kind="glazing", sequence=1, params={}),),
    )
    big = price_design(design_big)
    assert big.subtotal_cents > small.subtotal_cents


def test_missing_product_adds_note():
    breakdown = price_design(_design([ComponentSpec(id=1, kind="moulding", sequence=1, params={})]))
    assert any("no catalog product" in n for n in breakdown.notes)


def test_discontinued_product_adds_note():
    from app.domain.design.spec import ProductResolution

    product = ProductResolution(
        product_id=9,
        name="Old Gold",
        description="",
        vendor_name="V",
        sku="X",
        unit_cost_cents=300,
        unit_price_cents=1200,
        price_uom="per_linear_ft",
        available=True,
        discontinued=True,
    )
    breakdown = price_design(
        _design([ComponentSpec(id=1, kind="moulding", sequence=1, params={}, product=product)])
    )
    assert any("discontinued" in n for n in breakdown.notes)
