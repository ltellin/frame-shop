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

- `lumber_prices` — lookup by (species, thickness, width) → $/board foot
- `finish_rates` — lookup by Finish name → $/ft
- `extra_rates` — lookup by Extra name → `{method, rate}`
- `joinery_rates` — lookup by joinery method → flat $ per frame
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
| Moulding | geometry (face width, overall height); `tooling work` (1–8); `waste factor`; `source_lumber_size` (per orientation); optional `minimum footage` override |
| DesignMoulding | `milling_orientation`; `non_offering_labor_charge` (optional override); `joinery_method` |
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
all — it's an explicit, shop-set fact on the Moulding itself,
`source_lumber_size`, one entry per milling orientation the Moulding is
actually milled in (see [`moulding.md`](moulding.md) and
[`../decisions/0007-source-lumber-size.md`](../decisions/0007-source-lumber-size.md)).
This also means there's no generic "stocked width steps" list to define — each
Moulding just names its own board size:

```python
def required_stock_dims_in(design_moulding):
    m = design_moulding.moulding
    return m.source_lumber_size[design_moulding.milling_orientation]   # (thickness, width)


def blank_board_feet_per_foot(moulding):
    # bounding-box cross-section of the blank, as board feet per linear foot
    blank_sqin = moulding.face_width * moulding.overall_height
    return blank_sqin * 12 / 144


def bare_material_price_per_foot(design_moulding, pricing_context):
    m, material = design_moulding.moulding, design_moulding.material
    thickness, width = required_stock_dims_in(design_moulding)
    price_per_bf = pricing_context.lumber_prices.get(material.species, thickness, width)
    raw = blank_board_feet_per_foot(m) * price_per_bf
    return raw * m.waste_factor   # milling waste + multi-stick board yield, both folded in here
```

**Minimum footage**, applied at design time. The shop has a default minimum
(currently **4 ft**); a Moulding may override it:

```python
def effective_minimum_footage(design_moulding, pricing_context):
    return design_moulding.moulding.minimum_footage or pricing_context.default_minimum_footage   # e.g. 4


def billable_footage(design_moulding, design, pricing_context):
    m = design_moulding.moulding
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


def extras_cost(design_moulding, billable_ft, pricing_context):
    total = 0
    for extra in design_moulding.extras:
        rate = pricing_context.extra_rates.get(extra.name)   # e.g. "inlay" -> {method, rate}
        if rate.method == "per_length":
            total += rate.value * billable_ft
        else:  # "flat"
            total += rate.value
    return total
```

Both use the **same `billable_ft`** computed for the bare material cost — a
working assumption (a shop typically finishes/inlays the whole stick before
chopping and joining it), not a confirmed decision; see Open Questions. Whether
`per_length` Extras should get the same two-rate treatment as Finish (a base
rate covering setup, a lower marginal rate beyond) is an open question — not
applied to Extras yet, only to Finish.

Moulding/Extra **compatibility constraints** are real but **not modelled here**
— deliberately deferred, noted in [`extra.md`](extra.md).

Recorded in
[`../decisions/0004-finish-and-extra-pricing.md`](../decisions/0004-finish-and-extra-pricing.md).

# Offering-priced vs custom-priced (Phase 4)

A moulding line prices one of exactly two ways, decided by an **exact-match**
check against its `source_offering`:

```python
def matches_source_offering(design_moulding):
    o = design_moulding.source_offering
    if o is None:
        return False
    return (design_moulding.moulding == o.moulding
            and design_moulding.material == o.material
            and design_moulding.finish == o.finish
            and set(design_moulding.extras) == set(o.extras))
```

No partial credit — **any** difference drops it to the custom path.

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

**Custom-priced** — the full computed chain, plus a per-foot
`non_offering_labor_charge`. Applies identically whether the DesignMoulding
never had a source Offering, or diverged from one:

```python
def custom_priced_moulding_cost(design_moulding, design, pricing_context):
    billable_ft = billable_footage(design_moulding, design, pricing_context)
    bare = bare_moulding_material_cost(design_moulding, design, pricing_context)
    finish = finish_cost(design_moulding, billable_ft, pricing_context)
    extras = extras_cost(design_moulding, billable_ft, pricing_context)
    upcharge_rate = (design_moulding.non_offering_labor_charge
                     or pricing_context.default_non_offering_labor_charge_per_foot)
    upcharge = upcharge_rate * billable_ft
    return bare, finish, extras, upcharge   # kept separate — the breakdown needs each
```

Recorded in
[`../decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](../decisions/0005-offering-pricing-and-non-offering-labor-charge.md).

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
total, so a caller (e.g. a storefront) can itemize it:

```python
def price_moulding_line(design_moulding, design, pricing_context):
    billable_ft = billable_footage(design_moulding, design, pricing_context)
    tooling_labor = tooling_work_labor_cost(design_moulding, billable_ft, pricing_context)

    if matches_source_offering(design_moulding):
        offering_price = offering_priced_cost(design_moulding, design, pricing_context)
        breakdown = {
            "offering_price": offering_price,
            "tooling_work_labor": tooling_labor,
        }
    else:
        bare, finish, extras, upcharge = custom_priced_moulding_cost(design_moulding, design, pricing_context)
        markup = material_markup_cost(bare, pricing_context)
        joinery = joinery_cost(design_moulding, pricing_context)
        breakdown = {
            "bare_material": bare,
            "material_markup": markup,
            "finish": finish,
            "extras": extras,
            "non_offering_labor_charge": upcharge,
            "joinery": joinery,
            "tooling_work_labor": tooling_labor,
        }

    breakdown["total"] = sum(breakdown.values())
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
- **Tooling-work labor applies on every moulding line, Offering-priced or not.**
- **Material markup applies only to bare lumber material cost, only on the
  custom path.**
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
per-level rate table); whether markup should ever extend to Finish/Extras.

# Pseudocode Sketch

See `price_design` above for the top-level entry point once a Design has one or
more DesignMouldings (Phase 8/9 territory for anything beyond moulding lines).
