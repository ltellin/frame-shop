"""Moulding-line pricing engine.

Mirrors docs/domain/pricing.md step for step — read that file for the
reasoning behind each function, and docs/decisions/0002-0007 for what's
settled vs still open (docs/OPEN_QUESTIONS.md).
"""

from __future__ import annotations

from .geometry import linear_feet_for_frame
from .models import MouldingLineInput
from .pricing_context import PricingContext


def required_stock_dims_in(line: MouldingLineInput) -> tuple[float, float]:
    """(thickness_in, width_in) of the board this line's Moulding is milled
    from, for this line's milling orientation. Not computed — an explicit
    fact on the Moulding (source_lumber_size) — see ADR 0007."""
    return line.moulding.source_lumber_size[line.milling_orientation]


def blank_board_feet_per_foot(line: MouldingLineInput) -> float:
    # bounding-box cross-section of the blank, as board feet per linear foot
    m = line.moulding
    blank_sqin = m.face_width_in * m.overall_height_in
    return blank_sqin * 12 / 144


def bare_material_price_per_foot(line: MouldingLineInput, pricing_context: PricingContext) -> float:
    thickness_in, width_in = required_stock_dims_in(line)
    price_per_bf = pricing_context.lumber_price_per_bf(line.material, thickness_in, width_in)
    raw = blank_board_feet_per_foot(line) * price_per_bf
    return raw * line.moulding.waste_factor  # milling waste + multi-stick board yield, folded in here


def effective_minimum_footage(line: MouldingLineInput, pricing_context: PricingContext) -> float:
    return line.moulding.minimum_footage_override or pricing_context.default_minimum_footage


def billable_footage(line: MouldingLineInput, pricing_context: PricingContext) -> float:
    required_ft = linear_feet_for_frame(
        line.finished_width_in, line.finished_height_in, line.moulding.face_width_in
    )
    return max(required_ft, effective_minimum_footage(line, pricing_context))


def bare_moulding_material_cost(
    line: MouldingLineInput, billable_ft: float, pricing_context: PricingContext
) -> float:
    return bare_material_price_per_foot(line, pricing_context) * billable_ft


def finish_cost(line: MouldingLineInput, billable_ft: float, pricing_context: PricingContext) -> float:
    """Two-rate, not flat: `base_rate_per_ft` covers the shop's minimum
    footage (setup/cleanup dominates a small job); `marginal_rate_per_ft`
    (typically lower) covers footage beyond that minimum. Never depends on
    face width either way. See docs/decisions/0008-finish-two-rate-pricing.md."""
    rate = pricing_context.finish_rates[line.finish]
    min_ft = effective_minimum_footage(line, pricing_context)
    base = rate.base_rate_per_ft * min_ft
    marginal = rate.marginal_rate_per_ft * max(0.0, billable_ft - min_ft)
    return base + marginal


def extras_cost(line: MouldingLineInput, billable_ft: float, pricing_context: PricingContext) -> float:
    total = 0.0
    for extra in line.extras:
        rate = pricing_context.extra_rates[extra.name]
        total += rate.value * billable_ft if rate.method == "per_length" else rate.value
    return total


def matches_source_offering(line: MouldingLineInput) -> bool:
    """No partial credit — any difference drops the line to the custom path."""
    offering = line.source_offering
    if offering is None:
        return False
    return (
        line.moulding == offering.moulding
        and line.material == offering.material
        and line.finish == offering.finish
        and set(line.extras) == set(offering.extras)
    )


def tooling_work_labor_cost(
    line: MouldingLineInput, billable_ft: float, pricing_context: PricingContext
) -> float:
    """Applies on every moulding line, Offering-priced or not — unlike
    non_offering_labor_charge and joinery."""
    return pricing_context.tooling_work_rate_per_foot * line.moulding.tooling_work * billable_ft


def joinery_cost(line: MouldingLineInput, pricing_context: PricingContext) -> float:
    """Flat per frame. Only charged on the custom path — an Offering's
    menu_price_per_foot is assumed to already bake it in."""
    return pricing_context.joinery_rates[line.joinery_method]


def material_markup_cost(bare_material_cost: float, pricing_context: PricingContext) -> float:
    return bare_material_cost * pricing_context.material_markup_rate


def price_moulding_line(line: MouldingLineInput, pricing_context: PricingContext) -> dict[str, float]:
    """Price one moulding line. Returns a breakdown dict with a "total" key,
    not just a single number, so a caller can itemize a quote."""
    billable_ft = billable_footage(line, pricing_context)
    tooling_labor = tooling_work_labor_cost(line, billable_ft, pricing_context)

    if matches_source_offering(line):
        breakdown = {
            "offering_price": line.source_offering.menu_price_per_foot * billable_ft,
            "tooling_work_labor": tooling_labor,
        }
    else:
        bare = bare_moulding_material_cost(line, billable_ft, pricing_context)
        upcharge_rate = (
            line.non_offering_labor_charge_override
            or pricing_context.default_non_offering_labor_charge_per_foot
        )
        breakdown = {
            "bare_material": bare,
            "material_markup": material_markup_cost(bare, pricing_context),
            "finish": finish_cost(line, billable_ft, pricing_context),
            "extras": extras_cost(line, billable_ft, pricing_context),
            "non_offering_labor_charge": upcharge_rate * billable_ft,
            "joinery": joinery_cost(line, pricing_context),
            "tooling_work_labor": tooling_labor,
        }

    breakdown["total"] = sum(breakdown.values())
    return breakdown


def price_total(line: MouldingLineInput, pricing_context: PricingContext, quantity: int = 1) -> dict[str, float]:
    """quantity lives on Design in the domain model, not on a moulding line —
    it's an explicit argument here since Design isn't implemented yet.
    Scales every line of the breakdown so it stays internally consistent."""
    if quantity < 1:
        raise ValueError(f"quantity must be >= 1, got {quantity!r}")
    breakdown = price_moulding_line(line, pricing_context)
    return {key: value * quantity for key, value in breakdown.items()}
