# Work Order

> Status: **not yet specified.** Lightweight template only. Do not implement from
> it.

# Definition

Represents one physical finished piece that the shop has committed to producing,
derived from an accepted Design. Production-facing.

# Responsibilities

_TBD._ Likely: carry the frozen specification to build from, track production
operations and their state, drive material requirements and production lists.

# Possible Attributes

Tentative. Not a schema.

- work order number
- the accepted Design it derives from
- a snapshot of the specification (products, prices, rules) as of acceptance
- production state (independent facet)
- fulfillment state (independent facet)

# Relationships

- **Design** — a Work Order is produced from one accepted Design.
- **Order** — a Work Order belongs to the Order that committed it.
- **Production Operation** — the steps performed against this Work Order.
- **Artwork** — the physical piece must be in hand to produce; timing of that
  requirement is an open question.

# Derived Values

- material requirements
- production / fulfillment status (from operation state, not one stored field)
- what appears on daily production/pick/cut lists — derived, never a stored list
  as source of truth

# Business Rules / Invariants

- A Work Order comes from an **accepted** Design, not a draft.
- Its specification snapshot does not change when catalog or pricing data
  changes.

# Historical / Snapshot Concerns

- This is where the acceptance snapshot lives (mechanism deferred). Historical
  specs must not drift.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

# Pseudocode Sketch

_None yet._
