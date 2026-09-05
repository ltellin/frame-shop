# ADR 0012 — A Design is a universal fabrication spec

- **Status:** accepted
- **Date:** 2026-09-05
- **Amends:** ADR 0003 (adds `type`, `provenance`), ADR 0009 (a Design may be a loose draft, not always on an Order)

## Context

The original model assumed every Design was art framing sitting on an Order, and
required customer + artwork up front. Real shop scenarios break that: phone
quotes with no artwork, trade orders of assembled frames / chops, mat-only and
glass-only cuts, canvas stretching, shadowboxes, art swaps, customer-supplied
frames, and repairs. See `docs/brief.md` and the scenario list in the slice-1.5
planning discussion.

## Decision

**Model 2 — one flexible Design, a light `type` tag, sale-lines for retail.**

- A **Design** is a *fabrication specification*: an ordered list of typed
  components built around a **primary opening**. It produces one or more physical
  pieces. Artwork is optional.
- **`base_ref` + `base_width_in`/`base_height_in`** — every design is built
  around one rectangle; `base_ref` (`art | sight | glass | rabbet | outside`)
  says what it represents. The geometry walk seeds from it.
- **Optional art metadata** lives on the Design (`art_title`, `art_type`,
  `art_depth_in`, `art_notes`). There is **no Artwork table**. A first-class
  "Piece" can be reintroduced at the Work Order snapshot step if production
  tagging needs it.
- **`Design.type`** is a *light* tag. It (a) picks the intake mode — which base
  dimension is asked for, whether the art block shows — (b) seeds a starter
  component stack (`STARTER_STACKS` in `kinds.py`), and (c) will select a
  production task template later. It does **not** restrict which components a
  design may contain. Values: `framing, mat_only, glazing_only, frame_only,
  canvas_stretch, object_box, swap, repair, other`.
- **`Design.quantity`** (default 1) — trade batches ("this spec × 10").
- **`component.provenance`** = `shop` | `customer`. Customer-supplied components
  price via a flat handling fee (`PlaceholderProfile.price_customer_supplied`),
  carry no material cost, are excluded from cut/purchase lists, and render
  hatched with a "customer's" label.
- **A Design may be a loose draft** — `order_id` nullable, plus a nullable
  `customer_id` so a quote can carry a name without an order. It is created
  (autosaved, Gmail-style) as soon as base dimensions are entered; leaving the
  page keeps it. Statuses collapse to `draft | accepted | discarded` (`held` /
  `quoted` are gone — a quote is a printed draft).
- **Retail material sold as-is** (an uncut stick, a full sheet of glass) is a
  **sale-line on the Order**, not a Design. `order_sale_line` +
  `PricingProfile.price_sale_line` are designed but not yet built.
- **Services / fees are line items, not schematic layers** (`ComponentKind.rendered`).

## Consequences

- One pricing engine, one geometry walk, one schematic, one component model serve
  every job type. `type` is ergonomics, not architecture — two designs of
  different types have the same table shape.
- The read model reports `complete: false` (null price / representations) until
  base dimensions exist; the domain is never handed a dimensionless design.
- **You may not**: add per-type or per-kind columns to `design` /
  `design_component`; gate components by `type`; reintroduce a required Artwork
  table; make retail material flow through Design — without revisiting this ADR.
- The future **`Job` layer** (Order → Job → Design, where a material sale is a
  Job with no Design) stays a clean migration: `type` / `quantity` / `order_id`
  move from Design to Job.

## Alternatives considered

- **Design stays art-framing; separate entities for material sales / trade /
  repair** — rejected: massive duplication of pricing, schematic, component
  model; the brief wants mats/glass/etc. on the same system.
- **A `Job` layer now** — the cleaner long-term shape, but an extra table and
  more indirection on the design page than the prototype needs. Deferred with the
  seam documented.
- **`type` also constrains allowed components** — closer to the "fixed slots" the
  brief warns against; the light tag keeps full flexibility.
