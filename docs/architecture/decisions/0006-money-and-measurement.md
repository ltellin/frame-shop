# ADR 0006 — Money as integer cents, measurements as Decimal, and the pricing-fact vocabulary

- **Status:** accepted
- **Date:** 2026-09-05

## Context

Framing pricing is money-sensitive and size-driven. The brief defers the actual
pricing *rules* but we still have to commit to the units those rules operate on,
because they touch the schema and the component registry.

## Decision

- **Money is an integer number of cents** everywhere — DB columns, domain,
  API. `domain/money.py` has the `Money` value object; rounding happens once,
  explicitly, when a computed amount becomes cents (`to_cents`, `ROUND_HALF_UP`).
  Never use `float` for money.
- **Measurements are `Decimal` inches.** Shop-style fractional input
  (`16 1/2`, `16-1/2`, `1/2`) is parsed to `Decimal` at the edge by
  `parse_inches` (`domain/measure.py`). DB columns are `Numeric(7,3)`.
- **Each component kind exposes a fixed vocabulary of geometry facts**, via its
  `geometry(params, inner) -> LayerGeometry`:
  `inner`, `outer`, `self_size` (footprint), `opening` (window or none),
  `linear_in` (moulding/fillet material), `area_sqin` (sheet material).
  Pricing profiles consume these — they do not re-measure.
- `Product.price_uom` is one of `per_linear_ft | per_united_in | per_sqft | each
  | sheet`.

## Consequences

- No floating-point money drift; totals are exact and reproducible.
- Pricing rules can change freely (ADR 0008) as long as they are expressed in
  terms of the fact vocabulary above.
- Adding a genuinely new pricing dimension (e.g. weight, perimeter joins) means
  extending `LayerGeometry` and every kind that should report it — a deliberate,
  visible change.
- **You may not** introduce `float` money, store measurements as strings/floats,
  or have a pricing profile compute geometry itself, without revisiting this ADR.

## Alternatives considered

- **`Decimal` dollars for money** — works, but invites inconsistent quantization;
  integer cents is unambiguous.
- **Let each kind emit arbitrary pricing inputs** — flexible, but then pricing
  profiles must know every kind's private shape; the fixed vocabulary keeps the
  engine kind-agnostic.
