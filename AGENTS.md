# AGENTS.md

Instructions and navigation for coding agents working in this repo. Keep this
file short. The encyclopedia is `docs/`, not here.

## What this project is

A browser-based ERP / order-management / production system for a custom
picture-framing shop. It is being **restarted deliberately**: domain model first,
one concept at a time, implementation kept behind understanding.

## Read before you work

1. `docs/domain/overview.md` — relationship map and glossary. Always first.
2. The specific `docs/domain/<concept>.md` for whatever you are about to touch.
3. `docs/OPEN_QUESTIONS.md` — what is deliberately undecided.
4. `docs/roadmap/roadmap.md` — where we are in the sequence.
5. `docs/decisions/` — settled decisions (currently empty).

## How to work here

- **Implement only the explicitly requested scope.** Do not build neighboring
  systems because they seem like the obvious next step.
- **Specify before implementing.** SPECIFY → IMPLEMENT → INTEGRATE are separate
  stages and are not collapsed.
- **Do not turn conceptual documents into database tables automatically.** A noun
  in the docs is not a table, a model, an endpoint, or a component until asked.
- **Prefer framing-domain terminology** — `Moulding`, `Material`, `Finish`,
  `Extra`, `Offering`, `DesignMoulding`, `Strainer`, `Order`, `WorkOrder`,
  `ProductionOperation` — not `Node`, `Edge`, `Entity`, `Resource`,
  `WorkflowDefinition`, `TransitionRule`, `DynamicProperty`.
- **Do not introduce generic ERP / workflow / graph abstractions** (including a
  shared `ProfileGeometry` for Moulding + Strainer). If you think one is
  genuinely necessary, stop and explain: (1) the concrete framing requirement
  that needs it, (2) why a simpler framing-specific model cannot represent it,
  (3) the complexity it adds. Wait for explicit approval.
- **Preserve unresolved questions.** Only the human resolves an open question.
- **Update the docs when a real decision is made** — the domain file, the open
  questions list, and `docs/decisions/` as appropriate.
- **`frontend/schematic-visualizer/` is a preserved prototype.** Do not refactor,
  rewrite, integrate, move, or delete it unless explicitly asked. Do not infer
  domain architecture from it.
- **Do not install dependencies** without a one-line justification given first.

## Domain guardrails

- **Model business boundaries, not screen sequence.** The domain model does not
  care which screen the user started on. It cares what information becomes
  required when something crosses a boundary — quoted, accepted, ordered,
  produced.
- **Do not infer workflow order from domain relationships.** A relationship such
  as `Design → Customer` does **not** imply that a Customer must exist before a
  Design. Check the relevant domain spec for whether a relationship is required,
  optional, or required only at a later business boundary.
- **Do not assume Customer or Artwork must exist before Design.** A Design can be
  anonymous, unattached, drafted, and discarded on its own. Some Designs frame a
  mirror or other product with no artwork at all.
- A saved draft Design is **not** an Order or a Work Order.
- **An Offering is a deliberate shop-standard configuration, not a requirement
  for custom fabrication.** Do not reinterpret Offering as merely a preset. Do
  not require a `DesignMoulding` to originate from an Offering.
- **Moulding describes geometry / fabrication characteristics only.** Material,
  Finish, and Extras belong to the configured `DesignMoulding` / `Offering`
  layer, not to `Moulding` — do not move Material into Moulding unless the domain
  spec is explicitly changed.

## Stop-and-explain rule

**If a requested feature cannot be represented cleanly by the existing domain
model, stop and explain the conflict before changing the architecture.** Flag any
request that would require a fundamental change to an existing domain assumption.
