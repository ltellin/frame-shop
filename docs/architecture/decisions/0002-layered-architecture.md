# ADR 0002 — Layered architecture; the domain has no framework imports

- **Status:** accepted
- **Date:** 2026-09-05

## Context

The brief: domain/business logic must live in Python; important framing / pricing
/ business rules must not live only in the frontend; the UI representation must
not dictate the database model. We want the rules to be testable and portable
across future interfaces.

## Decision

Four layers with a one-directional dependency rule:

```
api/       HTTP only — routers, request/response schemas. No business logic.
services/  use-cases: orchestrate domain + db, own transactions and commits.
domain/    pure Python. MUST NOT import fastapi. MUST NOT import sqlalchemy.
db/        SQLAlchemy models + session. Touched only by services.
```

`domain/` works on plain dataclasses (`domain/design/spec.py`). Services convert
ORM rows ↔ dataclasses. All framing/pricing/geometry logic lives in `domain/`
(and thin orchestration in `services/`), never in `frontend/`.

## Consequences

- `domain/` is unit-testable with no database and no HTTP.
- The same domain code can back a counter UI, a wood-shop view, a batch job, or a
  CLI without change.
- Small cost: services must map between ORM objects and dataclasses
  (`design_service.build_spec`).
- **You may not** add `from fastapi` or `from sqlalchemy` under `app/domain/`, or
  put pricing/geometry math in the frontend, without revisiting this ADR.

## Alternatives considered

- **Fat models / active-record** — faster to write, but couples rules to the ORM
  and to the DB session lifecycle, and makes "many interfaces on one model"
  harder.
- **Hexagonal / ports-and-adapters with formal interfaces** — more ceremony than
  a prototype needs; the plain layering gets 90% of the benefit.
