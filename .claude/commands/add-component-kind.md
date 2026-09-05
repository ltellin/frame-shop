---
description: Add a new framing component kind to the domain (registry + pricing + tests)
argument-hint: <kind-key>  e.g. liner, spacer, easel-back
---
Add a new framing component kind: **$ARGUMENTS**

Read `docs/architecture/decisions/0003-design-representation.md` and
`0006-money-and-measurement.md` first. Then:

1. **`backend/app/domain/design/kinds.py`**
   - Add a Pydantic param model (`model_config = ConfigDict(extra="forbid")`,
     typed fields with sensible defaults and constraints).
   - Add a `ComponentKind` subclass: `key`, `label`, `param_model`,
     `default_layer_role` (one of `LAYER_ROLES`), `consumes_product`, and — if it
     affects package size — a `geometry(params, inner) -> LayerGeometry`
     (default is a same-size, no-material layer).
   - Add the class to the `for _cls in (...)` registration tuple.
2. **`backend/app/domain/pricing/profiles.py`**
   - Add a `_price_<key>(self, layer, product) -> LayerPrice` method to
     `PlaceholderProfile` (crude placeholder math is fine; label it).
3. **`backend/app/seed/sample_catalog.py`** — if `consumes_product` is true, add
   a couple of sample `Product` rows for this kind.
4. **Tests** — extend `backend/tests/test_pricing.py` (a known spec → a known
   amount) and `backend/tests/test_representations.py` (the kind appears in the
   outside-in list and the exploded layout in the right place).
5. Run `/checks`.
6. If the new kind introduces a genuinely new geometry fact or pricing
   dimension, note it — that may warrant an ADR (`/new-adr`).

The frontend needs **no change** — it reads the kind list and param schema from
`/api/catalog/component-kinds`.
