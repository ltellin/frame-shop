# Lumber

> Status: **first-pass specification.** Documented as a current domain assumption.
> Not final, not an implementation instruction. Do **not** design the lumber
> purchasing / inventory system — this is only the price-reference concept.

---

# Definition

**Lumber** is the rough stock the shop buys to mill its own mouldings: a species
(from the [`Material`](material.md) list) at a nominal **thickness** (e.g. 4/4,
5/4, 6/4, 8/4), together with its **current price**.

This is the "place to store the pricing info of whatever lumber source is being
used." It is **reference data** — periodically updated — and is kept separate
from transaction history (an accepted order must not move when a lumber price is
updated later).

---

# Responsibilities

- Hold the current cost of each stock type the shop buys, so the pricing engine
  can look it up by (species, thickness).
- Be updatable when the shop's lumber source changes its prices.
- Stay distinct from any historical / accepted-order pricing snapshot.

---

# Possible Attributes

Tentative. Not a schema.

- **species** (matches a `Material` species)
- **nominal thickness** (4/4, 5/4, 6/4, 8/4, … — the stock steps the shop buys)
- **price** per **board foot** (unit assumed — see Open Questions)
- last-updated / effective date
- optional: grade / quality (FAS, Select, …) — out of scope for now, flag only
- optional: source / supplier label

---

# Relationships

- **Material** — names the species; Lumber holds the thicknesses and prices for
  that species.
- **Moulding** — a Moulding's geometry selects the **required thickness** (and
  the blank size) → which lumber row is used.
- **Pricing** — `bare_material_price_per_foot` reads a lumber price; see
  [`pricing.md`](pricing.md).

---

# Derived Values

_None on Lumber itself — it is an input. Everything derived from it lives in
pricing._

---

# Business Rules / Invariants

- Time-varying: prices change; the table is the *current* truth only.
- Historical / accepted work snapshots the price it used and does not re-read
  this table.
- Every species on the `Material` list should have at least one lumber row for
  the pricing chain to work (enforcement TBD).

---

# Historical / Snapshot Concerns

The whole point of splitting Lumber out from Material: when the shop updates a
price, live Designs re-price but accepted orders do not. The snapshot mechanism
is deferred (shared with `Material` / `DesignMoulding`).

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- Unit of pricing — board foot assumed; confirm. Is it ever per linear foot or
  per piece?
- How is the table keyed — species × nominal thickness only, or also width /
  length / grade?
- What thickness steps does the shop actually stock?
- Can thinner stock be glued up to reach a needed thickness, and how does that
  change the cost?
- Does grade / quality need to be modelled, or is one price per (species,
  thickness) enough?

---

# Pseudocode Sketch

```python
# reference lookup — current price only
def lookup_lumber_price_per_bf(lumber_table, species, nominal_thickness):
    row = lumber_table.get(species=species, thickness=nominal_thickness)
    return row.price_per_board_foot
```
