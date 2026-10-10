# 0008 — Finish pricing: a two-rate model instead of flat per-foot

Status: accepted. Date: 2026-09-17.

## Context

ADR 0004 priced Finish as a single flat rate per linear foot. In practice,
finishing a moulding involves significant setup and cleanup labor that doesn't
scale with the piece's size — once a piece is actually being finished, its
length matters much less than that fixed overhead. A truly flat per-foot rate
overcharges small pieces relative to the labor involved, and undercharges the
fixed-cost portion of larger ones.

## Decision

**Finish pricing is a two-rate model**, keyed by Finish name:

```
finish_cost = base_rate_per_ft × minimum_footage
            + marginal_rate_per_ft × max(0, billable_footage − minimum_footage)
```

- `base_rate_per_ft` applies up to whichever **minimum footage** actually
  governs this moulding line (a Moulding-level override, or the shop default —
  the same value `billable_footage` already uses for the bare material cost).
  This is deliberately **not a new, separate "finish minimum"** — it reuses
  the existing minimum-footage mechanism as the breakpoint, so a small job's
  finish charge is naturally floored at `base_rate_per_ft × minimum_footage`.
- `marginal_rate_per_ft` (expected to be **lower** than `base_rate_per_ft`,
  enforced at construction) applies to any footage beyond that minimum.
- Still **never depends on face width** — that part of ADR 0004 stands.

`FinishRate` becomes a `(base_rate_per_ft, marginal_rate_per_ft)` pair instead
of a single float; `PricingContext.finish_rates` maps Finish name to a
`FinishRate`.

## Alternatives considered

- **Keep the flat per-foot rate** (ADR 0004). Rejected — doesn't reflect that
  setup/cleanup labor dominates a small job.
- **A genuine sub-linear curve** (e.g. cost ∝ footage^0.7). Rejected — harder
  for a shop to reason about and tune than two plain dollar rates; the
  two-rate model already captures "setup dominates, then it matters less."
- **A separate flat setup fee plus a single per-foot rate** (rather than a
  base rate applied specifically up to the minimum footage). Considered
  equivalent in spirit but rejected in favor of reusing the existing
  minimum-footage concept rather than introducing a second, parallel "setup
  fee" concept.

## Consequences

- `backend/frameshop_pricing/models.py` gains `FinishRate`; `engine.finish_cost` and
  `PricingContext.finish_rates` updated accordingly. A new
  `effective_minimum_footage()` helper is shared between `billable_footage`
  and `finish_cost` so they always agree on which minimum applies.
- `docs/domain/finish.md` and `docs/domain/pricing.md` updated.
- **Open:** should Extras' `per_length` pricing get the same two-rate
  treatment, for the same setup-labor reasoning? Not applied there — only
  Finish, so far. See [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).
