"""Editable shop pricing reference data.

Update this file directly when your lumber yard changes its prices, or when
you want to add/adjust a Finish, Extra, or joinery rate. No other code needs
to change — see docs/domain/lumber.md, finish.md, extra.md, moulding.md, and
docs/domain/pricing.md for what each of these feeds into.
"""

from __future__ import annotations

from ..models import ExtraRate, FinishRate, JoineryMethod

# (species, thickness_in, width_in) -> $ per board foot.
#
# From this shop's lumber yard (S4S = surfaced four sides). Real dressed
# thickness is thinner than the nominal "quarter" name suggests:
#   4/4 -> 0.75"   5/4 -> 1.0625" (1-1/16")   6/4 -> 1.25"   8/4 -> 1.75"
# Widths are standard S4S actual widths (nominal 2/4/6/8/10/12 -> actual
# 1.5/3.5/5.5/7.25/9.25/11.25). A few thicker species also come as pre-squared
# turning stock (3x3, 4x4), included below as their own rows.
#
# Only this shop's 8 controlled Material species are included; the yard's
# sheet also lists other species (ash, beech, birch, cedar, fir, hickory,
# khaya, pine, and oak's "Rift & Qtr" grade) not on the Material list — add
# rows here if any of those ever get added to Material.
LUMBER_PRICES: dict[tuple[str, float, float], float] = {
    # --- ash ---
    ("ash", 0.75, 3.5): 4.20,
    ("ash", 0.75, 5.5): 6.20,
    ("ash", 0.75, 7.25): 8.20,
    ("ash", 0.75, 3.0): 11.00,  # 3x3
    ("ash", 1.0625, 7.25): 10.00,
    ("ash", 1.25, 5.5): 10.00,
    ("ash", 1.25, 7.25): 16.50,
    ("ash", 1.75, 5.5): 12.00,
    ("ash", 1.75, 7.25): 15.00,
    ("ash", 1.75, 9.25): 20.00,
    # --- cherry ---
    ("cherry", 0.75, 3.5): 4.45,
    ("cherry", 0.75, 5.5): 4.95,
    ("cherry", 0.75, 7.25): 7.70,
    ("cherry", 0.75, 9.25): 9.70,
    ("cherry", 0.75, 11.25): 12.70,
    ("cherry", 0.75, 3.0): 13.00,  # 3x3
    ("cherry", 1.0625, 5.5): 6.80,
    ("cherry", 1.0625, 7.25): 9.20,
    ("cherry", 1.0625, 11.25): 16.70,
    ("cherry", 1.25, 5.5): 8.00,
    ("cherry", 1.25, 7.25): 12.00,
    ("cherry", 1.25, 9.25): 14.00,
    ("cherry", 1.75, 5.5): 12.00,
    ("cherry", 1.75, 7.25): 16.00,
    ("cherry", 1.75, 9.25): 22.00,
    ("cherry", 1.75, 4.0): 28.00,  # 4x4
    # --- maple (hard white) ---
    ("maple", 0.75, 3.5): 4.85,
    ("maple", 0.75, 5.5): 6.30,
    ("maple", 0.75, 7.25): 8.80,
    ("maple", 0.75, 9.25): 12.30,
    ("maple", 0.75, 11.25): 14.30,
    ("maple", 0.75, 3.0): 14.00,  # 3x3
    ("maple", 1.0625, 5.5): 9.20,
    ("maple", 1.0625, 7.25): 12.20,
    ("maple", 1.0625, 9.25): 16.20,
    ("maple", 1.0625, 11.25): 22.20,
    ("maple", 1.25, 5.5): 9.50,
    ("maple", 1.25, 7.25): 14.00,
    ("maple", 1.25, 9.25): 17.00,
    ("maple", 1.75, 5.5): 15.50,
    ("maple", 1.75, 7.25): 24.00,
    ("maple", 1.75, 9.25): 34.50,
    ("maple", 1.75, 4.0): 24.00,  # 4x4
    # --- poplar ---
    ("poplar", 0.75, 1.5): 2.20,
    ("poplar", 0.75, 3.5): 2.50,
    ("poplar", 0.75, 5.5): 3.55,
    ("poplar", 0.75, 7.25): 4.45,
    ("poplar", 0.75, 9.25): 5.70,
    ("poplar", 0.75, 11.25): 6.85,
    ("poplar", 0.75, 3.0): 9.50,  # 3x3
    ("poplar", 1.0625, 3.5): 4.00,
    ("poplar", 1.0625, 5.5): 4.40,
    ("poplar", 1.0625, 7.25): 5.80,
    ("poplar", 1.0625, 9.25): 7.45,
    ("poplar", 1.0625, 11.25): 8.85,
    ("poplar", 1.25, 3.5): 7.00,
    ("poplar", 1.25, 5.5): 7.40,
    ("poplar", 1.25, 7.25): 8.75,
    ("poplar", 1.25, 9.25): 10.00,
    ("poplar", 1.25, 11.25): 11.40,
    ("poplar", 1.75, 3.5): 5.80,
    ("poplar", 1.75, 5.5): 8.00,
    ("poplar", 1.75, 7.25): 9.80,
    ("poplar", 1.75, 9.25): 12.80,
    ("poplar", 1.75, 11.25): 14.50,
    ("poplar", 1.75, 4.0): 15.00,  # 4x4
    # --- red oak ---
    ("red oak", 0.75, 3.5): 3.00,
    ("red oak", 0.75, 5.5): 3.95,
    ("red oak", 0.75, 7.25): 4.85,
    ("red oak", 0.75, 9.25): 6.50,
    ("red oak", 0.75, 11.25): 7.95,
    ("red oak", 0.75, 3.0): 11.00,  # 3x3
    ("red oak", 1.0625, 5.5): 6.20,
    ("red oak", 1.0625, 7.25): 8.95,
    ("red oak", 1.0625, 11.25): 14.20,
    ("red oak", 1.25, 5.5): 7.25,
    ("red oak", 1.25, 7.25): 10.00,
    ("red oak", 1.25, 9.25): 14.00,
    ("red oak", 1.75, 5.5): 10.00,
    ("red oak", 1.75, 7.25): 13.00,
    ("red oak", 1.75, 9.25): 16.50,
    # --- sapele (mahogany) ---
    ("sapele", 0.75, 3.5): 4.95,
    ("sapele", 0.75, 5.5): 7.15,
    ("sapele", 0.75, 7.25): 9.15,
    ("sapele", 0.75, 9.25): 13.20,
    ("sapele", 0.75, 11.25): 16.20,
    ("sapele", 0.75, 3.0): 17.00,  # 3x3
    ("sapele", 1.0625, 3.5): 6.20,
    ("sapele", 1.0625, 5.5): 8.20,
    ("sapele", 1.0625, 7.25): 11.20,
    ("sapele", 1.0625, 9.25): 17.20,
    ("sapele", 1.0625, 11.25): 19.20,
    ("sapele", 1.25, 5.5): 12.00,
    ("sapele", 1.25, 7.25): 14.00,
    ("sapele", 1.25, 9.25): 17.00,
    ("sapele", 1.25, 11.25): 20.00,
    ("sapele", 1.75, 5.5): 15.50,
    ("sapele", 1.75, 7.25): 18.00,
    ("sapele", 1.75, 9.25): 26.00,
    ("sapele", 1.75, 11.25): 33.00,
    ("sapele", 1.75, 4.0): 26.00,  # 4x4
    # --- walnut ---
    ("walnut", 0.75, 3.5): 9.20,
    ("walnut", 0.75, 5.5): 12.70,
    ("walnut", 0.75, 7.25): 16.70,
    ("walnut", 0.75, 9.25): 23.80,
    ("walnut", 0.75, 11.25): 28.20,
    ("walnut", 0.75, 3.0): 28.00,  # 3x3
    ("walnut", 1.0625, 5.5): 17.70,
    ("walnut", 1.0625, 7.25): 22.70,
    ("walnut", 1.0625, 11.25): 29.20,
    ("walnut", 1.25, 5.5): 22.00,
    ("walnut", 1.25, 7.25): 32.00,
    ("walnut", 1.25, 9.25): 42.00,
    ("walnut", 1.75, 5.5): 27.00,
    ("walnut", 1.75, 7.25): 38.00,
    ("walnut", 1.75, 9.25): 48.00,
    ("walnut", 1.75, 11.25): 59.00,
    # --- white oak ---
    ("white oak", 0.75, 3.5): 6.20,
    ("white oak", 0.75, 5.5): 10.20,
    ("white oak", 0.75, 7.25): 15.20,
    ("white oak", 0.75, 9.25): 21.70,
    ("white oak", 0.75, 11.25): 29.70,
    ("white oak", 0.75, 3.0): 28.00,  # 3x3
    ("white oak", 1.0625, 5.5): 14.45,
    ("white oak", 1.0625, 7.25): 26.20,
    ("white oak", 1.0625, 9.25): 30.70,
    ("white oak", 1.0625, 11.25): 39.20,
    ("white oak", 1.25, 5.5): 18.00,
    ("white oak", 1.25, 7.25): 27.00,
    ("white oak", 1.25, 9.25): 31.00,
    ("white oak", 1.75, 5.5): 28.00,
    ("white oak", 1.75, 7.25): 37.00,
    ("white oak", 1.75, 9.25): 44.00,
}

# Finish name -> two-rate pricing. base_rate_per_ft covers the shop's minimum
# footage (setup/cleanup labor dominates a small job); marginal_rate_per_ft
# (lower) applies to footage beyond that minimum. Never scales with face
# width. See docs/decisions/0008-finish-two-rate-pricing.md. EXAMPLE VALUES.
FINISH_RATES: dict[str, FinishRate] = {
    "oil": FinishRate(base_rate_per_ft=1.50, marginal_rate_per_ft=0.75),
    "painted": FinishRate(base_rate_per_ft=3.00, marginal_rate_per_ft=1.25),
    "stained": FinishRate(base_rate_per_ft=2.00, marginal_rate_per_ft=1.00),
}

# Extra name -> pricing method + rate.
# EXAMPLE VALUES.
EXTRA_RATES: dict[str, ExtraRate] = {
    "inlay": ExtraRate(method="per_length", value=4.00),
    "matching spacer": ExtraRate(method="per_length", value=3.00),
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
