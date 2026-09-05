# ADR 0005 — Payment, production, and fulfillment are independent state facets

- **Status:** accepted (design decision; implemented in slice 2)
- **Date:** 2026-09-05

## Context

The brief: "financial state, production state, and fulfillment state should not
be collapsed into one giant status value." A job can be simultaneously
`production: assembled`, `payment: deposit paid`, `fulfillment: in shop`. Also:
minimize worker "touches"; distinguish explicit vs derived vs display state; do
not model production as one rigid sequential state machine; do not build a
generic workflow engine.

## Decision

- A Work Order carries **three separate columns**: `production_state`,
  `payment_state`, `fulfillment_state`. Never one combined status.
- Three kinds of state, by origin:
  - **explicit** — a worker recorded it (a leaf task marked done);
  - **derived** — the system infers it from prerequisites (frame ready + art
    ready ⇒ `ready_to_fit`);
  - **display** — a simpler label the UI shows.
- Production = a small **fixed set** of `ProductionTask` rows per Work Order from
  a hard-coded template (e.g. `frame_fabrication`, `art_prep`, `fit_assembly`
  with `fit_assembly` depending on the other two). Workers touch only leaf tasks;
  `production_state` is derived. Frame and artwork work proceed in **parallel**.

## Consequences

- Reporting and UI can ask one facet without untangling the others.
- Fewer worker touches: leaf tasks only; higher-level state is computed.
- The task template stays tiny and lives in Python. Not user-configurable, no
  assignment, no per-area queues in the prototype.
- **You may not** collapse the three facets into one status, or turn the task
  template into a generic configurable workflow engine, without revisiting this
  ADR.
- Nothing in the slice-1 schema blocks this — Work Order and its states simply do
  not exist yet.

## Alternatives considered

- **One `status` enum** — what LifeSaver-era software does; the brief explicitly
  rejects it.
- **A generic workflow/BPM engine** — principle 9 ("no generic ERP engine") and
  the "do not over-engineer" instruction rule it out.
