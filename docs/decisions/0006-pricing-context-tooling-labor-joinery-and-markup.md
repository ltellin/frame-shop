# 0006 — PricingContext, tooling-work labor, joinery, material markup, and quantity

Status: accepted (first pass — Phases 5 and 6). Date: 2026-09-16.

## Context

Phase 5 closed out the remaining DesignMoulding attribute questions (quantity's
home, joinery, the shape of a price result). Phase 6 added the last pieces of
moulding pricing: tooling-work labor, markup, and how everything is threaded
together as one `PricingContext`. This also revisited whether Offering pricing
(ADR 0005) should instead be computed via the same formula with a labor
discount — it was reconsidered and reaffirmed.

## Decision

**`PricingContext` is a real object**, not a loose bag of parameters. It bundles
every shop-configurable rate table and default (lumber prices, finish rates,
extra rates, joinery rates, tooling-work rate, default minimum footage, default
non-offering labor charge, material markup rate) and is passed as a single
argument into every pricing function. It is **instantiated from one
centralized, hand-editable location per shop** — the same colocated,
hardcoded-reference-data preference already established for lumber/finish/extra
rates. This keeps pricing *formulas* shop-independent; only the data plugged
into `PricingContext` varies shop to shop.

**Quantity lives on `Design`, not `DesignMoulding`.** It multiplies the whole
Design's computed total (the sum of all its moulding lines, plus future
component types), not any single line.

**Joinery method** vocabulary, for now: `"underpinning"` and `"splining"`
(splining priced at roughly 3× underpinning's labor). It is a **flat charge per
frame** — not per corner, not per linear foot. It **follows the Offering/custom
split**: baked into an Offering's `menu_price_per_foot` when the DesignMoulding
matches it exactly; added as its own line item when priced as custom.

**Tooling-work labor applies universally** — added on top of *both* the
Offering-priced and custom-priced paths, unlike `non_offering_labor_charge` and
joinery (which both follow the Offering/custom split). It's a rate per foot,
scaled by the Moulding's `tooling_work` value (1/2/3/5/8): a first-pass
assumption is a single rate linearly multiplied by that number, rather than a
distinct rate per level.

**Material markup** is a shop-set percentage applied specifically to the **bare
lumber material cost**, and **only on the custom path** — never to Finish,
Extras, or any labor charge, and never to an Offering-priced line (a flat menu
rate has no decomposed material portion to mark up). It will extend to other
Design materials (mats, mounting, glazing) once those components exist,
possibly as a separate rate.

**A moulding line's price is a structured breakdown, not a single number** —
e.g. `{bare_material, material_markup, finish, extras,
non_offering_labor_charge, joinery, tooling_work_labor, total}` on the custom
path, or `{offering_price, tooling_work_labor, total}` on the Offering path.
This is so a caller (e.g. a storefront) can itemize a quote, not just show one
total.

**Reaffirmed: Offering keeps its flat, independently-set `menu_price_per_foot`
(ADR 0005), rather than being computed via the same formula with a discounted
labor rate.** Reconsidered this round and kept because:
- it keeps the "what does this cost to fabricate" formula free of any
  Offering-awareness — Offering-matching becomes one independent override
  rather than a branch buried inside the cost formula;
- it matches how a shop already prices a standard product (a number they
  already know, not an abstract "batch discount" they'd have to derive);
- it gives Offering prices deliberate **stability** — they don't drift with
  every live lumber-price change the way a computed price would, which is
  usually what you want for a listed/posted product price.
- Tooling-work labor's now-universal application already gives a form of
  "shared computation" across both paths without reopening the whole formula.

## Alternatives considered

- **Passing rate tables as separate function parameters** instead of one
  `PricingContext`. Rejected — doesn't scale as more inputs (tooling rate,
  joinery rates, markup) get added, and doesn't cleanly support "one shop, one
  editable settings location."
- **Quantity on DesignMoulding.** Rejected — quantity means "make N of this
  whole piece," a Design-level concept.
- **Joinery priced per corner.** Rejected — flat per frame is simpler and
  matches how the owner actually thinks about it.
- **Offering priced via the computed formula with a labor discount.**
  Reconsidered explicitly this round; rejected again for the reasons above.
- **A single flat total price returned from pricing**, instead of a breakdown.
  Rejected — a breakdown is more useful for the owner's storefront use case.

## Consequences

- Every pricing function in `pricing.md` now takes `(design_moulding, design,
  pricing_context)` rather than a mix of ad hoc table parameters.
- `Design` gains `quantity`; `DesignMoulding` gains `joinery_method` (with real
  pricing behavior) and a structured price-breakdown shape.
- Phase 6 (the rest of moulding pricing) is now **fully specified in
  pseudocode** — a complete `price_moulding_line` exists, covering bare
  material, finish, extras, Offering-vs-custom, tooling-work labor, joinery,
  and material markup.
- **Open:** the exact tooling-work-labor formula shape (linear multiplier vs. a
  per-level rate table); stocked board widths (carried over from ADR 0003);
  whether markup ever extends to Finish/Extras or other materials. See
  [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).
