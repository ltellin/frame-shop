# Product

> Status: **lightweight template only** (Phase 15). Do not implement from it.

# Definition

A catalog entry for a **bought-in good** the shop purchases from a vendor —
glazing, mat / mount board, hardware, and possibly manufacturer-made moulding.
Carries commercial / vendor data (cost, availability, SKU) as distinct from
framing geometry.

Note: the shop's own **milled moulding** is modelled through
[`Moulding`](moulding.md) (geometry) + [`Material`](material.md) +
[`Finish`](finish.md) + [`Extra`](extra.md) + [`Offering`](offering.md), **not**
through Product. How bought-in manufacturer moulding relates to that model is an
open question.

# Responsibilities

_TBD._ Likely: identify a purchasable item, carry vendor pricing and
availability, carry enough physical data for a Design to use it.

# Possible Attributes

Tentative. Not a schema.

- vendor
- vendor SKU / item number
- manufacturer
- description
- category (glazing, board, hardware, …)
- current vendor cost + unit of pricing
- availability / discontinued status
- category-specific physical attributes

# Relationships

- **Vendor** — a Product comes from a vendor.
- **Design components** — a future component (e.g. `DesignGlazing`) may reference
  a Product.
- **Pricing** — Product cost is one input.
- **Moulding** — see the note above; the relationship to bought-in manufacturer
  moulding is unresolved.

# Derived Values

_TBD._

# Business Rules / Invariants

- Catalog data changes over time; historical transactions must not change with
  it. Mechanism deferred.

# Historical / Snapshot Concerns

- Cost, availability, and metadata all drift. Accepted work needs a snapshot of
  what was true at acceptance. Deferred.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

# Pseudocode Sketch

_None yet._
