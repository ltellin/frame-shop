# 0011 — ExtraRate combines flat and per-length charges, not a method choice

Status: accepted. Date: 2026-10-18.

## Context

ADR 0004 modelled an Extra's pricing as a `method` property — `per_length`
**or** `flat`, mutually exclusive, with a single `value`. The owner wants an
Extra to be able to charge both at once (e.g. a per-foot inlay rate plus a
flat setup/hardware fee on the same named Extra), which the method-as-choice
shape can't express without either splitting one Extra into two catalog
entries or adding a second ExtraRate per Extra — both more bookkeeping than
the data itself needs.

## Decision

**`ExtraRate` drops `method`/`value` for two independent fields,
`flat_charge` and `per_length_charge`, both defaulting to 0.0.** An Extra
sets whichever applies — one, the other, or both — rather than declaring a
method. `engine.per_length_extras_cost` and `engine.flat_extras_cost` each
just read their own field directly off every Extra's rate; there's no
branching on method left in either function.

The Length/Chop/Join scoping from ADR 0009 is unchanged: `per_length_charge`
still applies at every order form, `flat_charge` still applies at `JOIN`
only — that split was already per-component, not per-Extra, so nothing
about *which tiers charge what* changes, only that one Extra can now
participate in both.

## Alternatives considered

- **Keep `method`, add a second optional rate for the other component.**
  Rejected — two fields that mean different things (`method`+`value` vs. a
  second value) is more surface area than just two charges that are each
  either present or zero.
- **Model a "both" Extra as two catalog rows** (e.g. `"inlay"` and
  `"inlay setup fee"`). Rejected — splits one real-world Extra into two
  DesignMoulding-level choices the customer would have to pick together
  every time, when it's really one thing with two cost components.

## Consequences

- `ExtraRate(method=..., value=...)` call sites break — updated: `models.py`
  (the field change itself), `data/shop_pricing_data.py` (the example
  `EXTRA_RATES`), `engine.py` (`per_length_extras_cost`/`flat_extras_cost`),
  `tests/test_pricing_engine.py`.
- `docs/domain/extra.md`'s "Pricing method" section is revised: no longer a
  choice between two kinds of Extra, just two chargeable components an
  Extra may use either or both of.
- No change to `docs/decisions/0009-length-chop-join-order-form.md`'s
  Length/Chop/Join scoping — it already applied per-component.
