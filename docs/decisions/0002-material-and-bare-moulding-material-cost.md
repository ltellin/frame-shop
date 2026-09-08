# 0002 — Material list, lumber pricing, and bare moulding material cost

Status: accepted (first pass — Phase 2). Date: 2026-09-08.

## Context

Phase 2 works out what a moulding is *made of* and the first layer of what it
*costs*: the bare, unfinished, unjoined stick — just wood. The shop mills its own
mouldings from rough lumber, so the cost of a stick is a function of the profile
geometry, the species, and current lumber prices. Finish, extras, joinery,
labour, markup, and quantity are later layers (Phase 3 / Phase 6) and are not
decided here.

## Decision

**Material is a small controlled list — wood species only for now.** Initial
species: **maple, poplar, white oak, red oak, walnut, sapele, ash, cherry**. A
`DesignMoulding` (or `Offering`) references one Material. Material holds no
geometry, price, or thickness.

**Lumber is a stored, time-varying price table** ([`../domain/lumber.md`](../domain/lumber.md)).
Rows are keyed by **species × nominal thickness** (4/4, 5/4, 6/4, 8/4, …) and
carry a price per **board foot** (unit assumed — open question). It is reference
data, updated periodically, kept separate from transaction history: updating a
price re-prices live Designs but never moves an accepted order.

**The bare moulding material cost is derived, per foot:**

```
required_thickness  = face_width or overall_height, per the Moulding's milling orientation
blank_cross_section = face_width × overall_height          (bounding box)
board_feet_per_foot = blank_cross_section × 12 / 144
raw_$_per_foot      = board_feet_per_foot × lumber_price(species, required_thickness)
bare_$_per_foot     = raw_$_per_foot × waste_factor
```

- **Milling orientation** is a new Moulding field: a 3/4"w × 2"t profile can be
  milled from 3/4"-thick stock (thickness = face width) or 2"-thick stock
  (thickness = overall height). Default: thickness from overall height.
- **Waste factor** is a new Moulding field: a multiplier ≥ 1.0 for *milling*
  yield loss (oversize blank + chips hogged out shaping the profile). Higher =
  pricier. Representation and default are open.

**Minimum footage.** The shop has a default minimum (**4 ft**). A Moulding may
override it (`minimum_footage`). At design time:

```
billable_feet = max(required_feet, minimum_feet)
bare_moulding_material_cost = bare_$_per_foot × billable_feet
```

Below the minimum you are billed for the minimum footage — not the actual
footage, and not a separate surcharge rate.

A mitre **cutting allowance** on `required_feet` is deferred (not modelled now).

## Alternatives considered

- **Free-text materials.** Rejected — a short controlled list keeps pricing and
  the UI simple; the shop works in a fixed set of species.
- **A precomputed Moulding × Material price matrix.** Rejected — derive from
  lumber prices so a price update propagates automatically and nothing goes
  stale.
- **Minimum footage as a flat surcharge or a rate multiplier.** Rejected — "bill
  for N feet" (N = 4) is the standard shop practice and the simplest rule.
- **Deriving waste factor from tooling work.** Not chosen — milling yield loss
  and setup effort are correlated but not the same (a deep cove wastes wood but
  may be one pass). Kept as its own field; revisit if it proves redundant.

## Consequences

- Phase 6 only needs to add tooling-work labour, finish, extras, joinery, markup,
  and quantity **on top of** this bare material cost.
- Two new Moulding fields (`milling orientation`, `waste factor`) and one
  optional one (`minimum footage`). Moulding still carries no prices.
- A new domain concept, `Lumber`, with its own doc.
- **Open:** the exact milling geometry — kerf / oversize allowance on stock
  thickness and blank, which thickness steps exist, glue-ups, grade — and where
  shop-wide pricing defaults (the 4 ft minimum, etc.) live. See
  [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).
- Accepted work must snapshot the lumber price and the Moulding pricing inputs
  used, not re-read them.
