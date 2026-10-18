"""Editable shop pricing reference data.

Update this file directly when you want to add/adjust a Finish, Extra, or
joinery rate. No other code needs to change — see docs/domain/lumber.md,
finish.md, extra.md, moulding.md, and docs/domain/pricing.md for what each of
these feeds into.

Lumber stock sizes and prices used to live here as Python dicts — they're now
genuinely tabular CSV files instead, since they're meant to be hand-edited as
tables (and are the natural backing for a simple UI later): see
stock_sizes.csv, lumber_prices.csv, and moulding_lumber_sources.csv in this
same directory. See docs/decisions/0010-moulding-lumber-sources-as-tables.md.
"""

from __future__ import annotations

from ..models import ExtraRate, FinishRate, JoineryMethod

# Finish name -> two-rate pricing. base_rate_per_ft covers the shop's minimum
# footage (setup/cleanup labor dominates a small job); marginal_rate_per_ft
# (lower) applies to footage beyond that minimum. Never scales with face
# width. See docs/decisions/0008-finish-two-rate-pricing.md. EXAMPLE VALUES.
FINISH_RATES: dict[str, FinishRate] = {
    "oil": FinishRate(base_rate_per_ft=1.50, marginal_rate_per_ft=0.75),
    "painted": FinishRate(base_rate_per_ft=3.00, marginal_rate_per_ft=1.25),
    "stained": FinishRate(base_rate_per_ft=2.00, marginal_rate_per_ft=1.00),
}

# Extra name -> rate. flat_charge is added once per frame (JOIN only);
# per_length_charge is added per billable foot (every order form). An Extra
# can set either, or both at once — see docs/decisions/0011-*.md.
# EXAMPLE VALUES.
EXTRA_RATES: dict[str, ExtraRate] = {
    "inlay": ExtraRate(flat_charge=50.00, per_length_charge=4.00),
    "matching spacer": ExtraRate(flat_charge=45.00, per_length_charge=2.00),
}

# Joinery method -> flat $ per frame (not per corner, not per foot).
JOINERY_RATES: dict[JoineryMethod, float] = {
    JoineryMethod.UNDERPINNING: 35.00,
    JoineryMethod.SPLINING: 85.00,
}

# Flat $ per frame, added for CHOP and JOIN order forms (not LENGTH) — the
# cutting/mitering charge, same shape as JOINERY_RATES but for the cut
# rather than the assembly. See docs/decisions/0009-length-chop-join-order-form.md.
# EXAMPLE VALUE.
CHOP_CHARGE_PER_FRAME: float = 12.00

# $ per tooling-work point, per foot. Applies to every moulding line,
# Offering-priced or not. EXAMPLE VALUE.
TOOLING_WORK_RATE_PER_FOOT: float = 2.5

# Shop-default minimum billable footage. Settled at 4 ft — see
# docs/decisions/0002-material-and-bare-moulding-material-cost.md.
DEFAULT_MINIMUM_FOOTAGE: float = 4.0

# $ per foot, added on the custom-pricing path only (fully custom, or
# diverged from an Offering). EXAMPLE VALUE.
DEFAULT_NON_OFFERING_LABOR_CHARGE_PER_FOOT: float = 3.00

# Percentage applied to bare lumber material cost only, custom path only.

MATERIAL_MARKUP_RATE: float = 2.5
