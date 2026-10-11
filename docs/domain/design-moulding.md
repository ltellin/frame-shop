# DesignMoulding

> Status: **first-pass specification.** Documented as a current domain assumption.
> Not final, not an implementation instruction.

---

# Definition

A **DesignMoulding** is the actual moulding configuration selected for **one
Design**. It is the point where geometry, material, finish, embellishment, and
design-specific dimensions come together into something priceable and buildable.

It references / contains:

- a **Moulding** (geometry)
- a **Material**
- a **Finish**
- zero or more **Extras**
- an **optional source Offering** (the `Offering` it was instantiated from, if
  any)
- design-specific dimensional / context information
- **joinery method** — `"underpinning"` | `"splining"` for now. Not just a
  production note: **it prices differently** (splining is roughly 3× the labor
  of underpinning). See [`pricing.md`](pricing.md).
- a **price breakdown** (not a single number) — see Derived Values

A Design will eventually contain one or more design-specific framing components;
`DesignMoulding` is the first of those. (Future siblings: `DesignGlazing`,
`DesignMounting`, etc. — not now.)

---

# Responsibilities

- Hold one fully- (or partially-) configured moulding choice for a Design.
- Remember whether it started from an Offering, even after diverging from it.
- Carry the design-specific dimensions the pricing engine and production need.
- Hold / reference the current live price result while the Design is being
  edited.

---

# How a DesignMoulding originates

Three paths. All are first-class; the model must not privilege one.

### 1. Standard Offering path

```
Offering  --selected / instantiated-->  DesignMoulding
```

The Offering supplies the starting configuration (Moulding, Material, Finish,
Extras). The DesignMoulding may initially match the Offering exactly.
`source_offering` = that Offering.

### 2. Customized Offering path

```
Offering  -->  DesignMoulding  +  modification
```

Example:

```
Offering:        1-inch black maple square
DesignMoulding:  same Moulding, same Material, same Finish, + walnut inlay Extra
```

The DesignMoulding **retains knowledge that it originated from the Offering**,
even though it no longer matches exactly. `source_offering` = that Offering.

### 3. Fully custom path

```
Moulding + Material + Finish + Extras  -->  DesignMoulding
source_offering = none
```

**A DesignMoulding must NOT require an Offering.** This is fundamental: an
Offering is a commercially meaningful standard starting point, not a prerequisite
for making a DesignMoulding.

---

# Possible Attributes

Tentative. Not a schema.

- reference to a Moulding
- reference to a Material
- reference to a Finish
- Extras[] (zero or more)
- **joinery method** — `"underpinning"` | `"splining"` for now, more may be
  added later. A design-specific choice, not a Moulding fact. **Prices
  differently**: a flat charge per frame, looked up by method, added as its own
  line on the custom path or baked into an Offering's menu price on the
  Offering path — see [`pricing.md`](pricing.md).
- **milling orientation** — `from_board_edge` (**default**) | `from_board_face`.
  Which way the moulding is cut from a board:
  - `from_board_edge` — face width ↔ board thickness, overall height ↔ board
    width. The moulding's decorative face is what was the board's edge. (This is
    the common case — see the 3/4"×2" example in [`moulding.md`](moulding.md).)
  - `from_board_face` — overall height ↔ board thickness, face width ↔ board
    width. Rotated 90° from the above; the decorative face is what was the
    board's broad face.

  Same [`lumber.md`](lumber.md) lookup and pricing-formula shape either way —
  only which geometry dimension is looked up as thickness vs width changes. Not
  a Moulding fact: the same Moulding geometry could in principle be milled
  either way for different Designs, so the choice lives here.
- `source_offering` — optional reference; null for fully custom
- design-specific dimensions (finished size / sight size / etc. — depends on how
  Design frames dimensions, which is not yet specified)
- **float gap** — for a DesignMoulding whose Moulding is FLOAT, the space between
  the edge of the artwork and the inside of the moulding. **Default 1/4".**
  Required to specify a float frame's dimensions; irrelevant for STANDARD.
- **`non_offering_labor_charge`** (optional override, per foot) — only relevant
  once the DesignMoulding is priced as custom (`matches_source_offering()` is
  false — see [`pricing.md`](pricing.md)). Defaults from a shop-configured rate;
  exposed to the designer to override for this specific piece once the
  divergence is flagged. Applies identically whether fully custom or diverged
  from an Offering.
- **`order_form`** — `LENGTH` | `CHOP` | `JOIN`, **default `JOIN`**. The
  wholesale-trade classification of how far the stick is processed: raw and
  uncut, cut to miter but unassembled, or cut and corner-joined into a
  finished frame. Shop-mode use never needs to touch this (it defaults to the
  finished-frame behavior already described everywhere else in this doc);
  supplier-mode use (selling moulding to other shops) sets it explicitly. Each
  tier is additive on the one before — see [`pricing.md`](pricing.md) and
  [`../decisions/0009-length-chop-join-order-form.md`](../decisions/0009-length-chop-join-order-form.md).
  Offering pricing and `non_offering_labor_charge` only apply at `JOIN`.
