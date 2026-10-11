# Offering

> Status: **first-pass specification.** Documented as a current domain assumption.
> Not final, not an implementation instruction.

---

# Definition

An **Offering** is a deliberate shop-standard frame configuration — a curated
point in the shop's larger capability space that the shop intends to sell
repeatedly.

An Offering is a **component recipe, not a sized product** — it references:

- a **Moulding** (geometry)
- a **Material**
- a **Finish**
- zero or more **Extras**

and nothing about dimensions. The same Offering can be built at whatever size a
Design calls for.

Example — `"Black Maple Square"`:

```
moulding = 1-inch square geometry
material = maple
finish   = black
extras   = []
```

Example — `"Black Maple with Walnut Inlay"`:

```
moulding = 1-inch square geometry
material = maple
finish   = black
extras   = [walnut inlay]
```

**An Offering is not merely a UI preset.** It is commercially and operationally
meaningful — in particular, it has its **own price**, independent of the
Moulding/Material/Finish/Extras cost formula.

---

# Responsibilities

- Define a repeatable, named configuration the shop wants to get efficient at
  making.
- Serve as an **optional** starting point for a `DesignMoulding`.
- Carry the **flat per-foot menu price** the shop charges for this exact
  recipe, at any size.

---

# Possible Attributes

Tentative. Not a schema.

- name (`"Black Maple Square"`)
- references: Moulding, Material, Finish, Extras[]
- **`menu_price_per_foot`** — a flat rate, hand-set by the shop, used whenever a
  DesignMoulding exactly matches this Offering. Bypasses the entire bare-material
  / finish / extras computation for that line. See [`pricing.md`](pricing.md).
- possibly a description, product photography, marketing copy — later

Not now, but an Offering may eventually relate to:

- stock / on-hand inventory (explicitly not needed yet)
- batch manufacturing
- preferred production methods / known labor
- marketing, online sales, sales-channel availability
- lead times

**Do not implement any of those systems now.**

---

# Relationships

- **Moulding / Material / Finish / Extra** — an Offering bundles one of each
  (Extras: zero or more).
- **DesignMoulding** — an Offering may be the `source_offering` a DesignMoulding
  was instantiated from. **Optional** — many DesignMouldings have none.
- **Pricing** — an exact-match DesignMoulding is priced from
  `Offering.menu_price_per_foot` directly; any divergence (or no Offering at
  all) falls to the computed custom chain plus a `non_offering_labor_charge`.
  See [`pricing.md`](pricing.md) and
  [`design-moulding.md`](design-moulding.md).
- **Length / Chop / Join** — **settled (ADR 0009): Offering pricing applies
  only to `order_form == JOIN`.** A `LENGTH` or `CHOP` DesignMoulding can
  never be Offering-priced, even if it names a `source_offering` and matches
  its recipe exactly — an Offering represents a standard *finished, assembled*
  product; raw or cut-but-unassembled stock is a categorically different sale.

---

# Derived Values

- Whether a given DesignMoulding still **exactly matches** its source Offering
  — `matches_source_offering()` in [`pricing.md`](pricing.md): Moulding,
  Material, Finish, and the Extras set must all be identical. **No partial
  credit** — any single difference means the DesignMoulding is priced as
  custom instead.

---

# Business Rules / Invariants

- **Offering represents a curated, repeatable shop product/configuration** — that
  is the load-bearing rule.
- **An Offering carries no dimensions.** Size is always a Design-specific input;
  the Offering only fixes the component recipe and its per-foot price.
- An Offering is **optional** as a source for a DesignMoulding. The shop can
  fabricate arbitrary configurations with no Offering involved.
- An Offering may include Extras and still be a standard product.
- **Exact match only.** A DesignMoulding either matches its source Offering's
  full recipe or it doesn't — there's no notion of "close enough" or some
  extras counting and others not.

---

# Historical / Snapshot Concerns

- When a Design sourced from an Offering is accepted, the accepted snapshot must
  preserve enough about the Offering (identity? `menu_price_per_foot` at the
  time? full configuration?) to reproduce what was sold. Still open.
- Offering definitions and `menu_price_per_foot` change over time; accepted
  orders must not move.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- Should the **source Offering identity** (and the `menu_price_per_foot` in
  effect at the time) be preserved in an accepted snapshot?
- How should **stocked Offering inventory** be represented later, if it ever is?

---

# Pseudocode Sketch

See [`pricing.md`](pricing.md) for `matches_source_offering` and
`offering_priced_cost`.
