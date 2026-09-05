# ADR 0010 — Reserve `version` + `updated_at` on Design for future concurrency

- **Status:** accepted
- **Date:** 2026-09-05

## Context

The brief: the app "may eventually be used simultaneously at a front counter,
wood shop, mounting/matting area, and pickup area." Two people could open the
same Design. We are **not** building multi-user concurrency in the prototype, but
retrofitting a version column onto a hot table later is disruptive.

## Decision

- `Design` carries `version` (integer, incremented on every edit in
  `design_service.update_design`) and `updated_at` (auto-updated) from slice 1.
- Nothing enforces them yet — no client sends `If-Match`, no service compares
  versions.
- When multi-user editing becomes real: PATCH requests carry the expected
  `version`; the service rejects a stale write with `409`; the frontend reloads
  and re-applies. Likely paired with the SQLite → Postgres move.

## Consequences

- The column exists and is maintained, so enabling optimistic concurrency is a
  service-logic change, not a migration on a table full of live designs.
- Tiny ongoing cost: one integer bumped per edit.
- **You may not** remove `version`/`updated_at` or stop incrementing them.

## Alternatives considered

- **Add it later when needed** — the migration itself is easy, but every existing
  row needs a sensible default and every write path needs auditing under load;
  cheaper to carry the column from the start.
- **Row locking / last-write-wins** — locking is heavy for counter use;
  last-write-wins silently loses a colleague's edits, which is exactly the
  failure mode we want to avoid.
