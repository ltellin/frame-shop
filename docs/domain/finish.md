# Finish

> Status: **specified and implemented** (backend/frameshop_pricing/). Documented as a
> current domain assumption; the pricing model may still evolve.

---

# Definition

**Finish** describes how the chosen Material is surface-treated. It is distinct
from Moulding geometry and from Material. It is a **small controlled list of
strings**, the same pattern as Material.

Starting values: **`"oil"`, `"painted"`, `"stained"`** — more to be added later.
A value can be as specific as needed (e.g. a future `"black stain"` alongside a
generic `"stained"`) — the list isn't required to stay at one level of
specificity.

Finish is a choice at the **DesignMoulding / Offering** layer.

---

# Responsibilities

- Name the surface treatment chosen for a configured moulding, from the
  controlled list.
- Identify which rate the pricing engine looks up.

---

# Possible Attributes

Tentative. Not a schema.

- **name** — the controlled-list string (`"oil"`, `"painted"`, `"stained"`, …)

Finish does **not** hold: geometry, material, a price, or (for now) structured
colour/product data — see Business Rules.

---

# Relationships

- **DesignMoulding** — references a Finish.
- **Offering** — references a Finish as part of a standard configuration.
- **Pricing** — looks up a **two-rate** pricing fact for the Finish name (a
  base rate and a lower marginal rate — see below); see
  [`pricing.md`](pricing.md).

---

# Derived Values

- **finish cost contribution** — **settled as a two-rate model, not a flat
  rate** (see [`../decisions/0008-finish-two-rate-pricing.md`](../decisions/0008-finish-two-rate-pricing.md)):

  ```
  finish_cost = base_rate_per_ft × minimum_footage
              + marginal_rate_per_ft × max(0, billable_footage − minimum_footage)
  ```

  `minimum_footage` is whichever minimum actually applied to this moulding
  line (a Moulding-level override, or the shop default) — the same one used
  for the bare material cost, so the "minimum charge" for finishing a small
  piece is naturally covered by it, with no separate finish-specific minimum
  needed. Derived, not stored here.

---

# Business Rules / Invariants

- A configured DesignMoulding has exactly one Finish.
- **Finish pricing never depends on the moulding's face width** — a wide
  profile and a narrow profile cost the same to finish, for the same footage.
- **Finish pricing is not flat-per-foot.** Setup and cleanup labor dominate a
  small job; a `base_rate_per_ft` covers the piece up to the shop's minimum
  footage, and a lower `marginal_rate_per_ft` covers footage beyond that —
  size matters much less once a piece is already being finished.
  `marginal_rate_per_ft` should not exceed `base_rate_per_ft`.
- Finish is stored as a **plain string** for now, not decomposed into a finish
  type + colour/product fields.
- **Finish rates are hardcoded reference data**, stored alongside the other
  pricing constants (lumber prices, extra/joinery rates) in
  `backend/frameshop_pricing/data/shop_pricing_data.py` — easy to hand-edit and extend.

---

# Historical / Snapshot Concerns

Finish rates may change over time; accepted orders must not move. Same
snapshot requirement as Material/Lumber — mechanism deferred.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- Should **Extras'** `per_length` pricing get the same two-rate (base +
  marginal) treatment as Finish, for the same setup-labor reasoning? Not
  applied there yet — only asked about for Finish so far.

---

# Pseudocode Sketch

See [`pricing.md`](pricing.md) for `finish_cost`, and
`backend/frameshop_pricing/engine.py` for the implementation.
