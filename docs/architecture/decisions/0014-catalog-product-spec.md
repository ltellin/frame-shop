# ADR 0014 — Catalog products carry a per-kind physical `spec`

- **Status:** accepted
- **Date:** 2026-09-06

## Context

Designing with real mouldings needs the moulding's real dimensions stored and fed
into the geometry — not just its name and price. The same is true (later) for
mats and glazing. The shop also mills its own mouldings, which have no external
vendor SKU.

## Decision

- A `Product` row keeps its **commercial** fields (`vendor_id`, `sku`,
  `unit_cost_cents`, `unit_price_cents`, `available`, `discontinued`) and gains a
  **`spec`** JSON column for the **physical** description (renamed from the unused
  `attributes`).
- `spec` is validated per-kind by a small Pydantic model in
  `app/domain/catalog/product_kinds.py` — the same "flexible in storage, typed at
  the edges" pattern used for `DesignComponent.params` (ADR 0003). `MouldingSpec`
  today: `face_width_in`, `height_in`, `rabbet_width_in`, `rabbet_height_in`,
  `material`, `finish`. `MatSpec` / `GlazingSpec` are thin stubs.
- Reads are lenient: `catalog_service.safe_spec` logs and falls back to `{}` on a
  bad row so a live design never crashes. The catalog loader is strict:
  a moulding row missing `face_width_in` aborts the load.
- **A selected product's spec overrides typed params before geometry runs**, via
  a new `ComponentKind.effective_params(params, product)` hook (default = no
  change; moulding/fillet take `face_in` from `spec.face_width_in`). `geometry()`
  keeps its `(params, inner)` signature — the hook does the merge in one place so
  only 2 of ~10 kinds change and geometry stays trivially testable.
- `Vendor.is_house: bool` marks the shop's own mill. Its `unit_cost_cents` is the
  cost to produce and there's no external SKU to reconcile.
- Seed data moves to a hand-editable `app/seed/catalog.json` (realistic
  placeholders) loaded with upsert-by-`(vendor, sku)`.

## Consequences

- Picking "Roma Tabacchino" sizes the frame, the linear-feet price, and the
  schematic frame border from its real 1.5″ face; typing a number still works
  when no product is attached.
- A richer profile (curved / ogee / slanted) is later a nested `profile` field
  added to `MouldingSpec` — no migration, no table change, and code reading
  `face_width_in` is untouched. That's the payoff of validating a JSON blob
  instead of spreading columns.
- **You may not** add per-kind physical columns to `Product`, or make `geometry()`
  take a product argument, without revisiting this ADR.
- If "Roma's profile" and "our copy of it" need to share one profile record,
  lift `spec` into a `MouldingProfile` table that `Product` points at — the blob
  is the seam. Not now.

## Alternatives considered

- **Columns on `Product`** — a wide, sparse table (any row fills ~6 of 30).
- **A `moulding_profile` extension table now** — cleaner long-term, more moving
  parts than the prototype needs; the JSON blob defers it cheaply.
- **Free-form `attributes` dict** — no validation; the same trap ADR 0003 avoided
  for component params.
