# Architecture overview (as built)

This describes the code as it stands after slice 1.5 (the design-workflow
rework — ADR 0012 / 0013). For *why* each choice was made, see `decisions/`. For
*what's next*, see `../roadmap.md`.

## Stack

| Layer | Choice | Notes |
|---|---|---|
| Backend | **FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2**, Python 3.12 | API-first JSON so many interfaces can sit on one data model. ADR 0001. |
| Frontend | **React 19 + TypeScript + Vite**, TanStack Query | Thin client. Vite dev proxy sends `/api` → `:8000`. |
| Dev DB | **SQLite** (`backend/frameshop.db`) | Postgres-compatible schema: `JSON` columns, `Decimal`, no SQLite-only SQL. ADR 0001. |
| Schematic | **Inline SVG** | ADR 0011. |

## Repository map

```
backend/
  app/
    main.py            FastAPI factory, router wiring, exception→HTTP mapping
    config.py          env-driven settings (FRAMESHOP_* vars) incl. media_dir / capture_source
    api/               HTTP only: health, catalog, customers, orders, designs, design_images
    services/          use-cases; own transactions + commits
      catalog_service.py   list/resolve products; the vendor-ingestion seam
      order_service.py     customer / order
      design_service.py    create, load, edit, reprice, add-to-order, build read model
      image_service.py     save / serve-path / delete artwork images on disk
      errors.py            NotFoundError / DomainValidationError → 404 / 422
    capture/           camera-capture abstraction (CaptureSource, NullCaptureSource, registry)
    domain/            pure Python — no fastapi, no sqlalchemy
      money.py         Money value object, integer cents
      measure.py       Dimensions, parse_inches (handles "16 1/2")
      catalog/
        product_kinds.py   per-kind physical spec models (MouldingSpec …) + registry
      design/
        spec.py            DesignSpec (base dims + type) / ComponentSpec / ArtworkSpec / ProductResolution
        kinds.py           component-kind registry + DESIGN_TYPES + STARTER_STACKS + effective_params
        layers.py          LayerGeometry / LayerView (shared, breaks an import cycle)
        geometry.py        walk_layers() + the "will it fit?" depth helpers
        representations.py  to_outside_in_list(), to_exploded_layout()
      pricing/
        profiles.py        PricingProfile protocol + PlaceholderProfile (fake rates)
        engine.py          price_design(spec, profile) → PriceBreakdown
    db/
      base.py          engine, SessionLocal, Base, get_session dependency
      models.py        ORM: Customer, Order, Design, DesignComponent, DesignImage, Vendor, Product
    seed/catalog.json + sample_catalog.py   catalog data + validating upsert loader
  alembic/             migrations (env.py wired to Base.metadata + settings)
  media/               uploaded / captured images (gitignored)
  tests/               pytest; in-memory SQLite
frontend/
  src/
    api/client.ts      the ONLY module that calls the backend
    api/types.ts       hand-written mirror of the backend read model
    nav.ts             navigate(hash); App.tsx holds the route table
    state/designEditor.tsx   the one editable Design + optimistic edit + debounced PATCH
    features/landing/        Landing.tsx — home screen + drafts list
    features/design/         NewDesignGate.tsx — pick type + dimensions → creates the draft
    features/design-editor/  DesignEditor, PiecePanel, ImagesStrip, ComponentList,
                             ComponentParamsPanel, PricePanel, SizeReadout, AddToOrderDialog
    features/schematic/      Schematic.tsx + layout.ts
    features/customers/      Customers.tsx — list + quick add
    features/orders/         Orders.tsx (list) + OrderDetail.tsx (pieces + add-another)
    theme.ts           ROLE_COLORS
```

Routes (hash): `#/` landing · `#/design/new[?order=N]` gate · `#/designs/:id[?order=N]`
editor · `#/customers` · `#/orders` · `#/orders/:id`.

## Request / data flow

```
User edits a component in ComponentList / ComponentParamsPanel
  → designEditor store updates local state optimistically
  → debounced PATCH /api/designs/{id}  { components: [full desired list] }
      → design_service.replace_components()  (validate kinds + params + provenance,
                                              renumber sequence, resolve parent_index)
      → design_service._reprice_if_complete()  (skipped if base dims are unset)
          → build_spec(): ORM rows + catalog_service.resolve() → DesignSpec (pure data)
          → price_design(spec): walk_layers() → PlaceholderProfile → PriceBreakdown
      → design_service.to_read_model(): components + price + representations + summary + warnings
  → store replaces local state with the authoritative response
  → PricePanel and Schematic re-render from it
```

The frontend never computes price or geometry. `layout.ts` only maps the
backend's exploded-layout model to SVG coordinates.

## The central bet — one flexible Design for every job

A `Design` is a *fabrication spec* built around a **base rectangle** (`base_ref` +
`base_width_in`/`base_height_in`) with an **ordered list of typed
`DesignComponent` rows**:

| field | meaning |
|---|---|
| `kind` | registry key (`moulding`, `mat`, `fillet`, `glazing`, `mount`, `backing`, `spacer`, `fabric`, `service`, `other`) |
| `sequence` | 1 = outermost, contiguous |
| `params` | kind-specific JSON, validated on write by that kind's Pydantic model |
| `layer_role` | optional schematic-placement tag; defaults from the kind |
| `product_id` | nullable FK to `Product` |
| `provenance` | `shop` \| `customer` — customer-supplied → handling fee, hatched layer (ADR 0012) |
| `parent_component_id` | nullable self-FK — used **only** where framing genuinely nests |

`Design.type` is a light tag (intake mode + starter stack + future task template;
does not gate components). Artwork is optional metadata on the Design — no Artwork
table. A Design can be a loose draft with no order/customer.

Everything else is **derived by pure functions**: `to_outside_in_list()`,
`to_exploded_layout()`, `price_design()`. Adding a component type = one class +
one `register()` in `kinds.py`; adding a job type = one `DESIGN_TYPES` +
`STARTER_STACKS` entry. The schema does not change. See ADR 0003 + 0012.

## What is intentionally NOT here yet

Accept → snapshot → Work Order; production tasks / the 3 state facets; Order
financials, payments, invoices; `order_sale_line` (retail material); real vendor
integration; real pricing rules; the `stretcher_bar` kind; production camera
drivers; OpenAPI-generated frontend types. Each has a designated home — see
`../roadmap.md` and the ADRs.
