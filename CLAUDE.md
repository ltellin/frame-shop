# Frame Shop

Browser-based software for running a custom picture-framing shop. The Python /
FastAPI backend owns all domain logic; the React / TypeScript frontend is a thin
client. Prototype stage.

- **Why this project exists and what it must become:** `docs/brief.md`
- **Where we are / what's next:** `docs/roadmap.md`
- **As-built architecture:** `docs/architecture/overview.md`
- **Decisions and their rationale:** `docs/architecture/decisions/`
- **How we work with AI agents here:** `docs/ai-workflow.md`

## Run

```bash
# backend  (http://localhost:8000)
cd backend && .venv/bin/alembic upgrade head \
  && .venv/bin/python -m app.seed.sample_catalog \
  && .venv/bin/uvicorn app.main:app --reload

# frontend (http://localhost:5173, proxies /api -> :8000)
cd frontend && npm run dev
```

## Verify

Run **`/checks`** before calling any change done: backend `pytest` + `ruff`,
frontend `tsc` + `build`, Alembic migration round-trip. A PostToolUse hook
auto-formats Python files with `ruff` after each edit.

## Architecture rules (do not violate without an ADR)

- **Layering:** `api → services → domain`, `services → db`.
  `backend/app/domain/` imports **no** FastAPI and **no** SQLAlchemy.
  Framing / pricing / business rules live in `domain/` and `services/` —
  **never** in the frontend. The frontend renders numbers and a layout model the
  backend gives it. (ADR 0002)
- **A Design is a flat, ordered list of typed `DesignComponent` rows** — `kind` +
  `sequence` (outside→inside) + kind-validated JSON `params` + an optional single
  `parent_component_id`. Component kinds are a registry in
  `backend/app/domain/design/kinds.py`. The textual and schematic views are pure
  functions in `domain/design/representations.py`. Do **not** add fixed component
  columns; do **not** build a generic tree/graph. (ADR 0003)
- **Pricing** is a separate, versioned `PricingProfile` in `domain/pricing/`. The
  Design stores no authoritative price — only a display cache. (ADR 0008)
- **Money is integer cents. Measurements are `Decimal` inches.** Every schema
  change goes through an Alembic migration. (ADR 0006)
- **Catalog data (`Vendor`, `Product`) is reference data**, separate from
  transaction data. Accepted work will snapshot the resolved catalog + price;
  snapshots are immutable and historical records never change. (ADR 0004, 0007)
- Keep `CLAUDE.md` files short — they load into context every session. Depth goes
  in `docs/`.

`backend/` and `frontend/` each have their own `CLAUDE.md` with area-specific
rules.
