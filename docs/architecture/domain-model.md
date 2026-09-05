# Domain model

## Entities (database tables)

```
Customer 1───* Order 1───* Artwork
                 │              ▲
                 │ 1            │ referenced by
                 ▼              │
               Design *─────────┘
                 │ 1
                 ▼
           DesignComponent *──0..1 (self) parent_component_id

Vendor 1───* Product  ◄── (nullable) DesignComponent.product_id
```

### Customer
Contact + history. `name`, `phone?`, `email?`, `notes?`. Minimal now; structured
to grow.

### Order
The commercial transaction container. `number` (int sequence starting at 5271),
`customer_id`, `status` (`draft` while being built at the counter). A Design
**always** belongs to an Order; starting the first Design auto-creates a draft
Order (`order_service.get_or_create_draft_order`). Financial fields
(subtotal / discount / tax / deposit / balance) are **not** here yet — slice 2.

### Artwork
The physical piece. `order_id`, `title`, `description?`, `width_in`, `height_in`,
`depth_in?`, `notes?`. **Belongs to the Order**, referenced by a Design — so
re-designing a piece keeps one Artwork record. (ADR: see risk flags in roadmap.)

### Design
An editable specification. `order_id`, `artwork_id`, `name`, `status` ∈
`draft | held | quoted | accepted | discarded`. Owns an ordered list of
`DesignComponent`. Carries:
- `version` (int, bumped on every edit) + `updated_at` — reserved for optimistic
  concurrency later (ADR 0010).
- `supersedes_id` (nullable self-FK) — reserved for revision lineage (ADR 0004).
- `price_breakdown` (JSON) + `priced_at` + `pricing_profile_id` +
  `pricing_profile_version` — a **display cache only, never authoritative**
  (ADR 0008). Editable statuses: `draft`, `held`, `quoted`. `accepted` is locked.

### DesignComponent
One typed element of a Design. `design_id`, `kind`, `sequence` (contiguous,
1 = outermost), `layer_role?`, `params` (JSON), `product_id?`,
`parent_component_id?`. `params` is validated on write by the kind's Pydantic
model in `kinds.py`. See ADR 0003.

### Vendor / Product
Catalog **reference data** — a different concept from transaction data (ADR 0007).
`Product`: `vendor_id`, `kind`, `sku`, `name`, `description`, `unit_cost_cents`,
`unit_price_cents`, `price_uom` (`per_linear_ft | per_united_in | per_sqft | each
| sheet`), `available`, `discontinued`, `attributes` (JSON). Unique on
`(vendor_id, sku)`.

## Value objects (never tables)

- **Money** — integer cents (`domain/money.py`).
- **Dimensions** — `Decimal` inches; `united_in`, `perimeter_in`, `area_sqin`,
  `grown_by()` (`domain/measure.py`).
- **DesignSpec / ArtworkSpec / ComponentSpec / ProductResolution** — plain
  dataclasses; the pure-data form services hand to the domain (`domain/design/spec.py`).
- **LayerGeometry / LayerView** — the output of the geometry walk.
- **PriceBreakdown / PriceLine** — the pricing engine's output.

## Derived state (computed, not stored as truth)

| Derived thing | Produced by |
|---|---|
| Price | `pricing/engine.py::price_design` on demand; cached on `Design` for display |
| Outside-to-inside list | `design/representations.py::to_outside_in_list` |
| Exploded schematic model | `design/representations.py::to_exploded_layout` |
| Running package size per layer | `design/geometry.py::walk_layers` |
| Discontinued / unavailable warnings | `design_service` resolving `product_id` against live catalog at read time |
| Order totals, invoices, cut lists, "daily closing" lists | later — all from canonical Design / Work Order data |

## The geometry walk

`walk_layers(design)` starts at the artwork size and moves outward
(sequence descending), asking each kind's `geometry(params, inner)` for its own
footprint, its window/opening, the material it consumes, and the new running
outer size. Both `price_design` and the representation functions consume this, so
geometry math exists in exactly one place. The math is **placeholder** — good
enough for a schematic and a demo price, not a faithful cutting model.

## Design → accepted → Work Order (slice 2 — designed, not built)

- `draft | held | quoted` → fully mutable, always shows **live** catalog + a fresh
  price.
- **Accept** (atomic service, slice 2): resolve every product against live
  catalog → run the pricing engine with a pinned `PricingProfile` id+version →
  serialize the resolved spec + breakdown into an **immutable snapshot JSON** →
  create one **Work Order** per accepted Design/Artwork, numbered
  `{order.number}-{n}`, holding the snapshot → set `Design.status = accepted`
  (locked).
- Editing an accepted Design → new Design row with `supersedes_id` → re-accept →
  new Work Order revision.
- **Invariant:** a snapshot is never mutated. Catalog/pricing changes never touch
  it. Invoices and production lists read snapshots, not live data. (ADR 0004)

## Production / payment / fulfillment (slice 2+)

Three **independent** state facets on the Work Order, never one status. Distinguish
explicit vs derived vs display state. Production is a small fixed set of
`ProductionTask` rows with kind-based prerequisites — not a workflow engine.
(ADR 0005)
