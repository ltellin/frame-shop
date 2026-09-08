# Pricing

> Status: **not yet specified** (Phases 6 and 10). Lightweight template plus
> established direction. **Do not design or build a pricing engine yet.**

# Definition

The domain logic that turns a Design (or one component) plus a pricing context
into a price. Conceptually `price_design(design, pricing_context)`, and for one
moulding configuration:

```
price_design_moulding(moulding, material, finish, extras, dimensions,
                      source_offering, pricing_context)
```

# Responsibilities

- Compute prices **outside** React components and database models.
- Let different components use different pricing formulas.
- Evolve over time without forcing rewrites of Moulding / Material / Finish /
  Offering / DesignMoulding.
- **Consume facts** the domain objects expose — those objects must **not** carry
  pricing methods.

# Possible Inputs

Tentative. Not a schema. Different components use different subsets.

| From | Inputs |
|---|---|
| Moulding | geometry; `tooling work` (1–8); `waste factor` (milling yield loss); `milling orientation`; optional `minimum footage` override |
| Material | species → the row to read in the lumber price records |
| Lumber ([`lumber.md`](lumber.md)) | current price per board foot for (species, thickness) |
| Finish | finish materials, finish labor / complexity |
| Extras | extra materials, extra labor, extra fabrication / tooling |
| Offering | whether this is a standard config; stock; standard pricing behavior; batch-production efficiencies (amortized setup) |
| Design context | finished dimensions, required linear footage, shop-default minimum footage, quantity |

# Relationships

- **DesignMoulding** — the primary unit moulding pricing operates on.
- **Material / Finish / Extra / Offering / Moulding** — fact sources.
- A **pricing context** — the shop-defined rules, rates, and current lumber
  prices in effect. Its shape is undecided.

# Derived Values

- The price is always derived. A Design does not store an authoritative price
  (whether it caches a display value is an open question).

# Bare moulding material cost (Phase 2)

The first layer of moulding pricing: the cost of the **bare, unfinished,
unjoined stick** — just wood. Finish, extras, joinery, labour (including tooling
work), markup, and quantity all layer on later (Phase 6+).

**Derived, per foot**, from the Moulding geometry + Material + current lumber
prices:

```python
def required_board_thickness_in(moulding):
    # milling orientation says which dimension the board thickness comes from
    if moulding.milling_orientation == "thickness_from_face_width":
        return moulding.face_width          # + oversize allowance — open
    return moulding.overall_height          # default; + oversize allowance — open


def blank_board_feet_per_foot(moulding):
    # bounding-box cross-section of the blank, as board feet per linear foot
    blank_sqin = moulding.face_width * moulding.overall_height   # + kerf — open
    return blank_sqin * 12 / 144


def bare_material_price_per_foot(moulding, material, lumber_table):
    price_per_bf = lookup_lumber_price_per_bf(
        lumber_table, material.species, required_board_thickness_in(moulding))
    raw = blank_board_feet_per_foot(moulding) * price_per_bf
    return raw * moulding.waste_factor      # milling waste bumps it up
```

**Minimum footage**, applied at design time. The shop has a default minimum
(currently **4 ft**); a Moulding may override it. If a DesignMoulding needs less
than the minimum, it is billed for the minimum:

```python
def bare_moulding_material_cost(design_moulding, design, lumber_table):
    m = design_moulding.moulding
    required_ft = linear_feet_for_frame(*design_moulding.finished_size, m.face_width)
    min_ft = m.minimum_footage or design_context.default_minimum_footage   # e.g. 4
    billable_ft = max(required_ft, min_ft)
    return bare_material_price_per_foot(m, design_moulding.material, lumber_table) * billable_ft
```

Recorded in
[`../decisions/0002-material-and-bare-moulding-material-cost.md`](../decisions/0002-material-and-bare-moulding-material-cost.md).

# Business Rules / Invariants

- Live lumber cost data and shop-defined pricing config are distinct inputs and
  must stay distinguishable.
- Bare price per foot is **derived** from current lumber prices, never stored as
  the source of truth; it is snapshotted at acceptance.
- Below the minimum footage, the bare material charge is
  `price_per_foot × minimum_footage`, not `× required_footage`.
- The same `tooling work` value may price differently for a one-off custom frame
  vs an amortized standard Offering.
- Accepted work must price consistently over time even as costs change — implies
  a snapshot at acceptance. Deferred.

# Historical / Snapshot Concerns

- Which inputs were live data vs shop config, and their values at acceptance,
  must eventually be preserved. Mechanism deferred.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md) under "Pricing".

# Pseudocode Sketch

```
price_design(design, pricing_context):
    total = 0
    for component in design.components:      # DesignMoulding(s), later others
        total += price_component(component, design, pricing_context)
    total += shared_labor(design, pricing_context)
    return total
```
