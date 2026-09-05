# ADR 0001 — Technology stack

- **Status:** accepted
- **Date:** 2026-09-05

## Context

The brief wants: a browser app; a Python backend that owns domain/business logic;
clean frontend/backend separation; a relational DB; "boring, understandable
technology over unnecessary infrastructure"; and a backend shaped so different
interfaces (counter, wood shop, mounting, pickup) can eventually sit on the same
data. Framework should not be chosen just for popularity.

## Decision

- **Backend: FastAPI + SQLAlchemy 2.0 (typed mapping) + Alembic + Pydantic v2**,
  Python 3.12 in a venv.
- **Frontend: React 19 + TypeScript + Vite**, TanStack Query for server state.
  Plain CSS. Vite dev server proxies `/api` to the backend.
- **Dev database: SQLite**, with a deliberately Postgres-compatible schema —
  `JSON` columns (→ JSONB later), `Decimal`/`Numeric`, integer cents, no
  SQLite-only SQL, all schema changes via Alembic.
- Monorepo: `backend/` and `frontend/` as siblings.

## Consequences

- A JSON API is the single contract; new interfaces are new frontends, not new
  backends.
- Pydantic gives typed request/response bodies and is reused for per-component
  parameter schemas (ADR 0003). OpenAPI is available for free.
- We hand-assemble ORM + migrations + settings (vs Django's batteries). Accepted:
  keeps the domain layer loosely coupled to the framework, which the brief's
  "UI must not dictate the DB model" principle rewards.
- Moving to Postgres later should be a config change plus a test pass, not a
  rewrite.
- No admin UI yet; a seed script covers catalog data for the prototype.

## Alternatives considered

- **Django + DRF** — admin UI and batteries would speed catalog CRUD, but tighter
  model/framework coupling and heavier conventions work against the separation
  the brief stresses.
- **Flask** — more hand-assembly than FastAPI for no gain here.
- **Postgres from day one** — matches the eventual multi-station reality but adds
  infrastructure now, against the "no unnecessary infrastructure" preference.
- **Vue / Svelte** — fine choices; React chosen for ecosystem size and SVG
  tooling familiarity.
