"""Moulding-line pricing engine.

Mirrors docs/domain/pricing.md step for step — read that file for the
reasoning behind each function, and docs/decisions/0002-0009 for what's
settled vs still open (docs/OPEN_QUESTIONS.md).
"""

from __future__ import annotations

from .geometry import linear_feet_for_frame
from .models import MouldingLineInput, OrderForm
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
    """LENGTH has no target frame size — it uses requested_footage_ft
    directly instead of a perimeter calculation. The minimum-footage floor
    still applies on top either way."""
    if line.order_form == OrderForm.LENGTH:
        required_ft = line.requested_footage_ft
    else:
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


def per_length_extras_cost(
    line: MouldingLineInput, billable_ft: float, pricing_context: PricingContext
) -> float:
    """Applies at every order form — a continuous inlay runs along the stick
    whether it's cut or not. See docs/decisions/0009-*.md."""
    total = 0.0
    for extra in line.extras:
        rate = pricing_context.extra_rates[extra.name]
        if rate.method == "per_length":
            total += rate.value * billable_ft
    return total


def flat_extras_cost(line: MouldingLineInput, pricing_context: PricingContext) -> float:
    """JOIN only — a flat extra (e.g. a hardware kit) typically describes
    something about the finished, assembled piece. See docs/decisions/0009-*.md."""
    total = 0.0
    for extra in line.extras:
        rate = pricing_context.extra_rates[extra.name]
        if rate.method == "flat":
            total += rate.value
    return total


def matches_source_offering(line: MouldingLineInput) -> bool:
    """No partial credit — any difference drops the line to the custom path.
    Offering pricing is a JOIN-only concept (ADR 0009): a LENGTH or CHOP line
    can never match, regardless of its source_offering."""
    if line.order_form != OrderForm.JOIN:
        return False
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
    """Flat per frame. Only charged on the JOIN, non-Offering-matched path —
    an Offering's menu_price_per_foot is assumed to already bake it in."""
    return pricing_context.joinery_rates[line.joinery_method]


def chop_charge(pricing_context: PricingContext) -> float:
    """Flat per frame, added for CHOP and JOIN order forms. Same shape as
    joinery_cost, for the cutting/mitering operation rather than assembly.
    See docs/decisions/0009-length-chop-join-order-form.md."""
    return pricing_context.chop_charge_per_frame


def material_markup_cost(bare_material_cost: float, pricing_context: PricingContext) -> float:
    return bare_material_cost * pricing_context.material_markup_rate


def price_moulding_line(line: MouldingLineInput, pricing_context: PricingContext) -> dict[str, float]:
    """Price one moulding line. Returns a breakdown dict with a "total" key,
    not just a single number, so a caller can itemize a quote.

    The three order forms are additive layers on one chain (ADR 0009):
        LENGTH = bare_material + material_markup + finish + per_length_extras + tooling_work_labor
        CHOP   = LENGTH + chop_charge
        JOIN   = matches_source_offering ? offering_price + tooling_work_labor
                                          : CHOP + non_offering_labor_charge + flat_extras + joinery
    Each `if` below is a real stopping point for that order form, not a flag
    checked later.
    """
    billable_ft = billable_footage(line, pricing_context)
    tooling_labor = tooling_work_labor_cost(line, billable_ft, pricing_context)

    if line.order_form == OrderForm.JOIN and matches_source_offering(line):
        breakdown = {
            "offering_price": line.source_offering.menu_price_per_foot * billable_ft,
            "tooling_work_labor": tooling_labor,
        }
        breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
        return breakdown

    # LENGTH: the base of the chain, always computed
    bare = bare_moulding_material_cost(line, billable_ft, pricing_context)
    breakdown = {
        "bare_material": bare,
        "material_markup": material_markup_cost(bare, pricing_context),
        "finish": finish_cost(line, billable_ft, pricing_context),
        "per_length_extras": per_length_extras_cost(line, billable_ft, pricing_context),
        "tooling_work_labor": tooling_labor,
    }
    if line.order_form == OrderForm.LENGTH:
        breakdown["total"] = sum(breakdown.values())
        return breakdown

    # CHOP: add the chop/cutting charge
    breakdown["chop_charge"] = chop_charge(pricing_context)
    if line.order_form == OrderForm.CHOP:
        breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
        return breakdown

    # JOIN, not Offering-matched: add the non-offering upcharge, flat extras, joinery
    upcharge_rate = (
        line.non_offering_labor_charge_override
        or pricing_context.default_non_offering_labor_charge_per_foot
    )
    breakdown["non_offering_labor_charge"] = upcharge_rate * billable_ft
    breakdown["flat_extras"] = flat_extras_cost(line, pricing_context)
    breakdown["joinery"] = joinery_cost(line, pricing_context)
    breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
    return breakdown


def price_total(line: MouldingLineInput, pricing_context: PricingContext, quantity: int = 1) -> dict[str, float]:
    """quantity lives on Design in the domain model, not on a moulding line —
    it's an explicit argument here since Design isn't implemented yet.
    Scales every line of the breakdown so it stays internally consistent."""
    if quantity < 1:
        raise ValueError(f"quantity must be >= 1, got {quantity!r}")
    breakdown = price_moulding_line(line, pricing_context)
    return {key: value * quantity for key, value in breakdown.items()}
