# Pricing

> Status: **first-pass specification, Phases 2–6 (moulding pricing) now
> complete.** General pricing (Phase 10, beyond one moulding line) is still a
> template. **Do not implement a pricing engine yet** — this is still docs.

# Definition

The domain logic that turns a Design (or one component) plus a **`PricingContext`**
into a price. For one moulding line:

```
price_moulding_line(design_moulding, design, pricing_context) -> PriceBreakdown
```

# Responsibilities

- Compute prices **outside** React components and database models.
- Let different components use different pricing formulas.
- Evolve over time without forcing rewrites of Moulding / Material / Finish /
  Offering / DesignMoulding.
- **Consume facts** the domain objects expose — those objects must **not** carry
  pricing methods.

# PricingContext

**Settled** (first pass): pricing functions take a single `PricingContext`
object rather than a scattered handful of rate-table parameters. It bundles
everything a shop can configure:

- `stock_sizes` — lookup by `stock_size_id` → (nominal thickness, thickness,
  width); species-agnostic reference, see [`lumber.md`](lumber.md)
- `lumber_prices` — lookup by (species, `stock_size_id`) → $/board foot
- `moulding_lumber_sources` — lookup by (moulding id, milling orientation) →
  `stock_size_id` — see
  [`../decisions/0010-moulding-lumber-sources-as-tables.md`](../decisions/0010-moulding-lumber-sources-as-tables.md)
- `finish_rates` — lookup by Finish name → $/ft
- `extra_rates` — lookup by Extra name → `{method, rate}`
- `joinery_rates` — lookup by joinery method → flat $ per frame
- `chop_charge_per_frame` — flat $ per frame, added for `CHOP` and `JOIN`
  order forms (see "Length / Chop / Join" below)
- `tooling_work_rate_per_foot` — $ per tooling-work point, per foot
- `default_minimum_footage` — e.g. 4 ft
- `default_non_offering_labor_charge_per_foot`
- `material_markup_rate` — a percentage applied to bare material cost

**A `PricingContext` is instantiated from one centralized, hand-editable
location per shop** (the same hardcoded-reference-data preference already
recorded for lumber/finish/extra rates — see
[`../architecture/overview.md`](../architecture/overview.md)). This keeps the
pricing *formulas* generic and shop-independent — different shops running this
software plug in their own numbers without touching the formula code. Exact
loading mechanism (a Python module, JSON, YAML, …) is still an implementation
decision, not made now.

# Possible Inputs

Tentative. Not a schema. Different components use different subsets — all now
reached through `PricingContext` rather than passed individually.

| From | Inputs |
|---|---|
| Moulding | `id` (joins against `pricing_context.moulding_lumber_sources`); geometry (face width, overall height); `tooling work` (1–8); `waste factor`; optional `minimum footage` override |
| DesignMoulding | `milling_orientation`; `non_offering_labor_charge` (optional override); `joinery_method`; `order_form` (`LENGTH` \| `CHOP` \| `JOIN`, default `JOIN`); `requested_footage_ft` (only for `LENGTH`) |
| Material | species → the rows to read in `pricing_context.lumber_prices` |
| Finish ([`finish.md`](finish.md)) | looked up in `pricing_context.finish_rates` |
| Extras ([`extra.md`](extra.md)) | looked up in `pricing_context.extra_rates` |
| Offering ([`offering.md`](offering.md)) | `menu_price_per_foot` — used only on an exact match |
| Design | finished dimensions; **`quantity`** (settled: lives on Design, not DesignMoulding) |

# Relationships

- **DesignMoulding** — the primary unit moulding pricing operates on.
- **Material / Finish / Extra / Offering / Moulding** — fact sources.
- **`PricingContext`** — the shop-defined rules and rates in effect, passed
  explicitly into every pricing function.

# Derived Values

- The price is always derived. A Design does not store an authoritative price
  (whether it caches a display value is an open question).

# Bare moulding material cost (Phase 2)

The first layer of moulding pricing: the cost of the **bare, unfinished,
unjoined stick** — just wood.

**The milling convention is fixed** (see [`moulding.md`](moulding.md)): a stick
is milled either `from_board_edge` (face width ↔ board thickness, overall
height ↔ board width — the common case) or `from_board_face` (overall height ↔
board thickness, face width ↔ board width — rotated 90°). Which one applies is a
**DesignMoulding** choice (`milling_orientation`), not a Moulding fact.

**Settled**: the required board size is not computed/rounded from geometry at
all — it's an explicit, shop-set fact, one entry per milling orientation the
Moulding is actually milled in. **Revised (ADR 0010)**: that fact lives in a
separate, hand-editable table (`pricing_context.moulding_lumber_sources`,
keyed by `(moulding.id, orientation)`), not on the Moulding object itself —
see [`moulding.md`](moulding.md),
[`../decisions/0007-source-lumber-size.md`](../decisions/0007-source-lumber-size.md),
and
[`../decisions/0010-moulding-lumber-sources-as-tables.md`](../decisions/0010-moulding-lumber-sources-as-tables.md).
This still means there's no generic "stocked width steps" list to define —
each Moulding is pointed at its own named stock size:

