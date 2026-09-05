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

## Working on framing components

Component kinds are a registry: `app/domain/design/kinds.py`. Each kind = a
Pydantic param model + a `ComponentKind` subclass (`default_layer_role`,
`consumes_product`, `geometry()`, `outside_in_label()`) + a `register()` call.
Pricing for a kind is a `_price_<key>` method on `PlaceholderProfile` in
`app/domain/pricing/profiles.py`. The geometry walk that both pricing and the
schematic consume is `app/domain/design/geometry.py`. Use `/add-component-kind`.

## Conventions

- Money: integer cents (`app/domain/money.py`). Measurements: `Decimal` inches,
  parsed at the edge by `parse_inches` (`app/domain/measure.py`).
- Statuses are plain strings validated in the service layer, not DB enums.
- Every model change needs an Alembic migration in the same change.
- Keep `domain/` unit-testable with no DB; test services against an in-memory
  SQLite session (see `tests/conftest.py`).
