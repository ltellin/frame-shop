# ADR 0008 — Pricing is a versioned profile; the Design stores no authoritative price

- **Status:** accepted
- **Date:** 2026-09-05

## Context

The brief: interactive editing must continuously produce a price; pricing logic
belongs in the backend/domain layer; the actual framing pricing system is **not
specified**; "create an architecture where pricing rules can evolve without
rewriting the Design model." The frontend may update optimistically for
responsiveness.

## Decision

- Pricing is a standalone module, `domain/pricing/`:
  - `PricingProfile` — a protocol: `id`, `version`, `price_layer(layer, product)`,
    `design_level_lines(design)`.
  - `PlaceholderProfile` — the only implementation today; deliberately crude,
    clearly-fake rates, `id="placeholder"`, `version=1`.
  - `price_design(spec, profile) -> PriceBreakdown` — walks `walk_layers()`,
    asks the profile to price each layer, sums, attaches notes/warnings.
- **The `Design` model holds no authoritative price** — only `price_breakdown`
  (JSON), `priced_at`, `pricing_profile_id`, `pricing_profile_version` as a
  **display cache**. The authoritative price is recomputed server-side on every
  meaningful read.
- The frontend renders the `PriceBreakdown` it is given. It may show an
  optimistic estimate but the backend response always wins.
- Any snapshot (ADR 0004) records the profile `id` + `version` used.

## Consequences

- Pricing rules can be rewritten entirely — new profile class, or a data-driven
  rate-table profile — with **zero change** to the Design schema or the component
  registry.
- Historical prices are reproducible: the profile version is on the snapshot.
- Small cost: the price is recomputed on reads rather than trusted from the row.
  Fine at prototype scale; the cache column is there if it matters later.
- **You may not** move pricing rates/rules into the frontend, or treat
  `Design.price_breakdown` as the source of truth, without revisiting this ADR.

## Alternatives considered

- **Price fields on Design/Component rows** — fast reads, but the rules leak into
  the schema and every rule change becomes a migration + backfill.
- **A rules engine / DSL now** — premature; the brief says not to invent pricing
  rules. The profile protocol is the seam; the engine can come later behind it.
