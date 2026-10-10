import pytest

from frameshop_pricing.engine import (
    billable_footage,
    extras_cost,
    finish_cost,
    joinery_cost,
    matches_source_offering,
    material_markup_cost,
    price_moulding_line,
    price_total,
    tooling_work_labor_cost,
)
from frameshop_pricing.models import (
    Extra,
    ExtraRate,
    FinishRate,
    JoineryMethod,
    MillingOrientation,
    Moulding,
    MouldingLineInput,
    MouldingType,
    Offering,
)
from frameshop_pricing.pricing_context import PricingContext


@pytest.fixture
def pricing_context():
    return PricingContext(
        lumber_prices={
            ("maple", 0.75, 3.5): 6.0,
            ("maple", 1.5, 2.0): 9.0,
        },
        finish_rates={
            "oil": FinishRate(base_rate_per_ft=1.0, marginal_rate_per_ft=0.5),
            "painted": FinishRate(base_rate_per_ft=2.0, marginal_rate_per_ft=1.0),
        },
        extra_rates={
            "inlay": ExtraRate("per_length", 4.0),
            "trim": ExtraRate("flat", 10.0),
        },
        joinery_rates={JoineryMethod.UNDERPINNING: 8.0, JoineryMethod.SPLINING: 24.0},
        tooling_work_rate_per_foot=0.5,
        default_minimum_footage=4.0,
        default_non_offering_labor_charge_per_foot=3.0,
        material_markup_rate=0.2,
    )


@pytest.fixture
def square_moulding():
    return Moulding(
        name="3/4 square",
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=0.75,
        tooling_work=1,
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),
            MillingOrientation.FROM_BOARD_FACE: (1.5, 2.0),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    )


def make_line(moulding, **overrides):
    defaults = dict(
        moulding=moulding,
        material="maple",
        finish="oil",
        extras=(),
        finished_width_in=8.0,
        finished_height_in=10.0,
    )
    defaults.update(overrides)
    return MouldingLineInput(**defaults)


def test_bare_material_price_per_foot_matches_hand_calc(square_moulding, pricing_context):
    from frameshop_pricing.engine import bare_material_price_per_foot

    line = make_line(square_moulding)
    # blank cross-section 0.75x0.75 sqin -> 0.046875 bf/ft; x $6/bf x 1.1 waste
    assert bare_material_price_per_foot(line, pricing_context) == pytest.approx(0.309375)


def test_rotated_orientation_reads_a_different_lumber_row(square_moulding, pricing_context):
    from frameshop_pricing.engine import bare_material_price_per_foot

    edge_line = make_line(square_moulding, milling_orientation=MillingOrientation.FROM_BOARD_EDGE)
    face_line = make_line(square_moulding, milling_orientation=MillingOrientation.FROM_BOARD_FACE)
    assert bare_material_price_per_foot(edge_line, pricing_context) != bare_material_price_per_foot(
        face_line, pricing_context
    )


@pytest.mark.parametrize(
    ("finished_size", "moulding_override", "expected"),
    [
        ((4.0, 4.0), None, 4.0),  # small frame: shop default minimum wins
        ((100.0, 100.0), None, pytest.approx(33.5833, rel=1e-3)),  # big frame: required footage wins
        ((4.0, 4.0), 6.0, 6.0),  # a Moulding-level override beats the shop default
    ],
)
def test_billable_footage_applies_the_right_minimum(
    square_moulding, pricing_context, finished_size, moulding_override, expected
):
    import dataclasses

    moulding = dataclasses.replace(square_moulding, minimum_footage_override=moulding_override)
    line = make_line(moulding, finished_width_in=finished_size[0], finished_height_in=finished_size[1])
    assert billable_footage(line, pricing_context) == expected


def test_finish_cost_charges_base_rate_up_to_the_minimum_then_a_lower_marginal_rate(
    square_moulding, pricing_context
):
    # at (or under) the shop minimum footage: base_rate_per_ft * minimum only
    small = make_line(square_moulding, finished_width_in=4.0, finished_height_in=4.0, finish="painted")
    min_ft = billable_footage(small, pricing_context)  # the shop minimum wins for a piece this small
    assert finish_cost(small, min_ft, pricing_context) == pytest.approx(2.0 * min_ft)

    # beyond the minimum: base covers the minimum, marginal covers the rest
    big = make_line(square_moulding, finished_width_in=100.0, finished_height_in=100.0, finish="painted")
    billable_ft = billable_footage(big, pricing_context)
    assert billable_ft > min_ft
    expected = 2.0 * min_ft + 1.0 * (billable_ft - min_ft)
    assert finish_cost(big, billable_ft, pricing_context) == pytest.approx(expected)


def test_finish_cost_never_depends_on_face_width(square_moulding, pricing_context):
    import dataclasses

    wide_moulding = dataclasses.replace(square_moulding, face_width_in=3.0)
    narrow_line = make_line(square_moulding, finish="oil")
    wide_line = make_line(wide_moulding, finish="oil")
    # same finished size target, same billable footage floor -> same finish cost
    # regardless of how wide the profile itself is
    billable_ft = 4.0
    assert finish_cost(narrow_line, billable_ft, pricing_context) == finish_cost(
        wide_line, billable_ft, pricing_context
    )


