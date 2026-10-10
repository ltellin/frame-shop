# 0004 — Finish and Extra: controlled lists and pricing method

Status: accepted (first pass — Phase 3). Date: 2026-09-16.

## Context

Phase 3 specifies Finish and Extra, the next two layers on top of the bare
moulding material cost from Phase 2. Both needed: what values exist today, how
each is priced, and where the pricing data lives.

## Decision

**Finish is a small controlled list of strings**, the same pattern as Material.
Starting values: `"oil"`, `"painted"`, `"stained"` — more to be added later, at
any level of specificity (e.g. a future `"black stain"` alongside a generic
`"stained"`). No structured colour/product data for now.

**Finish is priced at a flat rate per linear foot**, looked up by name. The rate
does **not** scale with the moulding's face width — a wide profile and a narrow
one cost the same per foot to finish.

**Extra is priced by a method that's a property of the Extra itself:**
`per_length` (a $/foot rate) or `flat` (a fixed $ amount). Starting extras:
`"inlay"` (per_length) and `"matching spacer"` (per_length) — more to be added
later. This makes adding a new extra a **data change** (name + method + rate),
not a code change.

**Both Finish and Extra rates, plus Extra's `per_length` rate, use the same
billable footage** already computed for the bare moulding material cost
(`max(required_feet, minimum_feet)`) — the working assumption that a shop
finishes/inlays the whole stick before chopping and joining it. Not confirmed;
kept as an open question.

**Moulding/Extra compatibility constraints** (some profiles can't take some
extras) are real but **explicitly deferred** — not modelled now, recorded as a
noted future requirement rather than silently dropped.

**All of this reference data (lumber prices, Finish rates, Extra rates,
waste-factor guidance) is meant to be hardcoded and colocated** in one
easy-to-edit place, not scattered across the codebase or normalized into
separate database tables from the start. Exact file format is an implementation
decision, not made now.

## Alternatives considered

- **Decomposing Finish into type + colour/product fields now.** Rejected — a
  plain string is enough for the current 3 values and defers structure until a
  real need (e.g. matching a specific paint SKU) appears.
- **A fixed enum of Extra pricing methods per named extra** (hardcoding "inlay is
  always per-length" in code). Rejected — making pricing method a declared
  property of the Extra itself means new extras are pure data.
- **Face-width-scaled Finish pricing** (more surface area on a wider profile
  costs more to finish). Rejected — the owner confirmed a flat per-foot rate
  regardless of width, for simplicity.
- **Implementing Moulding/Extra compatibility now.** Rejected — real requirement,
  but out of scope for this pass; explicitly parked rather than ignored.

## Consequences

- `finish.md` and `extra.md` move from modest notes to first-pass specs.
- `pricing.md` gains `finish_cost` and `extras_cost` pseudocode, both consuming
  the same `billable_ft` as `bare_moulding_material_cost`.
- A new architecture note (`architecture/overview.md`) records the
  "hardcoded, colocated reference data" preference — it will apply again to
  future pricing inputs (e.g. labor rates, markup), not just these three.
- **Open:** whether Finish/Extra should really use billable footage vs. required
  footage; Moulding/Extra compatibility constraints; whether some Extras should
  force custom (non-Offering-standard) pricing. See
  [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).
