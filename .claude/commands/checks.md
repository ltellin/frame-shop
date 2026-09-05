---
description: Full verification gate — backend tests + lint, frontend typecheck + build, migration round-trip
---
Run the project's verification gate. Run each step in order. **Stop at the first
failure**, show the failing output, and do not continue. Report a concise
pass/fail summary at the end.

1. Backend tests:
   `cd backend && .venv/bin/python -m pytest -q`
2. Backend lint:
   `cd backend && .venv/bin/ruff check .`
3. Frontend typecheck:
   `cd frontend && npx tsc -b`
4. Frontend build:
   `cd frontend && npm run build`
5. Migration round-trip on a throwaway database:
   `cd backend && FRAMESHOP_DATABASE_URL="sqlite+pysqlite:////tmp/frameshop_checks.db" .venv/bin/alembic upgrade head && FRAMESHOP_DATABASE_URL="sqlite+pysqlite:////tmp/frameshop_checks.db" .venv/bin/alembic downgrade base && rm -f /tmp/frameshop_checks.db`

If all five pass, say so plainly.
