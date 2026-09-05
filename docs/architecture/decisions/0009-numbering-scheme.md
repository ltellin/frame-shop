# ADR 0009 — Order and Work Order numbering

- **Status:** accepted
- **Date:** 2026-09-05

## Context

The brief's example: `Order #5271` with Work Orders `#5271-1`, `#5271-2`,
`#5271-3` — one per physical piece. Numbers are customer-facing (spoken at the
counter, written on artwork tags) and must be stable and human-friendly.

## Decision

- `Order.number` — an integer sequence, unique, indexed, starting at **5271**
  (`order_service._FIRST_ORDER_NUMBER`, a nod to the brief). Assigned at Order
  creation. Separate from the surrogate `Order.id`.
- `WorkOrder` number (slice 2) — the string `"{order.number}-{n}"` where `n` is a
  1-based counter within the Order.
- Internal foreign keys use surrogate `id`s, never the display number.

## Consequences

- Numbers are short, sequential, and reflect the Order → piece hierarchy the
  brief describes.
- The `-n` suffix is a display convention; the Work Order still has its own `id`
  and its own independent state (ADR 0005).
- **You may not** use `Order.number` / Work Order numbers as foreign keys.
- Revisit if the shop wants per-year resets, branch prefixes, or a different
  starting point.

## Alternatives considered

- **Expose the surrogate `id`** — leaks internal counters, no hierarchy in the
  number, awkward if IDs ever get reused across environments.
- **UUIDs** — not human-friendly; unusable at a counter.
