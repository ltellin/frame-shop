# 0010 — Moulding lumber sourcing moves to three normalized tables

Status: accepted. Date: 2026-10-17.

## Context

ADR 0007 put `source_lumber_size` directly on `Moulding`, as a `(thickness,
width)` pair per milling orientation. The owner wanted this managed more like
a plain, hand-editable table instead — "a slightly less automated system,"
spreadsheet-editable and the natural backing for a simple UI later, rather
than baked into the moulding's own object definition.

The first proposal pulled `source_lumber_size` into its own CSV
(`moulding_lumber_sources.csv`, keyed by `(moulding_id, orientation)`,
repeating the raw `(thickness, width)` pair). The owner paused on this: with
that table *and* the existing lumber price table both keyed by raw
`(thickness, width)`, the two would duplicate the same dimensions with no way
to catch one drifting from the other — e.g. a typo in one table's width
wouldn't be caught against the other.

A genuine data bug surfaced while rebuilding the lumber price data as part of
this work: the original `LUMBER_PRICES` dict's "3x3" and "4x4" square
turning-stock rows were filed under the *surrounding tier's* thickness (e.g.
`("ash", 0.75, 3.0)` commented "# 3x3") instead of the correct square
dimension (`3.0, 3.0`). This had been sitting undetected in a plain
dimension-keyed dict.

## Decision

**Three interlocking tables, not two, with a shared reference table in the
middle:**

1. **`data/stock_sizes.csv`** — species-agnostic reference:
   `stock_size_id → (nominal_thickness, thickness_in, width_in)`. A board size
   is a board size regardless of species.
2. **`data/lumber_prices.csv`** — `(species, stock_size_id) → price_per_bf`
   (previously `(species, thickness_in, width_in) → price`).
3. **`data/moulding_lumber_sources.csv`** — `(moulding_id, milling_orientation)
   → stock_size_id` (previously `Moulding.source_lumber_size`).

Both (2) and (3) reference (1) by id instead of repeating raw dimensions —
this is what eliminates the duplication that triggered the reconsideration.
A typo in a stock size now has exactly one place it can occur.

**`Moulding` gains a required `id: int` field** (first field, no default).
The engine needs a stable key to join against table 3, and the catalog's own
integer id (already the `MOULDINGS` dict key) is the natural one — simpler
than inventing a second identifier. `data/moulding_catalog.py` validates at
import time that each entry's `id` matches its dict key, so copy-paste drift
fails loudly, not silently.

**`Moulding.source_lumber_size` is removed entirely.** Which lumber stock a
Moulding is milled from is no longer a fact the `Moulding` object carries at
all — it lives only in table 3, resolved at pricing time via
`PricingContext.stock_size_for(moulding.id, orientation)`.

**CSV, not a Python dict**, chosen for all three tables — specifically
because it's spreadsheet-editable and the natural backing format for a
future simple UI, without requiring any change to the pricing engine itself
when that UI arrives.

## Alternatives considered

- **A single table repeating raw `(thickness, width)`** (the original
  proposal). Rejected — this is exactly the duplication-without-a-cross-check
  problem that prompted this reconsideration.
- **Fold `stock_sizes` into `lumber_prices`** (keep thickness/width columns
  on the price table, drop the separate reference table). Rejected — the
  price table is per-species, but a stock size itself isn't; a shared
  reference table lets `moulding_lumber_sources` point at the same id without
  needing to know about species at all.
- **Keep `source_lumber_size` on `Moulding`, just change its value type to a
  `stock_size_id` string.** Rejected — the owner specifically wanted lumber
  sourcing manageable as an external, hand-editable table rather than part of
  the Moulding object's own definition.

## Consequences

- `Moulding` loses `source_lumber_size`; gains `id`. Any code constructing a
  `Moulding` must supply `id` and can no longer pass `source_lumber_size`.
- `PricingContext` gains `stock_sizes` and `moulding_lumber_sources` fields,
  and two lookup methods: `stock_size_for(moulding_id, orientation)` and the
  re-signatured `lumber_price_per_bf(species, stock_size_id)` (previously
  `(species, thickness_in, width_in)`).
- `engine.required_stock_dims_in(line)` is replaced by
  `engine.required_stock_size_id(line, pricing_context)`.
- The 3x3/4x4 square-stock dimensions are corrected as part of this
  migration (`SQ3x3` = 3.0×3.0, `SQ4x4` = 4.0×4.0 in `stock_sizes.csv`), since
  rebuilding the price data surfaced the bug described above.
- This is a breaking change to the package's public surface — see
  `backend/CHANGELOG.md` 0.3.0.
- Resolves the "how is catalog/lumber reference data loaded and updated"
  question (`docs/OPEN_QUESTIONS.md` #46) for the lumber-sourcing piece
  specifically: hand-edited CSV, not a spreadsheet import or vendor feed (not
  ruled out later, just not what's built now).
