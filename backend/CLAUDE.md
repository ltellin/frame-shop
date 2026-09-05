# Backend — rules for this subtree

FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2. Python 3.12 in `.venv/`.

## Commands

```bash
.venv/bin/python -m pytest -q          # tests
.venv/bin/ruff check .                 # lint (also runs in /checks)
.venv/bin/alembic revision --autogenerate -m "..."   # after a model change
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed.sample_catalog           # reload fake catalog
```

## Layering (enforced by convention, checked in review)

```
app/api/       HTTP only — routers, request/response schemas. Thin.
app/services/  use-cases: orchestrate domain + db, own transactions & commits
app/domain/    pure Python. NO fastapi import. NO sqlalchemy import. The rules live here.
app/db/        SQLAlchemy models + session. Only services touch this.
```

If you're reaching for `from fastapi` or `from sqlalchemy` inside `app/domain/`,
stop — the logic belongs in a service, or the data belongs in a plain dataclass
in `domain/design/spec.py`.

## The Design model (ADR 0012)

A Design is a *fabrication spec*, not "art framing". Rules:

- Built around a **base rectangle** — `base_ref` (`art | sight | glass | rabbet |
  outside`) + `base_width_in`/`base_height_in`. The geometry walk seeds from
  `design.base_dimensions`.
- **No Artwork table** — `art_title` / `art_type` / `art_depth_in` / `art_notes`
  are optional columns on `design`. The art schematic layer shows only when
  `base_ref == 'art'`.
- **`type`** (`framing | mat_only | glazing_only | frame_only | canvas_stretch |
  object_box | swap | repair | other`) is a light tag: `DESIGN_TYPES` +
  `STARTER_STACKS` in `kinds.py`. It never restricts which components a design
  may contain.
- A Design may be a **loose draft** — `order_id` / `customer_id` nullable.
  `to_read_model` returns `complete: false` (null price/representations) until
  base dims exist — never build a `DesignSpec` without them.
- `component.provenance` = `shop | customer`; customer-supplied → the engine
  calls `profile.price_customer_supplied` (handling fee, no material).

## Working on framing components

Component kinds are a registry: `app/domain/design/kinds.py`. Each kind = a
Pydantic param model + a `ComponentKind` subclass (`default_layer_role`,
`consumes_product`, `rendered`, `geometry()`, `outside_in_label()`) + a
`register()` call. Pricing for a kind is a `_price_<key>` method on
`PlaceholderProfile` in `app/domain/pricing/profiles.py`. The geometry walk that
pricing and the schematic both consume is `app/domain/design/geometry.py`. Use
`/add-component-kind`.

## Images + camera (ADR 0013)

`design_image` rows + files under `FRAMESHOP_MEDIA_DIR` (`app/services/image_service.py`).
Camera capture is `app/capture/` — implement a `CaptureSource` and
`register_source()` for a real camera; the default `none` source returns 501.

## Conventions

- Money: integer cents (`app/domain/money.py`). Measurements: `Decimal` inches,
  parsed at the edge by `parse_inches` (`app/domain/measure.py`).
- Statuses are plain strings validated in the service layer, not DB enums.
- Every model change needs an Alembic migration in the same change (batch mode —
  see `alembic/env.py`).
- Keep `domain/` unit-testable with no DB; test services against an in-memory
  SQLite session (see `tests/conftest.py`).
