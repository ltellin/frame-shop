# Changelog

All notable changes to `frameshop-pricing` are recorded here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions
follow [semver](https://semver.org/).

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
