# Domain model

_See ADR 0012 for the shape below (the Design as universal fabrication spec)._

## Entities (database tables)

```
Customer 1───* Order 1───* Design *──0..1 (self) parent_component_id via
   ▲                          │  1                DesignComponent
   │ 0..1 (loose draft)       ├──* DesignComponent *──0..1 → Product
   └──────────────────────────┤
                              └──* DesignImage

Vendor 1───* Product  ◄── (nullable) DesignComponent.product_id
```

### Customer
Contact + history. `name`, `phone?`, `email?`, `notes?`, `is_trade` (wholesale /
B2B account). Minimal now; structured to grow.

### Order
The commercial transaction container. `number` (int sequence starting at 5271),
`customer_id`, `status`, `due_date?`, `po_number?`. An Order is created when a
Design is **added to an order** (`design_service.add_to_order`) — it is *not*
auto-created. Financial fields (subtotal / discount / tax / deposit / balance)
and `order_sale_line` (retail material) are **not** here yet.

### Design — the fabrication spec
An editable spec. Owns an ordered list of `DesignComponent` and a list of
`DesignImage`. **May be a loose draft** — `order_id` and `customer_id` both
nullable. Fields:
- `type` — `framing | mat_only | glazing_only | frame_only | canvas_stretch |
  object_box | swap | repair | other`. A light tag (intake mode + starter stack
  + future task template); does not gate components. `STARTER_STACKS` /
  `DESIGN_TYPES` in `kinds.py`.
- `base_ref` (`art | sight | glass | rabbet | outside`) + `base_width_in` /
  `base_height_in` (nullable) — the rectangle the component walk is built around.
- `art_title?`, `art_description?`, `art_type?`, `art_depth_in?`, `art_notes?` —
  optional artwork metadata (dimensions are `base_*`). **No Artwork table.**
- `quantity` (default 1) — identical physical pieces (trade batches).
- `status` ∈ `draft | accepted | discarded`. Editable only while `draft`.
  "On an order" is `order_id != null`, not a status. A quote is a printed draft.
- `version` + `updated_at` — reserved for optimistic concurrency (ADR 0010).
- `supersedes_id` — reserved for revision lineage (ADR 0004).
- `price_breakdown` (JSON) + `priced_at` + `pricing_profile_id` / `_version` —
  **display cache only, never authoritative** (ADR 0008); `null` until the design
  has base dimensions.

### DesignComponent
One typed element of a Design. `design_id`, `kind`, `sequence` (contiguous,
1 = outermost), `layer_role?`, `params` (JSON, validated on write by the kind's
Pydantic model in `kinds.py`), `product_id?`, `parent_component_id?`,
`provenance` (`shop | customer` — ADR 0012). See ADR 0003.

### DesignImage
Artwork photos (ADR 0013). `design_id`, `image_id` (uuid, URL + filename stem),
`content_type`, `byte_size`, `source` (`upload | camera`), `is_primary`. Bytes on
disk under `FRAMESHOP_MEDIA_DIR`.

### Vendor / Product
Catalog **reference data** — a different concept from transaction data
(ADR 0007, 0014). `Vendor`: `name`, `code?`, `is_house` (the shop's own mill).
`Product`: `vendor_id`, `kind`, `sku`, `name`, `description`, `unit_cost_cents`,
`unit_price_cents`, `price_uom` (`per_linear_ft | per_united_in | per_sqft | each
| sheet`), `available`, `discontinued`, and **`spec`** — the physical
description, JSON validated per-kind by `domain/catalog/product_kinds.py`
(`MouldingSpec` = `face_width_in`, `height_in`, `rabbet_width_in`,
`rabbet_height_in`, `material`, `finish`). Unique on `(vendor_id, sku)`. Seeded
from `app/seed/catalog.json`.

A selected product's `spec` overrides typed component params before geometry runs
(`ComponentKind.effective_params`): pick a real moulding and its face width drives
the frame size + linear-feet price, not the manual `face_in`.

## Value objects (never tables)

- **Money** — integer cents (`domain/money.py`).
- **Dimensions** — `Decimal` inches; `united_in`, `perimeter_in`, `area_sqin`,
  `grown_by()` (`domain/measure.py`).
- **DesignSpec** (`base_width_in`/`base_height_in`, `base_ref`, `type`,
  `quantity`, optional `ArtworkSpec` metadata, components) / **ComponentSpec**
  (with `provenance`) / **ProductResolution** — plain dataclasses; the pure-data
  form services hand to the domain (`domain/design/spec.py`). Built only when the
  design has real base dimensions.
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

`walk_layers(design)` starts at `design.base_dimensions` and moves outward
(sequence descending), asking each kind's `geometry(params, inner)` for its own
footprint, its window/opening, the material it consumes, and the new running
outer size. Both `price_design` and the representation functions consume this, so
geometry math exists in exactly one place. The representation functions drop
layers whose kind has `rendered = False` (services / fees) and drop the artwork
pseudo-layer unless `base_ref == 'art'`. The math is **placeholder** — good
enough for a schematic and a demo price, not a faithful cutting model.

`to_read_model` returns `complete: false` with null price / representations /
summary when `base_width_in` / `base_height_in` are unset — the domain is never
handed a dimensionless design.

## Design → accepted → Work Order (next slice — designed, not built)

- `draft` → fully mutable, always shows **live** catalog + a fresh price.
- **Accept** (atomic service): resolve every product against live catalog → run
  the pricing engine with a pinned `PricingProfile` id+version → serialize the
  resolved spec + breakdown into an **immutable snapshot JSON** → create one (or
  `quantity`) **Work Order** per accepted Design, numbered `{order.number}-{n}`,
  holding the snapshot → set `Design.status = accepted` (locked).
- Editing an accepted Design → new Design row with `supersedes_id` → re-accept →
  new Work Order revision.
- **Invariant:** a snapshot is never mutated. Catalog/pricing changes never touch
  it. Invoices and production lists read snapshots, not live data. (ADR 0004)

## Production / payment / fulfillment (slice 2+)

Three **independent** state facets on the Work Order, never one status. Distinguish
explicit vs derived vs display state. Production is a small fixed set of
`ProductionTask` rows with kind-based prerequisites — not a workflow engine.
(ADR 0005)
