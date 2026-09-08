# Vendor

> Status: **lightweight template only** (Phase 15). Do not implement from it.

# Definition

A source the shop buys from. Two kinds are already in view:

- suppliers of bought-in **products** (glazing, board, hardware, possibly
  manufacturer moulding — Roma, Fotiou, Omega, Larson-Juhl, …)
- **lumber** suppliers / sources the shop buys wood from, whose prices feed
  [`Material`](material.md) pricing

# Responsibilities

_TBD._ Likely: identify a supplier, carry ordering / contact details, anchor
time-varying price data.

# Possible Attributes

Tentative. Not a schema.

- name
- kind (product supplier / lumber source)
- contact / ordering info
- lead time / ordering notes

# Relationships

- **Product** — a vendor supplies products.
- **Material / lumber price** — a lumber source is where current wood prices come
  from (future, separate concept).
- **Pricing** — vendor cost and terms feed pricing.

# Derived Values

_TBD._

# Business Rules / Invariants

- Vendor pricing and availability change; historical records must not move with
  them.

# Historical / Snapshot Concerns

- See Product and Material.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

# Pseudocode Sketch

_None yet._
