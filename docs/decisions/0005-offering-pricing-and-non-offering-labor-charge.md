# 0005 — Offering pricing, exact-match rule, and the non-offering labor charge

Status: accepted (first pass — Phase 4). Date: 2026-09-16.

## Context

Phase 4 specifies Offering. The open questions were whether an Offering pins a
size, how it's priced, and what happens when a DesignMoulding sourced from an
Offering diverges from it.

## Decision

**An Offering is a component recipe, not a sized product.** It references a
Moulding, Material, Finish, and zero-or-more Extras — nothing about dimensions.
The same Offering can be built at any size a Design calls for.

**An Offering carries its own price: `menu_price_per_foot`.** This is a flat
rate the shop hand-sets on the Offering itself. When used, it **entirely
bypasses** the bare-material / finish / extras cost computation (Phases 2–3) —
it is not derived from that formula, just multiplied by whatever billable
footage the Design needs.

**A DesignMoulding gets Offering pricing only on an exact match** against its
`source_offering`'s full recipe: same Moulding, same Material, same Finish, and
the same set of Extras. **No partial credit** — any single difference (a
different finish, one extra added or removed, …) drops the entire line to
custom pricing. There is no notion of "some extras keep eligibility, others
don't."

**The custom path (fully custom, or diverged from an Offering) adds a
`non_offering_labor_charge` per foot**, on top of the computed bare-material +
finish + extras chain. This charge:
- Defaults from a shop-configured rate, stored alongside the other hardcoded
  pricing reference data (lumber, finish, extra rates).
- Is exposed on the DesignMoulding once `matches_source_offering` is false, and
  the designer can override it with their own value for that specific piece.
- Applies **identically** whether the DesignMoulding never referenced an
  Offering at all, or started from one and diverged — both are "not getting the
  batch-efficient standard price," and are not distinguished.
- Is **not** the same thing as tooling-work-derived labor (still unspecified,
  Phase 6) — it's specifically a "this isn't a standard product" surcharge, not
  a general fabrication-labor formula.

## Alternatives considered

- **Offering priced via the same computed formula, just with amortized/lower
  tooling-work labor.** Rejected — the owner chose a flat, independently-set
  menu price instead; simpler, and matches how a shop would actually list a
  standard product's price.
- **Offering pinning specific sizes** (like a retail SKU with fixed dimensions).
  Rejected — confirmed as "just component recipe," size stays a Design-specific
  input.
- **Partial/graduated matching** (some divergences keep some standard-pricing
  benefit). Rejected — exact match or not, kept deliberately binary and simple.
- **A one-time flat non-offering charge** instead of per-foot. Rejected — per
  foot matches how every other charge in the moulding line already scales with
  size.
- **Charging the upcharge only when actually diverging from a named Offering**
  (not when fully custom from the start). Rejected — confirmed to apply
  uniformly to any non-Offering-priced line.

## Consequences

- `Offering` gains `menu_price_per_foot`; still carries no dimensions.
- `DesignMoulding` gains a derived `matches_source_offering` flag and an
  optional `non_offering_labor_charge` override.
- `pricing.md` now has a full two-branch pricing decision for a moulding line
  (`price_moulding_line`), on top of Phases 2–3's bare material/finish/extras
  chain.
- Tooling-work-to-labor conversion (Phase 6) remains open and is explicitly
  distinct from this upcharge.
- **Open:** whether the source Offering identity and its `menu_price_per_foot`
  at the time are part of the acceptance snapshot; stocked Offering inventory
  (still deferred). See [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).
