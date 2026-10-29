# Decisions

This directory holds **durable architectural and domain decisions** — the ones
that are genuinely settled and that future work should treat as fixed until
explicitly revisited.

Unresolved questions live in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md), not
here.

Records so far:

- [`0001-moulding-geometry-and-tooling-work.md`](0001-moulding-geometry-and-tooling-work.md)
- [`0002-material-and-bare-moulding-material-cost.md`](0002-material-and-bare-moulding-material-cost.md)
- [`0003-milling-orientation-and-lumber-table-keying.md`](0003-milling-orientation-and-lumber-table-keying.md)
- [`0004-finish-and-extra-pricing.md`](0004-finish-and-extra-pricing.md)
- [`0005-offering-pricing-and-non-offering-labor-charge.md`](0005-offering-pricing-and-non-offering-labor-charge.md)
- [`0006-pricing-context-tooling-labor-joinery-and-markup.md`](0006-pricing-context-tooling-labor-joinery-and-markup.md)
- [`0007-source-lumber-size.md`](0007-source-lumber-size.md)
- [`0008-finish-two-rate-pricing.md`](0008-finish-two-rate-pricing.md)
- [`0009-length-chop-join-order-form.md`](0009-length-chop-join-order-form.md)
- [`0010-moulding-lumber-sources-as-tables.md`](0010-moulding-lumber-sources-as-tables.md)
- [`0011-extra-rate-combines-flat-and-per-length.md`](0011-extra-rate-combines-flat-and-per-length.md)
- [`0012-moulding-diagram-convention.md`](0012-moulding-diagram-convention.md)

## When to add a record

Add one only when the human has actually made a decision — not when the
documentation makes an answer look obvious. When you do:

- give it a number and a short title: `0001-database-is-postgres.md`
- also reflect the decision in the relevant domain file
- remove or update the corresponding open question

## Format

Lightweight ADR style:

```
# NNNN — Title

## Context
What situation forced a decision. What constraints applied.

## Decision
What we decided, stated plainly.

## Alternatives considered
What else was on the table and why it lost.

## Consequences
What this makes easier, what it makes harder, what it commits us to.
```
