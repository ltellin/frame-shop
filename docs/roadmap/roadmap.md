# Roadmap

This is a **domain-development sequence**, not a product/feature roadmap. It is
the order in which we intend to *think through and specify* concepts.

**This ordering is provisional** and will be revised as the domain becomes
clearer.

**Claude does not advance from one phase to the next on its own.** The human
decides when a conceptual area is done and when to move on. Finishing the
documentation for a phase does not authorize starting the next one.

**2026-09-17 — deliberate sequence deviation.** Phases 1–6 (everything needed to
price a moulding) are specified enough that the owner asked to pause the
SPECIFY sequence and **implement** that slice now — as a standalone package,
decoupled from the not-yet-specified `Design`/`DesignMoulding` (see
[`../decisions/`](../decisions/) 0002–0007) — so it's importable by an external
website today. Phase 7 (Artwork) was started and paused for this. The rest of
the SPECIFY sequence (7 onward) resumes after the implementation work.

Each phase is SPECIFY → (later) IMPLEMENT → (later still) INTEGRATE, and those
stages are not collapsed.

| Phase | Focus |
|---|---|
| **0** | Domain skeleton — this documentation structure. |
| **1** | **Moulding** specification — geometry, types (STANDARD / FLOAT), tooling work. |
| **2** | **Material** (species table) + **Lumber** (stock / pricing) + the **bare-moulding material price-per-foot** model — geometry + material + milling waste + minimum footage. |
| **3** | **Finish** and **Extra** specification. |
| **4** | **Offering** specification — standard configurations, repeatability, its own pricing. |
| **5** | **DesignMoulding** specification — Offering path, customized-Offering path, fully-custom path. |
| **6** | **The rest of moulding pricing** (pseudocode only) — tooling-work labour, joinery, markup, quantity, on top of Phases 2–4's bare material / finish / extras / Offering-vs-custom chain. |
| **7** | **Artwork / framed-object** specification (includes non-artwork products like mirrors). |
| **8** | **Design** specification. |
| **9** | Relationship between a Design and its multiple framing components. |
| **10** | **Pricing engine** specification (general). |
| **11** | Implement: save / reopen a Design. |
| **12** | Accept a Design / historical snapshot. |
| **13** | **Order** and **Work Order**. |
| **14** | Production. |
| **15** | Broader catalog / vendor / lumber / inventory / operations work. |

## Status

- Phase 0: complete — skeleton created.
- Phase 1 (Moulding): geometry fields (STANDARD rabbet depth/height, FLOAT
  internal height + board thickness, shared face width + overall height) and the
  **tooling work** 1–8 Fibonacci scale are **settled** (first pass) — see
  `docs/decisions/0001-moulding-geometry-and-tooling-work.md`. Also added: waste
  factor (multiplier, with rough starting guidance), optional minimum-footage
  override. Still open: how the STANDARD/FLOAT split is represented in storage.
  **Implemented** (the pricing-relevant parts) — see `backend/frameshop_pricing/`.
- Phase 2 (Material / Lumber / bare material cost): **settled** (first pass) —
  8-species Material list, a lumber-price table keyed by species × thickness ×
  width (price per board foot), and the derived bare-moulding price-per-foot
  chain with a 4 ft shop-default minimum footage — see
  `docs/decisions/0002-material-and-bare-moulding-material-cost.md`. The
  milling-geometry follow-ups are also **settled** — the fixed
  `from_board_edge` / `from_board_face` milling convention (a **DesignMoulding**
  field, not Moulding), no glue-ups, no grade — see
  `docs/decisions/0003-milling-orientation-and-lumber-table-keying.md`. The
  earlier "round up to nearest stocked step" mechanism was superseded by an
  explicit, per-Moulding `source_lumber_size` (per milling orientation) — see
  `docs/decisions/0007-source-lumber-size.md`, which also resolves the
  "stocked board widths" question. Only exact per-Moulding waste-factor values
  remain loose. **Implemented**, including real lumber-yard price data — see
  `backend/frameshop_pricing/data/shop_pricing_data.py`.
- Phase 3 (Finish / Extra): **settled** (first pass) — Finish as a small
  controlled list of strings, no face-width scaling; Extra priced by its own
  method (`per_length` | `flat`); both stored as hardcoded reference data
  alongside lumber prices — see `docs/decisions/0004-finish-and-extra-pricing.md`.
  Finish's pricing shape was later revised from flat-per-foot to a two-rate
  model (base rate to the minimum footage, lower marginal rate beyond) — see
  `docs/decisions/0008-finish-two-rate-pricing.md`. Open: whether Finish/Extra
  use billable or required footage (a working assumption is recorded); whether
  Extra's `per_length` pricing should get the same two-rate treatment; Extra ↔
  Moulding compatibility constraints (explicitly deferred). **Implemented** —
  see `backend/frameshop_pricing/`.
- Phase 4 (Offering): **settled** (first pass) — Offering is a size-agnostic
  component recipe (no dimensions) carrying its own `menu_price_per_foot`,
  used only when a DesignMoulding matches it exactly (no partial credit); any
  divergence or fully-custom DesignMoulding instead uses the computed chain
  plus a shop-configurable `non_offering_labor_charge` per foot — see
  `docs/decisions/0005-offering-pricing-and-non-offering-labor-charge.md`.
  Open: whether stocked inventory is ever modelled; whether Offering identity
  is part of the acceptance snapshot. **Implemented** (the pricing-relevant
  parts — `Offering`, `matches_source_offering`) — see `backend/frameshop_pricing/`.
  Not implemented: Offering as a persisted, catalog-backed entity.
- Phase 5 (DesignMoulding): **settled** (first pass) — `quantity` lives on
  Design (not DesignMoulding); joinery method (`"underpinning"` |
  `"splining"`, flat charge per frame, follows the Offering/custom split); the
  price result is a structured breakdown, not a single number — see
  `docs/decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`.
  Open: acceptance snapshot contents; placeholders during early design; where
  multiple DesignMouldings' spatial relationship is expressed. **Implemented**
  the decoupled pricing-relevant shape, as `MouldingLineInput` (not a real
  `DesignMoulding` — Design isn't specified) — see `backend/frameshop_pricing/models.py`.
- Phase 6 (rest of moulding pricing): **settled** (first pass) — introduced
  `PricingContext` (one object bundling every shop-configurable rate/default,
  instantiated from a centralized editable location per shop); tooling-work
  labor (per foot, applies to *every* moulding line, Offering-priced or not);
  material markup (a percentage on bare lumber cost only, custom path only);
  and confirmed Offering keeps its flat `menu_price_per_foot` rather than a
  computed-with-discount approach (reconsidered and reaffirmed) — see
  `docs/decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`.
  A full `price_moulding_line()` now exists in `docs/domain/pricing.md`,
  covering everything from bare material through markup. Open: exact
  tooling-work-labor formula shape; whether markup extends beyond lumber.
  **Implemented** — see `backend/frameshop_pricing/engine.py` (see the sequence-deviation
  note above).
- Phase 7 (Artwork): started, paused mid-SPECIFY for the Phase 1–6
  implementation push. Not finalized.
- Phases 8+: not started.