```python
def required_stock_size_id(design_moulding, pricing_context):
    m = design_moulding.moulding
    return pricing_context.stock_size_for(m.id, design_moulding.milling_orientation)


def blank_board_feet_per_foot(moulding):
    # bounding-box cross-section of the blank, as board feet per linear foot
    blank_sqin = moulding.face_width * moulding.overall_height
    return blank_sqin * 12 / 144


def bare_material_price_per_foot(design_moulding, pricing_context):
    m, material = design_moulding.moulding, design_moulding.material
    stock_size_id = required_stock_size_id(design_moulding, pricing_context)
    price_per_bf = pricing_context.lumber_price_per_bf(material.species, stock_size_id)
    raw = blank_board_feet_per_foot(m) * price_per_bf
    return raw * m.waste_factor   # milling waste + multi-stick board yield, both folded in here
```

**Minimum footage**, applied at design time. The shop has a default minimum
(currently **4 ft**); a Moulding may override it. **`LENGTH` order forms have
no target frame size** (see "Length / Chop / Join" below) — they use a
directly-requested footage instead of a perimeter calculation, but the same
minimum-footage floor still applies on top:

```python
def effective_minimum_footage(design_moulding, pricing_context):
    return design_moulding.moulding.minimum_footage or pricing_context.default_minimum_footage   # e.g. 4


def billable_footage(design_moulding, design, pricing_context):
    m = design_moulding.moulding
    if design_moulding.order_form == "LENGTH":
        required_ft = design_moulding.requested_footage_ft
    else:
        required_ft = linear_feet_for_frame(*design_moulding.finished_size, m.face_width)
    return max(required_ft, effective_minimum_footage(design_moulding, pricing_context))


def bare_moulding_material_cost(design_moulding, design, pricing_context):
    billable_ft = billable_footage(design_moulding, design, pricing_context)
    return bare_material_price_per_foot(design_moulding, pricing_context) * billable_ft
```

Recorded in
[`../decisions/0002-material-and-bare-moulding-material-cost.md`](../decisions/0002-material-and-bare-moulding-material-cost.md)
and refined in
[`../decisions/0003-milling-orientation-and-lumber-table-keying.md`](../decisions/0003-milling-orientation-and-lumber-table-keying.md).

# Finish and Extra cost (Phase 3, Finish's pricing shape revised — see ADR 0008)

**Finish is priced with a two-rate model, not a flat rate** — settled in
[`../decisions/0008-finish-two-rate-pricing.md`](../decisions/0008-finish-two-rate-pricing.md).
Setup/cleanup labor dominates a small job, so a `base_rate_per_ft` covers the
piece up to whichever minimum footage actually applied (Moulding override or
shop default — the same one `billable_footage` used), and a lower
`marginal_rate_per_ft` covers footage beyond that:

```python
def finish_cost(design_moulding, billable_ft, pricing_context):
    rate = pricing_context.finish_rates.get(design_moulding.finish)   # e.g. "oil" -> (base, marginal)
    min_ft = effective_minimum_footage(design_moulding, pricing_context)
    base = rate.base_rate_per_ft * min_ft
    marginal = rate.marginal_rate_per_ft * max(0, billable_ft - min_ft)
    return base + marginal


def per_length_extras_cost(design_moulding, billable_ft, pricing_context):
    total = 0
    for extra in design_moulding.extras:
        rate = pricing_context.extra_rates.get(extra.name)   # e.g. "inlay" -> {method, rate}
        if rate.method == "per_length":
            total += rate.value * billable_ft
    return total


def flat_extras_cost(design_moulding, pricing_context):
    total = 0
    for extra in design_moulding.extras:
        rate = pricing_context.extra_rates.get(extra.name)
        if rate.method == "flat":
            total += rate.value
    return total
```

**Settled (ADR 0009): split by pricing method, not just by value, because they
apply at different Length/Chop/Join tiers** — `per_length` Extras apply at
*every* order form (a continuous inlay runs along the stick whether it's cut
or not); `flat` Extras apply at `JOIN` only (they typically describe something
about the finished, assembled piece — see "Length / Chop / Join" below).
`per_length_extras_cost` uses the **same `billable_ft`** computed for the bare
material cost — a working assumption (a shop typically finishes/inlays the
whole stick before chopping and joining it), not a confirmed decision; see
Open Questions. Whether `per_length` Extras should get the same two-rate
treatment as Finish (a base rate covering setup, a lower marginal rate beyond)
is a separate open question — not applied to Extras yet, only to Finish.

