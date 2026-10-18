# 0009 — Length / Chop / Join order form

Status: accepted. Date: 2026-10-11.

## Context

The pricing engine so far only ever produced a finished, joined frame — a
reasonable default when the software is used inside a shop building a piece
for a customer. But the owner also uses this engine as a **moulding
supplier**, selling to other frame shops. The wholesale moulding trade has a
standard three-tier classification for how far a stick is processed before it
ships:

- **Length** — raw, uncut stock, priced per foot. No target frame size at all.
- **Chop** — cut to the four mitered pieces for a specific frame size, not
  assembled.
- **Join** — chopped *and* corner-assembled into a finished frame.

This is published, standard terminology in the trade (how real moulding
suppliers structure their price sheets) — not something invented for this
project.

## Decision

**The three tiers are additive, layered directly on the existing pricing
chain**, via a new `order_form` (`LENGTH` | `CHOP` | `JOIN`) on
`MouldingLineInput`, defaulting to `JOIN` (unchanged behavior for existing
shop-mode callers):

```
LENGTH total = bare_material + material_markup + finish + per_length_extras + tooling_work_labor
CHOP total   = LENGTH total + chop_charge
JOIN total   = matches_source_offering (JOIN only)
                 ? offering_price + tooling_work_labor
                 : CHOP total + non_offering_labor_charge + flat_extras + joinery
```

- **`tooling_work_labor` and `finish` apply at every tier.** Milling the
  profile and finishing the stick both happen before the stick is ever cut —
  unrelated to whether the customer ultimately buys it raw, chopped, or
  joined.
- **A new `chop_charge`** (flat $ per frame, mirroring how `joinery_cost`
  already works — same shape, same reasoning) is added for `CHOP` and `JOIN`.
- **`LENGTH` orders have no target frame size.** `MouldingLineInput` gains
  `requested_footage_ft`, used instead of the perimeter-from-finished-size
  calculation when `order_form` is `LENGTH`. The existing minimum-footage
  floor still applies on top of whichever number is used.
- **Offering pricing (`menu_price_per_foot`) and `non_offering_labor_charge`
  are scoped to `JOIN` only.** `matches_source_offering` returns `False`
  outright for `LENGTH`/`CHOP` lines. These are a categorically different
  product (raw or cut stock, not a retail assembled frame) — "did this
  qualify as our standard off-the-shelf frame" isn't a meaningful question to
  ask of a length of uncut moulding.
- **`Extra`'s `per_length` method applies at every tier**; the `flat` method
  applies at `JOIN` only. A continuous inlay runs along the stick whether it's
  cut or not; a flat extra (e.g. a hardware kit) describes something about the
  assembled piece.

## Alternatives considered

- **A per-foot chop charge** instead of flat-per-frame. Rejected — mirrors
  `joinery_cost`'s existing, already-approved shape; keeps the two "assembly
  stage" charges consistent with each other.
- **Letting Offering pricing apply to Length/Chop too** (a supplier commonly
  publishes a standard chopped-set price, not just an assembled one — and the
  owner expects to want this). Deferred, not rejected outright — scoped to
  `JOIN` for this pass to match what was explicitly asked for now; genuinely
  expected follow-up work, not just a hypothetical (see Open Questions #35).
- **Flat extras applying at every tier.** Rejected — a flat extra typically
  describes the finished, assembled piece; kept `JOIN`-only alongside Offering
  logic for the same reason.

## Consequences

- `models.py`: new `OrderForm` enum; `MouldingLineInput` gains `order_form`
  (default `JOIN`) and `requested_footage_ft` (required only for `LENGTH`,
  validated at construction).
- `pricing_context.py`: new `chop_charge_per_frame` field.
- `engine.py`: `billable_footage` branches on `order_form`; `extras_cost` is
  split into `per_length_extras_cost` and `flat_extras_cost`; a new
  `chop_charge()`; `matches_source_offering` gates on `order_form == JOIN`;
  `price_moulding_line` rebuilt around the tiered/additive structure above.
- **Open, and expected, not just hypothetical:** the owner anticipates wanting
  Offering to cover Length/Chop too, not just Join (a real supplier catalog
  typically publishes a standard price for all three forms of a recipe). Not
  built now — needs its own design pass (does Offering get three price points,
  or something else?) — see [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

## Correction (2026-10-18)

Extra pricing is no longer a `per_length`-or-`flat` method choice — see
[`0011-extra-rate-combines-flat-and-per-length.md`](0011-extra-rate-combines-flat-and-per-length.md).
The per-tier scoping above is unchanged, just restated per-component: an
Extra's **per-length charge** applies at every tier; its **flat charge**
applies at `JOIN` only. An Extra may use either or both.