def test_finish_rate_rejects_a_marginal_rate_higher_than_base(pricing_context):
    with pytest.raises(ValueError):
        FinishRate(base_rate_per_ft=1.0, marginal_rate_per_ft=1.5)


def test_extras_cost_mixes_per_length_and_flat(pricing_context):
    class Stub:
        extras = (Extra("inlay"), Extra("trim"))

    # inlay: $4/ft x 5ft = 20; trim: flat $10
    assert extras_cost(Stub(), billable_ft=5.0, pricing_context=pricing_context) == pytest.approx(30.0)


def test_offering_exact_match_bypasses_the_computed_chain(square_moulding, pricing_context):
    offering = Offering(
        name="Black Maple Square",
        moulding=square_moulding,
        material="maple",
        finish="oil",
        extras=(),
        menu_price_per_foot=15.0,
    )
    line = make_line(square_moulding, source_offering=offering)
    assert matches_source_offering(line) is True

    breakdown = price_moulding_line(line, pricing_context)
    billable_ft = billable_footage(line, pricing_context)

    assert breakdown["offering_price"] == pytest.approx(15.0 * billable_ft)
    assert breakdown["tooling_work_labor"] == pytest.approx(
        tooling_work_labor_cost(line, billable_ft, pricing_context)
    )
    assert breakdown["total"] == pytest.approx(sum(breakdown[k] for k in breakdown if k != "total"))
    assert "bare_material" not in breakdown
    assert "material_markup" not in breakdown
    assert "joinery" not in breakdown


def test_diverging_from_offering_falls_to_custom_pricing_with_upcharge(square_moulding, pricing_context):
    offering = Offering(
        name="Black Maple Square",
        moulding=square_moulding,
        material="maple",
        finish="oil",
        extras=(),  # the offering has no extras
        menu_price_per_foot=15.0,
    )
    # adding an inlay the Offering doesn't have breaks the exact match
    line = make_line(square_moulding, extras=(Extra("inlay"),), source_offering=offering)
    assert matches_source_offering(line) is False

    breakdown = price_moulding_line(line, pricing_context)
    billable_ft = billable_footage(line, pricing_context)

    # every custom-path component should be present and independently correct
    assert breakdown["finish"] == pytest.approx(finish_cost(line, billable_ft, pricing_context))
    assert breakdown["extras"] == pytest.approx(extras_cost(line, billable_ft, pricing_context))
    assert breakdown["material_markup"] == pytest.approx(
        material_markup_cost(breakdown["bare_material"], pricing_context)
    )
    assert breakdown["non_offering_labor_charge"] == pytest.approx(
        pricing_context.default_non_offering_labor_charge_per_foot * billable_ft
    )
    assert breakdown["joinery"] == pytest.approx(joinery_cost(line, pricing_context))
    assert breakdown["total"] == pytest.approx(sum(breakdown[k] for k in breakdown if k != "total"))


def test_joinery_is_flat_per_frame_not_scaled_by_size(square_moulding, pricing_context):
    small = make_line(square_moulding, finished_width_in=4.0, finished_height_in=4.0)
    large = make_line(square_moulding, finished_width_in=40.0, finished_height_in=40.0)
    assert joinery_cost(small, pricing_context) == joinery_cost(large, pricing_context)


def test_price_total_scales_every_component_by_quantity(square_moulding, pricing_context):
    line = make_line(square_moulding)
    single = price_moulding_line(line, pricing_context)
    tripled = price_total(line, pricing_context, quantity=3)
    for key, value in single.items():
        assert tripled[key] == pytest.approx(value * 3)


def test_price_total_rejects_nonpositive_quantity(square_moulding, pricing_context):
    line = make_line(square_moulding)
    with pytest.raises(ValueError):
        price_total(line, pricing_context, quantity=0)


def test_unknown_material_raises_a_helpful_error(square_moulding, pricing_context):
    line = make_line(square_moulding, material="unobtainium")
    with pytest.raises(KeyError):
        price_moulding_line(line, pricing_context)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tooling_work", 4),
        ("waste_factor", 0.9),
    ],
)
def test_moulding_rejects_invalid_pricing_inputs(square_moulding, field, value):
    import dataclasses

    with pytest.raises(ValueError):
        dataclasses.replace(square_moulding, **{field: value})


def test_moulding_allows_a_face_only_source_lumber_size(square_moulding):
    # a profile that's only ever milled from_board_face (e.g. wide, shallow) is valid
    import dataclasses

    face_only = dataclasses.replace(
        square_moulding,
        source_lumber_size={MillingOrientation.FROM_BOARD_FACE: (1.5, 2.0)},
    )
    assert face_only.source_lumber_size[MillingOrientation.FROM_BOARD_FACE] == (1.5, 2.0)


def test_moulding_requires_at_least_one_source_lumber_size(square_moulding):
    import dataclasses

    with pytest.raises(ValueError):
        dataclasses.replace(square_moulding, source_lumber_size={})
