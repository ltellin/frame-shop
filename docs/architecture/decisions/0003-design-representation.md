# ADR 0003 — A Design is a flat ordered list of typed components

- **Status:** accepted — amended by [ADR 0012](0012-design-as-fabrication-spec.md)
  (adds `type`, `provenance`; artwork folds onto the Design)
- **Date:** 2026-09-05

## Context

The brief is emphatic in two directions at once:

- Do **not** lock Designs into fixed slots (`moulding`, `mat_1`, `mat_2`, `glass`…).
  Real framing has stacked mouldings, multiple mats, fillets, unusual mounts.
- Do **not** lock Designs into a single canonical linear "stack" either.
- Multiple representations (outside-to-inside description; spatial/exploded
  diagram) must be derivable from the stored model.
- Principle 8: favor flexibility through a good domain model, not a generic
  abstraction framework. Principle 9: no generic ERP engine.

## Decision

A `Design` owns an **ordered list of typed `DesignComponent` rows**:

- `kind` — a key into a **registry** (`domain/design/kinds.py`). Each kind is a
  small class: a Pydantic **param model** (validated on every write), a
  `default_layer_role`, a `consumes_product` flag, a `geometry(params, inner)`
  method, and an `outside_in_label()` method.
- `sequence` — integer, contiguous, `1` = outermost. The traditional
  outside-to-inside ordering.
- `params` — kind-specific JSON. Stored loose, **validated at the edge** by the
  kind's param model. Never a free-for-all.
- `layer_role` — optional tag for schematic placement; defaults from the kind.
- `parent_component_id` — a nullable **single** self-reference, used *only* where
  framing genuinely nests (a moulding stacked on another; a fillet inside a mat
  opening).

All representations are **pure functions** of the component list, in
`domain/design/representations.py` and `domain/design/geometry.py`:
`to_outside_in_list()`, `to_exploded_layout()`, and the pricing walk.

## Consequences

- New component type = one class + one `register()` call. **No schema change.**
- Neither a fixed-column schema nor a canonical stack is baked in; the linear
  order and the spatial view are both derived.
- `params` typing lives in code, not the DB — migrations aren't needed to evolve
  a kind's parameters, but the param model is the contract.
- **You may not** add per-kind columns to `design_component`, introduce a generic
  node/edge graph table, or let `params` bypass its kind's Pydantic model,
  without revisiting this ADR.
- Known limit: a single `sequence` int plus one parent pointer cannot fully
  encode arbitrary spatial nesting. Tracked as the top risk in `../roadmap.md`.

## Alternatives considered

- **Fixed slots** — rejected outright by the brief.
- **Generic tree/graph (nodes + edges tables)** — maximum flexibility, but it is
  the "generic abstraction framework" principle 8 warns against, and it makes
  every query and every representation harder.
- **Single canonical stack only** — can't represent a fillet that sits *inside* a
  mat window rather than simply beneath it.
