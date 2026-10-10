# Design

> Status: **not yet specified** (Phase 8). This is a placeholder template plus the
> principles already established. Do not implement from it. See
> [`overview.md`](overview.md) and [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

# Definition

The editable framing specification being explored or developed — how a piece
should be framed. A Design is an **independently meaningful domain object**: it
can exist anonymous and unattached, be saved as a draft with no customer, or be
discarded without ever becoming an Order.

# Responsibilities

- Hold the framing structure being designed: an ordered, flexible collection of
  design-specific components. The first component type is
  [`DesignMoulding`](design-moulding.md); future siblings include glazing,
  mounting, mats, fillets, backing, fabric.
- Preserve enough framing relationships to derive multiple representations
  (outward-to-inward like traditional framing software; exploded technical
  schematic; possibly others) without being locked to one.
- Support being worked on over time — saved, reopened, revised.

# Possible Attributes

Tentative. Not a schema.

- some identifier
- lifecycle state (draft / held / quoted / accepted / discarded / archived — the
  exact set is an open question)
- a base reference the structure is built around (open question)
- base dimensions
- the collection of design components (DesignMoulding(s), later others)
- optional artwork association / metadata — or another framed object (a mirror)
- optional customer association
- **`quantity`** — **settled**: lives here, not on any individual component
  (e.g. `DesignMoulding`). Multiplies the Design's whole computed total — see
  [`pricing.md`](pricing.md). Still open: default value, and whether it means
  "N identical copies" or something more nuanced.
- timestamps

# Relationships

- **DesignMoulding** (and future components) — a Design contains them.
  Structural, core.
- **Artwork** — optional while designing. Some Designs frame a mirror or other
  product with no customer artwork at all. May become required at a later
  boundary (open question).
- **Customer** — optional while designing; may become required at the commercial
  boundary.
- **Pricing** — a Design can be priced given a pricing context; price is not
  stored as authoritative.
- **Order** — a later commercial relationship; a draft Design does not belong to
  an Order.
- **Work Order** — produced from an accepted Design at the production boundary.

Do not infer creation order from any of these.

# Derived Values

- finished / outer dimensions
- opening / sight dimensions
- the visual representations (outward-to-inward and exploded schematic) — pure
  functions of the component collection + base
- price (given a pricing context)
- material requirements

# Business Rules / Invariants

- A Design must be valid on its own, with no Customer, Artwork, Order, or Work
  Order.
- Structure is flexible: no fixed `outer_moulding` / `mat_1` / `mat_2` fields, no
  fixed maximum number of components.
- The domain model is not a generic node/edge graph — it uses framing concepts.

# Historical / Snapshot Concerns

- When a Design is accepted, the specifics its components depend on (geometry,
  material, finish, extras, offering, pricing inputs) must be snapshotted so
  later catalog/price changes do not alter accepted work. Mechanism not decided.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md) under "Design".

# Pseudocode Sketch

_None yet._
