from __future__ import annotations

from decimal import Decimal

from app.domain.design.spec import ComponentSpec, DesignSpec, ProductResolution
from app.domain.pricing.engine import price_design
from app.domain.pricing.profiles import PlaceholderProfile


def _design(components, w="16", h="20"):
    return DesignSpec(
        id=1,
        base_width_in=Decimal(w),
        base_height_in=Decimal(h),
        components=tuple(components),
    )


def test_empty_design_only_has_fitting_fee():
    breakdown = price_design(_design([]))
    assert breakdown.profile_id == "placeholder"
    assert len(breakdown.lines) == 1
    assert breakdown.lines[0].label == "Fitting & assembly"
    assert breakdown.subtotal_cents == PlaceholderProfile().FITTING_FEE * 100


def test_mat_then_moulding_accumulates_size():
    design = _design(
        [
            ComponentSpec(id=10, kind="moulding", sequence=1, params={"face_in": "1.0"}),
            ComponentSpec(id=11, kind="mat", sequence=2, params={"border_in": "2.0"}),
        ]
    )
    breakdown = price_design(design)
    assert [line.kind for line in breakdown.lines] == ["moulding", "mat", "fee"]
    mat_line = next(line for line in breakdown.lines if line.kind == "mat")
    # mat self size 20x24 -> (20 + 24) * 0.35 + 12 cut = 27.40
    assert mat_line.amount_cents == 2740


def test_bigger_base_costs_more():
    small = price_design(_design([ComponentSpec(id=1, kind="glazing", sequence=1, params={})]))
    big = price_design(
        _design([ComponentSpec(id=1, kind="glazing", sequence=1, params={})], w="40", h="60")
    )
    assert big.subtotal_cents > small.subtotal_cents


def test_missing_product_adds_note():
    breakdown = price_design(_design([ComponentSpec(id=1, kind="moulding", sequence=1, params={})]))
    assert any("no catalog product" in n for n in breakdown.notes)


def test_customer_supplied_component_charges_handling_only():
    breakdown = price_design(
        _design(
            [ComponentSpec(id=1, kind="moulding", sequence=1, params={}, provenance="customer")]
        )
    )
    frame = next(line for line in breakdown.lines if line.kind == "moulding")
    assert frame.amount_cents == PlaceholderProfile().COM_HANDLING["moulding"] * 100
    assert any("customer-supplied" in n for n in breakdown.notes)
    assert not any("no catalog product" in n for n in breakdown.notes)


def test_discontinued_product_adds_note():
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