- **`requested_footage_ft`** — required only when `order_form` is `LENGTH`.
  A `LENGTH` line has no target frame size at all (it's just "N feet of this
  moulding, raw"), so it can't derive required footage from `finished size`
  the way `CHOP`/`JOIN` do.

**Not on DesignMoulding**: `quantity` — **settled** to live on
[`design.md`](design.md) instead. Quantity multiplies a Design's whole total,
not any one moulding line — see [`pricing.md`](pricing.md).

---

# Relationships

- **Design** — a DesignMoulding belongs to exactly one Design. Required — a
  DesignMoulding has no meaning without its Design.
- **Moulding / Material / Finish / Extra** — references one of the first three,
  zero-or-more of the last. Material, Finish, Extras, **joinery method**, the
  **float gap**, and the **milling orientation** are carried here, not on the
  Moulding.
- **Offering** — optional `source_offering`.
- **Pricing** — a DesignMoulding is the primary unit the moulding pricing engine
  operates on.
- **Work Order / accepted snapshot** — at acceptance, a DesignMoulding's full
  configuration and pricing inputs must be preserved.

---

# Derived Values

- **price breakdown** — `price_moulding_line()` in [`pricing.md`](pricing.md);
  a structured dict (e.g. `bare_material`, `material_markup`, `finish`,
  `extras`, `non_offering_labor_charge` or `offering_price`, `joinery`,
  `tooling_work_labor`, `total`), **not a single number**. **Settled**.
- **required linear footage** — from Moulding face width + finished size
- **billable footage** — `max(required footage, minimum footage)`, where the
  minimum is `Moulding.minimum_footage` or the shop default (currently 4 ft)
- **bare moulding material cost** — `bare price per foot × billable footage`
  (see [`pricing.md`](pricing.md)); the first pricing layer, before finish /
  extras / joinery / labour / markup
- finished / outer frame size
- **`matches_source_offering`** — exact-match comparison against `source_offering`
  (Moulding, Material, Finish, and the Extras set all identical). **Settled**:
  no partial credit — see [`pricing.md`](pricing.md).
- **pricing path** — `matches_source_offering` true → `Offering.menu_price_per_foot
  × billable footage`; false (fully custom, or diverged) → the computed chain
  plus `non_offering_labor_charge`. **Settled**, see [`pricing.md`](pricing.md).

---

# Business Rules / Invariants

- A DesignMoulding belongs to a Design.
- `source_offering` is optional and may be null.
- Having a `source_offering` does **not** lock the configuration — it may
  diverge, and the origin is still recorded.
- An Extra on a DesignMoulding does not by itself make it "custom" — but if that
  Extra isn't part of the source Offering's recipe, it **does** break the exact
  match and drop the line to custom pricing (these are two different claims:
  Extras are legitimate on standard products in general, but *this specific*
  DesignMoulding either matches its *specific* Offering or it doesn't).

---

# Historical / Snapshot Concerns

During active design a DesignMoulding is **editable** and may use current
shop/vendor/material pricing inputs.

At a later commercial acceptance / order boundary, the system must preserve
enough to reproduce **what was sold and why it cost what it did** — candidates:

- moulding geometry / specification
- material
- finish
- extras
- source Offering information (identity? full config?)
- pricing inputs (lumber cost, finish cost, labor rates, …)
- final accepted price

**Do not decide the snapshot implementation** (copied rows / immutable revisions
/ serialized snapshots / version tables / other). The domain requirement:
*an accepted commercial transaction must not change when live
shop/catalog/material pricing data changes later.*

---

# Open Questions

**Settled** this round: the exact-match rule (`matches_source_offering`, no
partial credit) and its pricing consequence (Offering rate vs. custom chain +
`non_offering_labor_charge`) — see
[`../decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](../decisions/0005-offering-pricing-and-non-offering-labor-charge.md).
Also settled: `quantity` lives on Design; joinery method vocabulary and its
flat-per-frame pricing; the price breakdown is structured, not a single number
— see
[`../decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`](../decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md).

Still open, mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- What exactly gets snapshotted at acceptance, and is the source Offering
  identity (and its `menu_price_per_foot` at the time) part of it?
- How do multiple DesignMouldings in one Design express their spatial /
  structural relationship (build-up: outer frame + liner)?
- Can Moulding / Material / Finish be placeholders during early design?
- Can a float **Offering** pin its own gap, or is the float gap only defaulted
  per DesignMoulding?
- Where does the **shop-default minimum footage** live within `PricingContext`
  precisely (its presence in `PricingContext` is settled; the surrounding
  shop-settings concept, if any, is not)?
- Does the minimum footage also scale finish / other per-foot charges, or only
  the bare moulding material?

---

# Pseudocode Sketch

See [`pricing.md`](pricing.md) for `price_moulding_line(design_moulding, design,
pricing_context)` — the concrete, current version of this now that Phases 2–6
are specified.
