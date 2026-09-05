# Frame Shop

Browser-based software for running a custom picture-framing shop. Python/FastAPI
backend owns the domain logic; React/TypeScript frontend is a thin client.

**Prototype stage.** The current slice is the central interaction: create a
Design for one piece of artwork, build/edit its framing spec while seeing a live
price and an exploded schematic, and save it.

## Documentation

| | |
|---|---|
| Why this exists, what it must become | [`docs/brief.md`](docs/brief.md) |
| Where the project stands, what's next | [`docs/roadmap.md`](docs/roadmap.md) |
| As-built architecture | [`docs/architecture/overview.md`](docs/architecture/overview.md) |
| Domain model | [`docs/architecture/domain-model.md`](docs/architecture/domain-model.md) |
| Decisions and rationale | [`docs/architecture/decisions/`](docs/architecture/decisions/) |
| Working here with AI agents | [`docs/ai-workflow.md`](docs/ai-workflow.md) |

## Prerequisites

- Python 3.12 (`brew install python@3.12`)
- Node 20+ / npm

## Setup

```bash
# backend
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed.sample_catalog

# frontend
cd ../frontend
npm install
```

## Run

```bash
# terminal 1 — backend on http://localhost:8000
cd backend && .venv/bin/uvicorn app.main:app --reload

# terminal 2 — frontend on http://localhost:5173 (proxies /api -> :8000)
cd frontend && npm run dev
```

Open http://localhost:5173.

## Test

```bash
cd backend && .venv/bin/python -m pytest -q     # backend unit + API tests
cd frontend && npx tsc -b && npm run build      # frontend typecheck + build
```

In Claude Code, `/checks` runs the whole gate (tests, lint, build, migration
round-trip).

### Screenshots without a full browser install

Headless Brave/Chrome works:

```bash
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  --headless=new --disable-gpu --window-size=1500,1000 \
  --screenshot=/tmp/frameshop.png "http://localhost:5173/#/designs/1"
```

## Layout

```
backend/    FastAPI app — api / services / domain / db, Alembic, pytest
frontend/   Vite + React + TS
docs/       brief, architecture, ADRs, roadmap
.claude/    Claude Code settings, format hook, slash commands
```
