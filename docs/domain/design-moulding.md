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
- joinery method
- current calculated pricing information or a pricing result — **exact structure
  undecided**

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
- **joinery method** — how the frame's corners / lengths are joined (e.g.
  chop-and-join vs joining from length; underpinner vs splines / dowels). A
  design-specific choice; kept loose for now, not enumerated as a decision. Not a
  Moulding fact.
- `source_offering` — optional reference; null for fully custom
- design-specific dimensions (finished size / sight size / etc. — depends on how
  Design frames dimensions, which is not yet specified)
- **float gap** — for a DesignMoulding whose Moulding is FLOAT, the space between
  the edge of the artwork and the inside of the moulding. **Default 1/4".**
  Required to specify a float frame's dimensions; irrelevant for STANDARD.
- quantity (or is quantity on the Design? — open question)
- current price result — shape undecided

---

# Relationships

- **Design** — a DesignMoulding belongs to exactly one Design. Required — a
  DesignMoulding has no meaning without its Design.
- **Moulding / Material / Finish / Extra** — references one of the first three,
  zero-or-more of the last. Material, Finish, Extras, **joinery method**, and the
  **float gap** are carried here, not on the Moulding.
- **Offering** — optional `source_offering`.
- **Pricing** — a DesignMoulding is the primary unit the moulding pricing engine
  operates on.
- **Work Order / accepted snapshot** — at acceptance, a DesignMoulding's full
  configuration and pricing inputs must be preserved.

---

# Derived Values

- current price (from the pricing engine, given a pricing context)
- **required linear footage** — from Moulding face width + finished size
- **billable footage** — `max(required footage, minimum footage)`, where the
  minimum is `Moulding.minimum_footage` or the shop default (currently 4 ft)
- **bare moulding material cost** — `bare price per foot × billable footage`
  (see [`pricing.md`](pricing.md)); the first pricing layer, before finish /
  extras / joinery / labour / markup
- finished / outer frame size
- whether it still exactly matches `source_offering` (by comparison)
- whether it is still eligible for standard (vs custom) pricing — open question
  whether this is derived, flagged, or explicit

---

# Business Rules / Invariants

- A DesignMoulding belongs to a Design.
- `source_offering` is optional and may be null.
- Having a `source_offering` does **not** lock the configuration — it may
  diverge, and the origin is still recorded.
- An Extra on a DesignMoulding does not by itself make it "custom".

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

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- How do we determine whether a DesignMoulding still exactly matches its source
  Offering after edits?
- Does modifying a DesignMoulding from an Offering automatically remove standard
  pricing eligibility? Can some customizations keep standard pricing while others
  trigger custom pricing?
- What exactly gets snapshotted at acceptance, and is the source Offering
  identity part of it?
- Where does `quantity` live — DesignMoulding or Design?
- What is the structure of the "current price result" it holds?
- How do multiple DesignMouldings in one Design express their spatial /
  structural relationship (build-up: outer frame + liner)?
- Can Moulding / Material / Finish be placeholders during early design?
- What is the **joinery method** vocabulary, and does the choice feed pricing
  and/or production (labor, equipment)?
- Can a float **Offering** pin its own gap, or is the float gap only defaulted
  per DesignMoulding?
- Where does the **shop-default minimum footage** live (a shop-settings /
  pricing-context concept, not literally each Design row)?
- Does the minimum footage also scale finish / other per-foot charges, or only
  the bare moulding material?

---

# Pseudocode Sketch

Illustrative only — not a decision about structure or where values live.

```python
def price_design_moulding(
    moulding,        # geometry + tooling work
    material,        # species -> current lumber cost via pricing_context
    finish,          # -> finish materials + labor
    extras,          # list -> materials + labor + tooling
    dimensions,      # design-specific finished size
    source_offering, # Offering or None -> standard vs custom behavior
    pricing_context, # shop rates, current lumber prices, markup rules
):
    ...  # deferred — Phase 6. Objects expose facts; this engine consumes them.
```
