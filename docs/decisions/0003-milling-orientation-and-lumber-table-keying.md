# 0003 — Milling orientation, lumber-table keying, and the remaining Phase 2 details

Status: accepted (first pass — Phase 2 close-out). Date: 2026-09-16.

## Context

[ADR 0002](0002-material-and-bare-moulding-material-cost.md) settled the shape of
the bare moulding material cost but left several milling-geometry details open:
which dimension maps to required board thickness, how the lumber table is keyed,
what stock thickness steps exist, whether glue-ups or grade need modelling, and
what the waste factor actually looks like in practice. This ADR closes those out.

## Decision

**The milling convention is fixed shop practice, not a Moulding attribute:**

- **`from_board_edge`** (the common case, and the default): the moulding's
  **face width** becomes the required **board thickness**; the **overall
  height** becomes the required **board width**. A board can yield multiple
  side-by-side sticks this way (e.g. two 3/4"-wide × 2"-tall sticks from one
  3/4"-thick × 5½"-wide board). The moulding's decorative face is what was the
  board's edge.
- **`from_board_face`** (rotated 90°): **overall height** becomes the required
  board thickness; **face width** becomes the required board width. The
  decorative face is what was the board's broad face. Same lookup shape and
  formula as the standard case — only which geometry dimension is read as
  thickness vs width changes; no separate tooling-work or waste-factor delta.

**This choice lives on `DesignMoulding` (`milling_orientation`), not on
`Moulding`.** The same Moulding geometry could in principle be milled either way
for different Designs, so it is a per-design input, independent of the geometry
record — the same layering rule already used for joinery method and the float
gap.

**The lumber table is keyed by species × nominal thickness × width**, priced per
**board foot**. Stocked thickness steps: **4/4, 5/4, 6/4, 8/4**. Stocked width
steps are not yet given (open question). No grade / quality dimension.

**No kerf / oversize allowance in the formula.** Required thickness and width
each round up to the nearest stocked step; a Moulding's own geometry is expected
to already carry whatever margin it needs. Simpler than modelling a separate
allowance constant.

**No glue-ups.** The shop always buys stock already at or above the needed
thickness — a lumber row is never combined with another to reach a size.

**Multi-stick-per-board yield is folded into the waste factor, not modelled
explicitly.** The formula stays `(face width × overall height) × 12/144 × $/bf ×
waste_factor` — no packing/yield calculation. A profile's waste factor is set
with typical board-width leftover already in mind, alongside shaping chip loss.

**Waste factor is a multiplier** (e.g. `1.15`), not a percentage. Rough starting
guidance, correlated with tooling work but not derived from it by formula:

| Tooling work | Waste factor |
|---|---|
| 1–2 (simple square/rectangular) | ~1.1 |
| 3–5 (shaped: ogee, cove, …) | ~1.2–1.3 |
| 8 (complex geometry) | ~1.4–1.5 |

## Alternatives considered

- **Milling orientation as a Moulding field.** Rejected — it's a choice made
  when milling a particular piece, not a fact about the profile's geometry
  itself; keeping Moulding geometry-only stays consistent with how joinery
  method and the float gap were already placed on DesignMoulding.
- **Modelling multi-stick board yield explicitly** (computing sticks-per-board
  and dividing cost). Rejected for now — real but adds a packing/rounding
  calculation and a stocked-width assumption for comparatively little accuracy
  gain over folding it into the waste factor.
- **A kerf/oversize allowance constant on top of the raw geometry.** Rejected —
  simpler to require Moulding geometry to already include appropriate margin and
  just round up to the nearest stocked step.
- **Modelling glue-ups and lumber grade.** Rejected for now — the shop doesn't
  do either in practice; revisit if that changes.

## Consequences

- `Moulding` loses the provisional `milling_orientation` field added in ADR
  0002's round; `DesignMoulding` gains `milling_orientation`
  (`from_board_edge` default | `from_board_face`).
- The lumber lookup now takes a width as well as a thickness; `lumber.md`'s
  table and pseudocode reflect that.
- **Open:** stocked board width steps (needed to round up the "other" dimension
  in the lookup) and exact per-Moulding waste-factor values (only category
  guidance is set). See [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).
- Phase 2 is otherwise closed: the bare moulding material cost formula is fully
  specified in pseudocode, pending only those two loose numbers and, eventually,
  storage/implementation.
