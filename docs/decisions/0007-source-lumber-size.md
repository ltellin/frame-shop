# 0007 — Moulding names its own source lumber size, per milling orientation

Status: accepted (first pass — Phase 1/2 refinement). Date: 2026-09-17.

## Context

ADR 0003 modelled the required board thickness/width as **computed** from a
Moulding's geometry (`face_width` / `overall_height`, per the milling
orientation), then rounded up to the nearest of a generic list of "stocked
steps." In practice, a shop doesn't necessarily buy the *minimum* board that
fits a profile — it may deliberately use a bigger board than strictly
necessary, and that choice varies by profile, not by a general rounding rule.
The owner's example: a 3/4"-wide square profile might be milled from 3/4"
dressed lumber, while a different, also 3/4"-wide profile might deliberately
use 1"-wide stock instead — the same "round up geometry to nearest step" rule
can't express that; it's a per-Moulding judgment call.

This also ties into a concrete, practical need: the owner has a real price list
from their lumber yard and wants a small, easily-viewed-and-edited master
record of exactly which boards get bought and what they cost — picture-frame
stock doesn't vary much, so this stays a short, hand-maintained list in
practice.

## Decision

**Each Moulding explicitly names the lumber stock size used to mill it, per
milling orientation — `source_lumber_size`.** This is a stored `(thickness,
width)` pair, editable directly on the Moulding record:

- At least one milling orientation must be defined, but neither is privileged
  — a Moulding needs a `from_board_edge` entry only if it's ever milled that
  (common) way, and a `from_board_face` entry only if it's ever milled that
  (rotated) way. **Correction (2026-10-10):** this ADR originally said
  `from_board_edge` was always required; real catalog data surfaced profiles
  (wide, shallow ones) that are only ever milled `from_board_face`, so the
  rule was loosened to "at least one, either one."
- Species is **not** part of `source_lumber_size` — that still comes from
  `Material`. `source_lumber_size` (thickness, width) + Material's species
  together select the row to read in the [`lumber.md`](../domain/lumber.md)
  master price list.

**This replaces the computed "round geometry up to the nearest stocked step"
mechanism from ADR 0003.** `required_stock_dims_in()` in
[`pricing.md`](../domain/pricing.md) is now a direct lookup —
`moulding.source_lumber_size[design_moulding.milling_orientation]` — not a
calculation from `face_width` / `overall_height`. The blank's bounding box
(`face_width × overall_height`) is still used for the *volume* calculation
(how much of that board a linear foot of moulding consumes), just not for
picking *which* board to buy.

**This also resolves the "what stocked board widths does the shop buy"
question** from ADR 0003/0005 — there's no longer a generic list to define.
Each Moulding just names its own board size, and the [`lumber.md`](../domain/lumber.md)
master price list only needs a row for whichever (species, thickness, width)
combinations actual Mouldings reference.

## Alternatives considered

- **Keep computing + rounding from geometry** (the ADR 0003 approach).
  Rejected — doesn't allow a shop to deliberately over-spec a board for a given
  profile, which is a real, common judgment call.
- **A generic "stocked widths" reference list**, separate from each Moulding.
  Rejected — redundant once every Moulding names its own board size directly;
  a generic list would just be one more thing to keep in sync.
- **Fold species into `source_lumber_size`** (so it directly names a full
  lumber row). Rejected — species is a per-DesignMoulding choice (via
  Material), independent of which Moulding geometry is used; keeping
  `source_lumber_size` species-free preserves that independence.

## Consequences

- `Moulding` gains a new field, `source_lumber_size`, keyed by milling
  orientation. `round_up_to_stocked_thickness` / `round_up_to_stocked_width`
  are removed from the pricing pseudocode.
- The [`lumber.md`](../domain/lumber.md) master price list is now understood to
  be small and shop-maintained in practice (a handful of rows), populated
  from real lumber-yard pricing data the owner already has.
- Pricing a DesignMoulding in a milling orientation its Moulding has no
  `source_lumber_size` for is an error condition (incomplete Moulding data),
  not a computation to fall back on.
- No further domain open questions remain on stocked board sizes.
