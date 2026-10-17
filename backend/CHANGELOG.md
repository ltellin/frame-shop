# Changelog

All notable changes to `frameshop-pricing` are recorded here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions
follow [semver](https://semver.org/).

## 0.2.1 — 2026-10-17

Data fix: nine catalog mouldings could not be priced because their
`source_lumber_size` named stock the lumber yard doesn't sell (0.5" and 1.0"
thick, 1.25" x 3.5") and so had no row in `LUMBER_PRICES`.

- 1001, 1002: now milled from 4/4 S4S x 3-1/2" (0.75, 3.5).
- 3001-3006: now milled from 5/4 S4S x 5-1/2" (1.0625, 5.5), ripped.
- 4001: now milled `from_board_face` from 5/4 S4S x 5-1/2" (1.0625, 5.5).
- Known gap: ash has no 5/4 x 5-1/2" row, so 3001-3006 and 4001 are still
  unpriceable in ash until that row is added.
- New test: every catalog moulding has a cherry lumber price.

## 0.2.0 — 2026-10-11

Adds **Length / Chop / Join** wholesale order-form pricing — the standard
moulding-trade classification for how far a stick is processed before it
ships. See `docs/decisions/0009-length-chop-join-order-form.md`.

- `MouldingLineInput.order_form` (`LENGTH` | `CHOP` | `JOIN`, default `JOIN` —
  no behavior change for existing shop-mode callers) and
  `requested_footage_ft` (for `LENGTH`, which has no target frame size;
  `finished_width_in`/`finished_height_in` are now optional, required only
  for `CHOP`/`JOIN`).
- New `PricingContext.chop_charge_per_frame`, added for `CHOP` and `JOIN`.
- Offering pricing and `non_offering_labor_charge` are now `JOIN`-only;
  `matches_source_offering` returns `False` for any other order form.
- `extras_cost` split into `per_length_extras_cost` (every order form) and
  `flat_extras_cost` (`JOIN` only).
- **Breaking:** `extras_cost` removed, replaced by the two functions above.
  `MouldingLineInput.finished_width_in`/`finished_height_in` are now optional
  keyword fields rather than required positional-or-keyword ones (callers
  using keyword arguments, as documented, are unaffected).

## 0.1.0 — 2026-10-10

First release. Prices one moulding line end to end — see
`docs/roadmap/roadmap.md` Phases 1–6 and `docs/decisions/0001`–`0008` for the
domain reasoning behind each piece.

- `Moulding`, `Material`, `Finish`, `Extra`, `Offering`, `MouldingLineInput` —
  the core value objects, decoupled from the not-yet-specified `Design`.
- `PricingContext` — one place a shop plugs in its own rates, loaded from
  `data/shop_pricing_data.py`.
- `price_moulding_line`: bare material cost (real lumber-yard pricing,
  species × thickness × width) → two-rate Finish pricing → Extras
  (per-length/flat) → exact-match Offering pricing or the custom chain plus a
  non-offering labor charge → universal tooling-work labor → flat-per-frame
  joinery → material markup → an itemized breakdown. `price_total` applies
  quantity on top.
- `get_moulding(id)` — a hand-edited catalog, `data/moulding_catalog.py`,
  seeded with the shop's first 17 profiles.