Moulding/Extra **compatibility constraints** are real but **not modelled here**
— deliberately deferred, noted in [`extra.md`](extra.md).

Recorded in
[`../decisions/0004-finish-and-extra-pricing.md`](../decisions/0004-finish-and-extra-pricing.md).

# Offering-priced vs custom-priced (Phase 4)

A moulding line prices one of exactly two ways, decided by an **exact-match**
check against its `source_offering`:

```python
def matches_source_offering(design_moulding):
    # settled, ADR 0009: Offering pricing is a JOIN-only concept
    if design_moulding.order_form != "JOIN":
        return False
    o = design_moulding.source_offering
    if o is None:
        return False
    return (design_moulding.moulding == o.moulding
            and design_moulding.material == o.material
            and design_moulding.finish == o.finish
            and set(design_moulding.extras) == set(o.extras))
```

No partial credit — **any** difference drops it to the custom path. A
`LENGTH` or `CHOP` line can never be Offering-priced, regardless of what its
`source_offering` is — see "Length / Chop / Join" below for why.

**Offering-priced** — bypasses the bare-material / finish / extras / joinery
computation entirely. **This was deliberately kept as a flat, independently-set
rate rather than the custom formula with a labor discount** — see the
Alternatives section of ADR 0005: it keeps the "what does this cost to make"
formula free of any Offering-awareness, matches how a shop already thinks about
a standard product's price, and gives a deliberately *stable* listed price that
doesn't drift with every lumber-price tick:

```python
def offering_priced_cost(design_moulding, design, pricing_context):
    billable_ft = billable_footage(design_moulding, design, pricing_context)
    return design_moulding.source_offering.menu_price_per_foot * billable_ft
```

**Custom-priced** (`JOIN`, not Offering-matched) — the full computed chain
through `CHOP`, plus a per-foot `non_offering_labor_charge`, flat Extras, and
joinery. Applies identically whether the DesignMoulding never had a source
Offering, or diverged from one. See "Length / Chop / Join" below for the full
chain — this layer is just its last step.

