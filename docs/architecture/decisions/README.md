# Architecture Decision Records

Each ADR captures one decision, why it was made, and what it commits us to — so
the reasoning survives outside a chat log. Short is fine. Supersede rather than
edit once a decision has shipped.

Add one with `/new-adr <short-title>`. Use `0000-template.md`.

| # | Title | Status |
|---|---|---|
| [0001](0001-tech-stack.md) | Technology stack | accepted |
| [0002](0002-layered-architecture.md) | Layered architecture; domain has no framework imports | accepted |
| [0003](0003-design-representation.md) | Design = flat ordered typed components + kind registry | accepted |
| [0004](0004-snapshot-on-accept.md) | Snapshot on accept; historical records are immutable | accepted (design; built in slice 2) |
| [0005](0005-three-state-facets.md) | Payment / production / fulfillment are independent facets | accepted (design; built in slice 2) |
| [0006](0006-money-and-measurement.md) | Money as cents, measurements as Decimal, pricing-fact vocabulary | accepted |
| [0007](0007-catalog-vs-transaction-data.md) | Catalog reference data is separate from transaction data | accepted |
| [0008](0008-pricing-profiles.md) | Pricing is a versioned profile; Design stores no authoritative price | accepted |
| [0009](0009-numbering-scheme.md) | Order and Work Order numbering | accepted |
| [0010](0010-optimistic-concurrency-reserved.md) | Reserve `version` + `updated_at` on Design | accepted |
| [0011](0011-schematic-svg.md) | SVG for the schematic | accepted |
