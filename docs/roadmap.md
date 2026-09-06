# Roadmap & current state

Living document. Update it when a milestone lands or a decision changes. A fresh
agent session should be able to read this + `architecture/overview.md` and know
where things stand.

_Last updated: 2026-09-06._

---

## Real moulding catalog — DONE

ADR 0014. `Product.spec` (per-kind physical description, JSON validated by
`domain/catalog/product_kinds.py`); `Vendor.is_house`; `attributes` → `spec`
rename. A selected moulding's real face width drives the frame geometry + price
via `ComponentKind.effective_params`. Seed moved to hand-editable
`app/seed/catalog.json` (realistic placeholders — correct + extend). A
"will it fit?" warning compares the stack depth to the moulding's
`rabbet_height_in`. Frontend: picker shows face width; profile shown read-only;
`face_in` hidden when a product is selected.

**Next for the catalog:** a CSV/spreadsheet importer (`app/catalog/adapters/`) and
a browser catalog-admin page — both still deferred (see backlog).

---

## Slice 1.5 — design as universal fabrication spec — DONE

ADR 0012 + 0013. Rework so a design can be started with zero upfront info and
covers every shop scenario (quotes, trade, mat/glass-only, swap, repair).

- **Schema**: dropped the `artwork` table (folded onto `design` as `base_*` +
  `art_*`); `design` gains `type`, `quantity`, nullable `order_id` + `customer_id`;
  `design_component.provenance`; new `design_image` table; `order.due_date` /
  `po_number`; `customer.is_trade`. Statuses → `draft | accepted | discarded`.
- **Domain**: geometry seeds from `base_dimensions`; art layer only when
  `base_ref == 'art'`; services excluded from the schematic (`rendered`);
  `DESIGN_TYPES` + `STARTER_STACKS`; customer-supplied handling pricing.
- **API**: lenient `POST /api/designs` (loose draft OK); `to_read_model` reports
  `complete: false` + a `summary` (finished size); `POST /api/designs/{id}/add-to-order`;
  `/api/designs/{id}/images` (upload / list / serve / delete / **capture** → 501);
  `/api/catalog/design-types`.
- **Frontend**: `#/design/new` is a small "what + dimensions" gate that autosaves
  the draft and drops into the editor; editor gained the **Piece panel** (type /
  base dims / art / quantity / images), a **finished-size readout**, a
  **Shop/Customer-supplied** toggle, an **Add-to-order dialog**, and
  `#/orders/:id` **OrderDetail** with "add another design". Landing shows a
  **Drafts** list. `NewDesign` form deleted.
- Backend tests green; frontend tsc + build green; migration round-trips.

### Known rough edges (not blockers)

- Schematic still cramped with many layers; single-layer designs (mat-only) look
  sparse. Presentation-only — `frontend/src/features/schematic/layout.ts`.
- `src/api/types.ts` is hand-maintained — keep in sync with `to_read_model`.
- `POST /api/designs` auto-creates on the frontend after a 700ms debounce on both
  dimensions; a fat-fingered dimension makes a draft that's then corrected in the
  editor. Acceptable; revisit if it annoys.

---

## Slice 1 — interactive Design editor — DONE

> Create a Design for one piece of artwork, interactively build/edit its framing
> spec while seeing its price and a schematic, and save it (draft / hold).

Built and committed:

- Backend: catalog (Vendor/Product) + seed; Customer/Order/Artwork; Design +
  DesignComponent with the kind registry (10 kinds); geometry walk; placeholder
  pricing engine; outside-in + exploded representations; `GET/POST/PATCH
  /api/designs`. ~31 pytest tests. Alembic initial migration.
- Frontend: home (start-a-design form + design list); design editor with
  ComponentList (add/remove/reorder/select), schema-driven ComponentParamsPanel
  (with catalog product picker), PricePanel; SVG exploded Schematic with
  list↔schematic selection sync; optimistic edit + debounced PATCH + reconcile;
  status controls (draft/hold/quote/discard); hash routing.
- Persists to SQLite. Discontinued-product warning on load.

Added after slice 1:

- **Landing page** (`#/`) with three entry points: Make a Design, Customers,
  Orders. Hash routing in `App.tsx` + `nav.ts`.
- **Customers page** (`#/customers`) — list with order counts + quick-add form.
  Backend `GET /api/customers` now includes `order_count`.
- **Orders page** (`#/orders`) — order list (number, customer, status, piece
  count) expanding to the pieces/designs on each, linking into the editor. New
  backend `GET /api/orders` + `customer_name`/`designs` on the order detail.

### Known rough edges (not blockers)

- **Schematic layout is cramped** with 5+ layers and leader lines can cross.
  Presentation-only — tune `frontend/src/features/schematic/layout.ts`
  (`GAP_Y`, `SHEAR`, `MAX_LAYER_W`, label packing). ADR 0011.