Recorded in
[`../decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](../decisions/0005-offering-pricing-and-non-offering-labor-charge.md).

# Length / Chop / Join (ADR 0009)

The wholesale moulding trade's standard three-tier classification for how far
a stick is processed before it ships — **Length** (raw, uncut, priced per
foot, no target frame size), **Chop** (cut to the four mitered pieces for a
frame size, not assembled), **Join** (chopped *and* corner-assembled). Settled
as **additive layers on the existing chain**, via `order_form` on
DesignMoulding (default `JOIN` — unchanged behavior for shop-mode use):

```
LENGTH total = bare_material + material_markup + finish + per_length_extras + tooling_work_labor
CHOP total   = LENGTH total + chop_charge
JOIN total   = matches_source_offering ? offering_price + tooling_work_labor
                                        : CHOP total + non_offering_labor_charge + flat_extras + joinery
```

`tooling_work_labor` and `finish` apply at **every** tier — milling the
profile and finishing the stick both happen before the stick is ever cut,
regardless of what the customer ultimately buys. `chop_charge` is a flat $ per
frame, the same shape as `joinery_cost`:

```python
def chop_charge(pricing_context):
    return pricing_context.chop_charge_per_frame   # flat, per frame
```

Recorded in
[`../decisions/0009-length-chop-join-order-form.md`](../decisions/0009-length-chop-join-order-form.md).

# Tooling-work labor, joinery, and material markup (Phase 6)

The remaining pieces of a moulding line's price.

**Tooling-work labor applies universally** — on *both* the Offering-priced and
custom-priced paths, unlike `non_offering_labor_charge`. It scales with the
Moulding's `tooling_work` value (1/2/3/5/8) and with size:

```python
def tooling_work_labor_cost(design_moulding, billable_ft, pricing_context):
    return pricing_context.tooling_work_rate_per_foot * design_moulding.moulding.tooling_work * billable_ft
```

(A linear multiplier on the Fibonacci number — a first-pass assumption, not
confirmed; an alternative would be a distinct $/ft rate per tooling-work level
instead of one rate scaled by the number.)

**Joinery is a flat charge per frame** (not per corner, not per foot), looked up
by method (`"underpinning"` | `"splining"` for now — splining priced roughly 3×
underpinning's labor). **It follows the Offering/custom split**: baked into an
Offering's `menu_price_per_foot` when the line matches exactly; added as its own
line item when custom:

```python
def joinery_cost(design_moulding, pricing_context):
    return pricing_context.joinery_rates.get(design_moulding.joinery_method)  # flat, per frame
```

**Material markup** is a shop-set percentage applied specifically to the **bare
lumber material cost** — not to Finish, Extras, or labor charges, and **not** to
an Offering-priced line (there's no decomposed material portion inside a flat
menu rate to mark up). Will extend to other materials (mats, mounting, glazing)
once those Design components exist — possibly as its own separate markup rate:

```python
def material_markup_cost(bare_material_cost, pricing_context):
    return bare_material_cost * pricing_context.material_markup_rate
```

**Putting the moulding line together** — a structured breakdown, not just a
total, so a caller (e.g. a storefront) can itemize it. One function, with an
early return per order-form tier (each tier is a real stopping point, not a
flag to check later):

```python
def price_moulding_line(design_moulding, design, pricing_context):
    billable_ft = billable_footage(design_moulding, design, pricing_context)
    tooling_labor = tooling_work_labor_cost(design_moulding, billable_ft, pricing_context)

    if design_moulding.order_form == "JOIN" and matches_source_offering(design_moulding):
        breakdown = {
            "offering_price": offering_priced_cost(design_moulding, design, pricing_context),
            "tooling_work_labor": tooling_labor,
        }
        breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
        return breakdown

    # LENGTH: the base of the chain, always computed
    bare = bare_moulding_material_cost(design_moulding, design, pricing_context)
    breakdown = {
        "bare_material": bare,
        "material_markup": material_markup_cost(bare, pricing_context),
        "finish": finish_cost(design_moulding, billable_ft, pricing_context),
        "per_length_extras": per_length_extras_cost(design_moulding, billable_ft, pricing_context),
        "tooling_work_labor": tooling_labor,
    }
    if design_moulding.order_form == "LENGTH":
        breakdown["total"] = sum(breakdown.values())
        return breakdown

    # CHOP: add the chop charge
    breakdown["chop_charge"] = chop_charge(pricing_context)
    if design_moulding.order_form == "CHOP":
        breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
        return breakdown

    # JOIN, not Offering-matched: add the non-offering upcharge, flat extras, joinery
    upcharge_rate = (design_moulding.non_offering_labor_charge
                     or pricing_context.default_non_offering_labor_charge_per_foot)
    breakdown["non_offering_labor_charge"] = upcharge_rate * billable_ft
    breakdown["flat_extras"] = flat_extras_cost(design_moulding, pricing_context)
    breakdown["joinery"] = joinery_cost(design_moulding, pricing_context)
    breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
    return breakdown
```

**Quantity** lives on `Design`, not `DesignMoulding` (settled) — it multiplies
the whole Design's total, not any single line:

```python
def price_design(design, pricing_context):
    line_totals = sum(price_moulding_line(dm, design, pricing_context)["total"]
                       for dm in design.design_mouldings)   # + future component types
    return line_totals * design.quantity
```

Recorded in
[`../decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`](../decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md).

# Business Rules / Invariants

- Live lumber cost data and shop-defined pricing config are distinct inputs and
  must stay distinguishable, both reached through `PricingContext`.
- Bare price per foot is **derived**, never stored as the source of truth; it is
  snapshotted at acceptance.
- Below the minimum footage, the bare material charge is
  `price_per_foot × minimum_footage`, not `× required_footage`.
- No glue-ups and no grade modelling — settled, not formula concerns.
- Finish never depends on face width, but is **not flat per foot** — a
  two-rate model (base rate to the minimum footage, lower marginal rate
  beyond); Extras are either per-length (flat rate, same footage as
  material/finish) or flat regardless of size.
- Offering pricing is **exact-match only** — no partial credit.
- The custom path always adds `non_offering_labor_charge`; tooling-work labor
  and joinery follow their own, different rules (see above) — the three are not
  interchangeable.
- **Tooling-work labor applies on every moulding line, Offering-priced or not,
  at every order form.**
- **Material markup applies only to bare lumber material cost, only on the
  custom path.**
- **`order_form` defaults to `JOIN`** so existing shop-mode behavior is
  unchanged. Offering pricing and `non_offering_labor_charge` are scoped to
  `JOIN` only; `chop_charge` applies to `CHOP` and `JOIN`; `flat` Extras apply
  to `JOIN` only; `per_length` Extras, Finish, and tooling-work labor apply to
  all three.
- **Quantity lives on Design and multiplies the Design's total**, not any one
  DesignMoulding's price.
- Accepted work must price consistently over time even as costs change — implies
  a snapshot at acceptance. Deferred.

# Historical / Snapshot Concerns

- Which inputs were live data vs shop config, and their values at acceptance,
  must eventually be preserved. Mechanism deferred.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md) under "Pricing".
Remaining: the exact tooling-work-labor formula shape (linear multiplier vs a
per-level rate table); whether markup should ever extend to Finish/Extras;
whether Offering should ever get its own Length/Chop price points instead of
being scoped to Join only (ADR 0009).

# Pseudocode Sketch

See `price_design` above for the top-level entry point once a Design has one or
more DesignMouldings (Phase 8/9 territory for anything beyond moulding lines).
