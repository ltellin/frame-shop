# Lumber

> Status: **first-pass specification, milling-geometry details settled.**
> Documented as a current domain assumption. Not final, not an implementation
> instruction. Do **not** design the lumber purchasing / inventory system —
> this is only the price-reference concept.

---

# Definition

**Lumber** is the rough stock the shop buys to mill its own mouldings: a species
(from the [`Material`](material.md) list) at a nominal **thickness** and
**width**, together with its **current price**.

This is the **master lumber price list** — the record of what boards the shop
commonly buys and what they currently cost from its lumber yard. In practice
this stays a **short list**: picture-frame stock doesn't vary in size all that
much, so a shop only buys a handful of (species, thickness, width) combinations.
It should be easy for the shop to view and update by hand every so often when
the lumber yard's prices change. It is **reference data** — periodically
updated — and is kept separate from transaction history (an accepted order must
not move when a lumber price is updated later).

---

# Responsibilities

- Hold the current cost of each stock type the shop buys, so the pricing engine
  can look it up by (species, thickness, width).
- Be updatable when the shop's lumber source changes its prices.
- Stay distinct from any historical / accepted-order pricing snapshot.

---

# Possible Attributes

Tentative. Not a schema.

- **species** (matches a `Material` species)
- **nominal thickness** — **settled stock steps: 4/4, 5/4, 6/4, 8/4**. Actual
  **S4S (surfaced four sides) dressed thickness** — what a Moulding's
  `source_lumber_size` should actually use — is thinner than the "quarter"
  name suggests: **4/4 → 0.75", 5/4 → 1.0625" (1-1/16"), 6/4 → 1.25", 8/4 →
  1.75"**. (An earlier pass in this doc used rough, pre-surfacing numbers —
  corrected here against this shop's real lumber yard price sheet.) More
  thickness steps can be added later if a Moulding needs deeper stock; a few
  species are also available as pre-squared stock (3"×3", 4"×4").
- **nominal width** — the stocked board widths the shop buys in (this shop's
  actual S4S widths: 1.5", 3.5", 5.5", 7.25", 9.25", 11.25" — standard
  dressed widths for nominal 2"/4"/6"/8"/10"/12" stock, plus pre-squared
  turning stock at 3"×3" and 4"×4"). No generic "list of stocked widths" to
  define here — a specific board size gets a `stock_size_id` in
  `stock_sizes.csv` (species-agnostic — see "Settled: a shop-managed stock
  table" below), and each Moulding is pointed at one via
  `moulding_lumber_sources.csv`; a lumber-price row exists for whichever
  `(species, stock_size_id)` combinations those actually reference.
- **price** per **board foot** (settled — see
  [`../decisions/0003-milling-orientation-and-lumber-table-keying.md`](../decisions/0003-milling-orientation-and-lumber-table-keying.md))
- last-updated / effective date
- ~~grade / quality~~ — **not modelled** (settled: one price per species ×
  thickness × width)
- optional: source / supplier label

---

# Relationships

- **Material** — names the species; Lumber holds the thicknesses, widths, and
  prices for that species.
- **Moulding** — `PricingContext.moulding_lumber_sources` (keyed by
  `(moulding.id, milling_orientation)`, see [`moulding.md`](moulding.md))
  points at the `stock_size_id` to look up here — an explicit, shop-editable
  fact, not computed from geometry, and not a field on `Moulding` itself
  (ADR 0010). **A single stocked board can yield more than one side-by-side
  moulding stick** — that yield isn't modelled explicitly here; it's folded
  into the Moulding's [`waste factor`](moulding.md).
- **Pricing** — `bare_material_price_per_foot` reads a lumber price by
  (species, `stock_size_id`); see [`pricing.md`](pricing.md).

---

# Derived Values

_None on Lumber itself — it is an input. Everything derived from it lives in
pricing._

---

# Business Rules / Invariants

- Time-varying: prices change; the table is the *current* truth only.
- Historical / accepted work snapshots the price it used and does not re-read
  this table.
- No glue-ups: the shop always buys stock already at or above the needed
  thickness — a lumber row is never combined with another to reach a size.
- Every species on the `Material` list should have at least one lumber row for
  the pricing chain to work (enforcement TBD).

---

# Historical / Snapshot Concerns

The whole point of splitting Lumber out from Material: when the shop updates a
price, live Designs re-price but accepted orders do not. The snapshot mechanism
is deferred (shared with `Material` / `DesignMoulding`).

---

# Settled: a shop-managed stock table (ADR 0010)

Recorded 2026-10-17 as the owner's intended design; **implemented** the same
day as three hand-editable CSVs in `backend/frameshop_pricing/data/`. Full
reasoning in
[`../decisions/0010-moulding-lumber-sources-as-tables.md`](../decisions/0010-moulding-lumber-sources-as-tables.md).

- **`stock_sizes.csv`** — species-agnostic reference table:
  `stock_size_id, nominal_thickness, thickness_in, width_in`. Seeded once from
  the lumber yard's price sheet; from here on the shop maintains it directly
  — add, rename, reprice (via the price table below), remove — without
  touching code.
- **`lumber_prices.csv`** — `species, stock_size_id, price_per_bf`. One row
  per (species, stock size) the shop actually stocks. Price stayed **per
  board foot** (not per linear foot) — the existing unit, not changed by this
  table split.
- **`moulding_lumber_sources.csv`** — `moulding_id, milling_orientation,
  stock_size_id`. Each Moulding is pointed at a named stock size by id,
  **one row per milling orientation it's actually milled in** — this is the
  same shape ADR 0007 established, just moved off the `Moulding` object (see
  [`moulding.md`](moulding.md)).

**Why a separate `stock_sizes.csv` and not just two tables:** the first design
had `moulding_lumber_sources` and `lumber_prices` each independently keyed by
raw `(thickness, width)` — a typo in one wouldn't be caught against the
other. Routing both through a shared `stock_size_id` makes a stock size exist
in exactly one place.

**Why this was needed at all:** before this, the link between a Moulding and
its lumber price was an exact numeric match against a Python data module. In
v0.2.0, nine mouldings named sizes the yard doesn't sell (0.5" and 1.0" thick,
1.25" x 3.5") and so were unpriceable until the data was corrected by hand
(v0.2.1). Rebuilding that price data for this migration also surfaced a real,
previously undetected bug: the "3x3" and "4x4" square turning-stock rows were
filed under the surrounding tier's thickness instead of their actual square
dimension — fixed as part of this change (see ADR 0010).

**Resolved** from the original open details list: species fit as one price
row per (species, stock size) (not a grid); unit stayed board foot; a
Moulding keeps one `stock_size_id` pointer per milling orientation.
**Still open:** effective dates / snapshots (see Historical / Snapshot
Concerns above, unchanged by this table split); what happens when a Moulding
points at a `stock_size_id` that's since been removed from `stock_sizes.csv`
— not defensively handled, currently just a `KeyError` at pricing time.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md). Unit, keying,
thickness steps, glue-ups, and grade are **settled** (see
[`../decisions/0003-milling-orientation-and-lumber-table-keying.md`](../decisions/0003-milling-orientation-and-lumber-table-keying.md)).
Stocked board widths — **resolved**: there's no generic list to define; each
Moulding is pointed at its own named stock size via
`moulding_lumber_sources.csv` (see
[`../decisions/0010-moulding-lumber-sources-as-tables.md`](../decisions/0010-moulding-lumber-sources-as-tables.md)).
Remaining, both carried over from the stock-table work above: effective
dates / snapshots; behavior when a Moulding points at a removed
`stock_size_id`.

---

# Pseudocode Sketch

```python
# reference lookup — current price only
def lookup_lumber_price_per_bf(lumber_prices, species, stock_size_id):
    return lumber_prices[(species, stock_size_id)]
```
