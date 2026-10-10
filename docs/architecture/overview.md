# Architecture Overview

Intentionally high-level. This records only the direction we are currently
committed to. It is **not** a detailed application architecture, and there is no
package structure for code that does not yet exist.

## Known direction

- **Browser-based application.**
- **Python backend.** Owns the domain and business logic.
- **JavaScript / TypeScript frontend.**
- **Relational database**, eventually. Choice of database and when it is
  introduced are not decided.
- **Clean separation** between domain / business logic and UI.
- **Pricing and business rules live outside frontend rendering code.** If the
  frontend is computing what a frame costs or how big a mat is, that logic is in
  the wrong place.
- **Domain concepts should not depend unnecessarily on the web framework.** The
  core model should be expressible in plain Python.
- The **frontend schematic visualizer** (`frontend/schematic-visualizer/`) is a
  **preserved prototype**, not an architectural constraint. Do not derive the
  domain model from it. Do not integrate it yet.
- **Domain vocabulary stays framing-specific.** No generic ERP / workflow / graph
  abstractions (`Node`, `Edge`, `WorkflowDefinition`, `TransitionRule`, a shared
  `ProfileGeometry`, …) unless a concrete framing requirement forces one and the
  human approves it. See `AGENTS.md`.
- **Pricing objects expose facts, not methods.** Moulding, Material, Finish,
  Extra, and Offering carry data a pricing engine consumes; they do not compute
  prices themselves.
- **Simple pricing reference data lives together, hardcoded, and easy to
  hand-edit.** Lumber prices, Finish per-foot rates, Extra rates, and
  waste-factor guidance are all name/key → rate lookups with no real business
  logic of their own. The owner's preference is to keep them colocated (one
  file or directory) rather than scattered, so new values can be plugged in
  without hunting through the codebase. Exact format (a Python module, JSON,
  YAML, …) is an implementation decision for whenever this is actually built —
  not decided now.

## Not decided yet

- Specific web framework, ORM, migration tool.
- Database engine.
- API style / shape.
- Frontend framework and state management for the rebuilt app.
- How the backend is layered internally beyond "domain logic is separable".
- Deployment, auth, multi-station concurrency.

## Reference points

Established framing shop software (e.g. LifeSaver) is a useful parity reference
for *what* a shop needs to do. It is not a model to copy structurally — improving
the workflow and UX is the point of this project.
