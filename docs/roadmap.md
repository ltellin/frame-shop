# Roadmap & current state

Living document. Update it when a milestone lands or a decision changes. A fresh
agent session should be able to read this + `architecture/overview.md` and know
where things stand.

_Last updated: 2026-09-05 — end of slice 1._

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
   create `WorkOrder`(s) numbered `{order.number}-{n}` → lock the Design.
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
| Payments, deposit (50% / full), Order subtotal/tax/balance | `Order` + `Payment` model, `order_service` | brief "intake workflow" step 6–7 |
| Production task graph + derived `production_state` | `domain/production/`, `ProductionTask` model | ADR 0005; tiny hard-coded template |
| Invoices, work-order sheets, labels, cut lists, "daily closing" lists | `domain/documents/` (derivation only) | all derived from canonical data; brief |
| Real vendor catalog ingestion | `app/catalog/adapters/<vendor>.py` → `catalog_service` | ADR 0007 |
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
2. **Artwork ownership** — currently Artwork belongs to the Order, referenced by
   Design. If the shop workflow turns out to attach artwork to a Design or a
   Work Order more naturally, this is a migration.
3. **Quote as status vs entity** — `Design.status = quoted` today. A
   customer-facing multi-piece quote *document* may later need Order-level
   grouping.
4. **Snapshot granularity** — invoice totals (Order level) vs production spec
   (Work Order level). Rule: compute once at accept, store per Work Order, sum to
   the Order. Don't add a second computation path.
5. **Geometry is placeholder** — `kinds.py` geometry and `PlaceholderProfile`
   rates are not real. Fine for the prototype; don't let a demo number become a
   requirement.
