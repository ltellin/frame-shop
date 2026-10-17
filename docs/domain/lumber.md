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
  dressed widths for nominal 2"/4"/6"/8"/10"/12" stock). No generic "list of
  stocked widths" to define here — a specific board size is named explicitly
  per Moulding via `source_lumber_size` (see
  [`moulding.md`](moulding.md)); a lumber row exists for whichever
  (thickness, width) combinations those actually reference.
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
- **Moulding** — `source_lumber_size` (per milling orientation, see
  [`moulding.md`](moulding.md)) names the exact (thickness, width) to look up
  here — an explicit, shop-editable fact, not computed from geometry. **A
  single stocked board can yield more than one side-by-side moulding stick** —
  that yield isn't modelled explicitly here; it's folded into the Moulding's
  [`waste factor`](moulding.md).
- **Pricing** — `bare_material_price_per_foot` reads a lumber price by
  (species, thickness, width); see [`pricing.md`](pricing.md).

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

# Planned direction: a shop-managed stock table (not implemented)

Recorded 2026-10-17 as the owner's intended design, for planning only — no code
yet, and the details below are not decided.

- **Seed once, then the shop owns it.** The table is initially populated from
  the lumber yard's price sheet; after that the software's user maintains it
  like any other pricing information — add, rename, reprice, remove — without
  editing code.
- **Named stock profiles.** Each stock lumber size (e.g. "5/4 x 5-1/2") gets a
  **name or ID** and a **price** (the owner said "price per foot"; today's model
  is price per *board* foot — the unit is to be settled).
- **Mouldings point at a profile.** A Moulding's `source_lumber_size` would
  reference a stock profile by name/ID instead of naming a raw (thickness,
  width) pair that must happen to match a row in a data file.

**Why:** today the link between a Moulding and its lumber price is an exact
numeric match against a Python data module. In v0.2.0, nine mouldings named
sizes the yard doesn't sell (0.5" and 1.0" thick, 1.25" x 3.5") and so were
unpriceable until the data was corrected by hand (v0.2.1). A named, editable
profile makes that link explicit and puts it where a shop would maintain it.

**Open details:** how species fit (one profile x species price grid, or a
profile per species); board foot vs linear foot; whether a Moulding keeps one
pointer per milling orientation; effective dates / snapshots (see Historical /
Snapshot Concerns above); what happens when a Moulding points at a profile
that was removed; where it is stored (see Open Questions 46 and 47).

Until then, the hand-edited `shop_pricing_data.py` stays the source of truth.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md). Unit, keying,
thickness steps, glue-ups, and grade are **settled** (see
[`../decisions/0003-milling-orientation-and-lumber-table-keying.md`](../decisions/0003-milling-orientation-and-lumber-table-keying.md)).
Stocked board widths — **resolved**: there's no generic list to define; each
Moulding's `source_lumber_size` names its own board size directly (see
[`../decisions/0007-source-lumber-size.md`](../decisions/0007-source-lumber-size.md)).
No open questions remain on Lumber itself.

---

# Pseudocode Sketch

```python
# reference lookup — current price only
def lookup_lumber_price_per_bf(lumber_table, species, nominal_thickness, nominal_width):
    row = lumber_table.get(species=species, thickness=nominal_thickness, width=nominal_width)
    return row.price_per_board_foot
```