- Frontend API types are **hand-maintained** in `src/api/types.ts`. Keep in sync
  with the backend read model on every change.
- `test`-style deprecation warnings from Starlette TestClient — cosmetic.

---

## Slice 2 — accept → Work Order (NEXT)

Design is in `architecture/domain-model.md` and ADRs 0004, 0005, 0009. Scope:

1. `WorkOrder` model + `services/work_order_service` — accept a Design atomically:
   resolve catalog → price with pinned profile → write immutable snapshot JSON →
   create `WorkOrder`(s) numbered `{order.number}-{n}` (one, or `quantity`) →
   lock the Design.
2. Migration for `work_order` (+ `production_state`, `payment_state`,
   `fulfillment_state` columns, default values only for now).
3. `POST /api/designs/{id}/accept`; `GET /api/work-orders/{id}`; list on an Order.
4. Frontend: an "Accept" action → Work Order card showing the schematic
   fingerprint + number + the three state pills.
5. Tests: accept freezes the spec; a later catalog price change does **not**
   alter the snapshot; re-accept via `supersedes_id` produces a revision.

Explicitly still out: payments/deposits, Order financial rollups, production task
graph, invoices — those are slice 3+.

---

## Backlog / deferred (with a designated home)

| Item | Where it will live | Notes |
|---|---|---|
| `order_sale_line` — retail material sold as-is | `order_service` + `OrderDetail`; `PricingProfile.price_sale_line` stub exists | ADR 0012 |
| `stretcher_bar` kind + real `canvas_stretch` / `object_box` stacks | `kinds.py` registry + `STARTER_STACKS` | ADR 0012 |
| `chop_only` type (linear-feet intake, no rectangle) | needs a non-`base_ref` intake | ADR 0012 |
| Production camera driver (ceiling rig) | `app/capture/` — a new `CaptureSource` | ADR 0013 |
| Image thumbnails / EXIF / named views | `image_service` + Pillow | ADR 0013 |
| `Job` layer between Order and Design | migrate `type`/`quantity`/`order_id` off Design | ADR 0012 |
| Payments, deposit (50% / full), Order subtotal/tax/balance | `Order` + `Payment` model, `order_service` | brief "intake workflow" step 6–7 |
| Production task graph + derived `production_state` | `domain/production/`, `ProductionTask` model | ADR 0005; tiny hard-coded template |
| Invoices, work-order sheets, labels, cut lists, "daily closing" lists | `domain/documents/` (derivation only) | all derived from canonical data; brief |
| CSV / spreadsheet catalog importer | `app/catalog/adapters/csv.py` → same shape as `catalog.json` | ADR 0007, 0014 |
| Browser catalog-admin page (`#/catalog`) | add/edit vendors + products + specs | ADR 0014 |
| Real vendor catalog ingestion (live feeds) | `app/catalog/adapters/<vendor>.py` → `catalog_service` | ADR 0007 |
| Real pricing rules / rate tables | new `PricingProfile` implementation | ADR 0008; no schema change |
| OpenAPI-generated frontend types | replace hand-written `src/api/types.ts` | via `openapi-typescript` |
| SQLite → Postgres | `config.py` `database_url` | pair with optimistic concurrency (ADR 0010) |
| Multi-user optimistic concurrency | `design_service.update_design` + `If-Match` | ADR 0010; column already exists |
| Auth / permissions / roles | new middleware layer | out of scope until multi-station is real |

---

## Open risks / things to watch

1. **`sequence` (linear) vs true spatial nesting** — the top schema-pressure
   point. A single `sequence` int + one `parent_component_id` can't fully encode
   e.g. a fillet *inside* a mat opening vs. simply beneath it. The early
   schematic is approximate on purpose. Revisit ADR 0003 before the schematic
   gets sophisticated or before production cut lists depend on exact nesting.
2. **Artwork ownership** — RESOLVED (ADR 0012): artwork is optional metadata on
   the Design; no table. A first-class "Piece" may return at the Work Order
   snapshot step if production tagging needs it.
3. **Quote as status vs entity** — RESOLVED (ADR 0012): a quote is a printed
   draft (`status = draft`, optionally with a `customer_id`). A customer-facing
   multi-piece quote *document* would derive from an Order.
6. **`base_ref` intake for non-rectangular jobs** — `chop_only` (linear feet) has
   no `base_ref` that fits; kept out of the type list until built.
4. **Snapshot granularity** — invoice totals (Order level) vs production spec
   (Work Order level). Rule: compute once at accept, store per Work Order, sum to
   the Order. Don't add a second computation path.
5. **Geometry is placeholder** — `kinds.py` geometry and `PlaceholderProfile`
   rates are not real. Fine for the prototype; don't let a demo number become a
   requirement.
