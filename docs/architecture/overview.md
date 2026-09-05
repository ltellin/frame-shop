# Architecture overview (as built)

This describes the code as it stands after slice 1. For *why* each choice was
made, see `decisions/`. For *what's next*, see `../roadmap.md`.

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
    config.py          env-driven settings (FRAMESHOP_* vars)
    api/               HTTP only: health, catalog, customers, orders, designs
    services/          use-cases; own transactions + commits
      catalog_service.py   list/resolve products; the vendor-ingestion seam
      order_service.py     customer / order / artwork
      design_service.py    create, load, edit components, reprice, build read model
      errors.py            NotFoundError / DomainValidationError → 404 / 422
    domain/            pure Python — no fastapi, no sqlalchemy
      money.py         Money value object, integer cents
      measure.py       Dimensions, parse_inches (handles "16 1/2")
      design/
        spec.py            ArtworkSpec / ComponentSpec / DesignSpec / ProductResolution (dataclasses)
        kinds.py           component-kind registry + per-kind Pydantic param models
        layers.py          LayerGeometry / LayerView (shared, breaks an import cycle)
        geometry.py        walk_layers() — the one place geometry accumulates
        representations.py  to_outside_in_list(), to_exploded_layout()
      pricing/
        profiles.py        PricingProfile protocol + PlaceholderProfile (fake rates)
        engine.py          price_design(spec, profile) → PriceBreakdown
    db/
      base.py          engine, SessionLocal, Base, get_session dependency
      models.py        ORM: Customer, Order, Artwork, Design, DesignComponent, Vendor, Product
    seed/sample_catalog.py   fake vendors + products (5 vendors, ~13 products)
  alembic/             migrations (env.py wired to Base.metadata + settings)
  tests/               pytest; in-memory SQLite; ~31 tests
frontend/
  src/
    api/client.ts      the ONLY module that calls the backend
    api/types.ts       hand-written mirror of the backend read model
    state/designEditor.tsx   the one editable Design + optimistic edit + debounced PATCH
    features/home/           start-a-design form + design list
    features/design-editor/  ComponentList, ComponentParamsPanel, PricePanel, DesignEditor
    features/schematic/      Schematic.tsx + layout.ts
    theme.ts           ROLE_COLORS
```

## Request / data flow

```
User edits a component in ComponentList / ComponentParamsPanel
  → designEditor store updates local state optimistically
  → debounced PATCH /api/designs/{id}  { components: [full desired list] }
      → design_service.replace_components()  (validate kinds + params, renumber sequence,
                                              resolve parent_index → parent_component_id)
      → design_service.recompute_price()
          → build_spec(): ORM rows + catalog_service.resolve() → DesignSpec (pure data)
          → price_design(spec): walk_layers() → PlaceholderProfile → PriceBreakdown
      → design_service.to_read_model(): components + price + representations + warnings
  → store replaces local state with the authoritative response
  → PricePanel and Schematic re-render from it
```

The frontend never computes price or geometry. `layout.ts` only maps the
backend's exploded-layout model to SVG coordinates.

## The central bet — flexible Design without a generic tree

A `Design` owns an **ordered list of typed `DesignComponent` rows**:

| field | meaning |
|---|---|
| `kind` | registry key (`moulding`, `mat`, `fillet`, `glazing`, `mount`, `backing`, `spacer`, `fabric`, `service`, `other`) |
| `sequence` | 1 = outermost, contiguous, ascending toward the artwork |
| `params` | kind-specific JSON, validated on write by that kind's Pydantic model |
| `layer_role` | optional schematic-placement tag; defaults from the kind |
| `product_id` | nullable FK to `Product` |
| `parent_component_id` | nullable self-FK — used **only** where framing genuinely nests |

Everything else is **derived by pure functions** of that list:

- `to_outside_in_list()` — the traditional industry description
- `to_exploded_layout()` — the schematic model
- `price_design()` — the price

Adding a component type = one class + one `register()` in `kinds.py`. The schema
does not change. See ADR 0003.

## What is intentionally NOT here yet

Accept → snapshot → Work Order; production tasks / the 3 state facets on a Work
Order; Order financials, payments, invoices; auth; real vendor integration; real
pricing rules; OpenAPI-generated frontend types. Each has a designated home —
see `../roadmap.md` and the ADRs.
