# Order

> Status: **not yet specified.** Lightweight template only. Do not implement from
> it.

# Definition

The customer-facing commercial transaction — the work a customer has agreed to.
Occurs at a commercial boundary, after one or more Designs are accepted. An Order
is roughly a grouping of accepted work for one customer; more can be added over
time.

# Responsibilities

_TBD._ Likely: group accepted work, hold customer association, carry commercial
data (totals, due dates, PO / trade references), track payment state.

# Possible Attributes

Tentative. Not a schema.

- order number
- customer (required at this boundary)
- the accepted Designs / line items it covers
- due date(s)
- payment state (independent facet)
- trade PO / reference

# Relationships

- **Customer** — required for an Order (a commercial boundary requirement).
- **Design** — accepted Designs participate in an Order. A draft Design does not.
- **Work Order** — an Order's committed pieces generate Work Orders.
- **Payment** — payment state is tracked but is its own concern, not one status.

# Derived Values

- totals (from priced line items)
- overall payment / production / fulfillment status (independent facets, derived
  from constituent state — not one stored field)

# Business Rules / Invariants

- An Order requires a Customer.
- A saved draft Design is not automatically an Order.

# Historical / Snapshot Concerns

- Line-item pricing and product selections must be fixed at acceptance so later
  catalog/price changes don't alter the Order. Deferred.

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

# Pseudocode Sketch

_None yet._
