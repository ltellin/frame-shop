# Open Questions

Unresolved questions, kept deliberately unresolved. Do **not** answer one just
because it is written down or because the docs make an answer look obvious. An
answer lands here only when the human has actually decided — and then it also
moves into the relevant domain file and, if architectural, into
[`decisions/`](decisions/).

---

## Moulding (geometry)

Geometry fields, the tooling-work scale, the milling convention, the
lumber-table shape, and each Moulding's explicit `source_lumber_size` (per
milling orientation, replacing computed rounding) are **settled** (first pass)
— see
[`decisions/0001-moulding-geometry-and-tooling-work.md`](decisions/0001-moulding-geometry-and-tooling-work.md),
[`decisions/0003-milling-orientation-and-lumber-table-keying.md`](decisions/0003-milling-orientation-and-lumber-table-keying.md),
and
[`decisions/0007-source-lumber-size.md`](decisions/0007-source-lumber-size.md).
Still open:

1. Should the STANDARD/FLOAT geometry difference be nullable fields, subtype
   models, separate geometry objects, or inheritance? (Domain distinction is
   documented; the representation is not chosen.)
2. **Tooling-work labor's exact formula shape** — a first-pass assumption (rate
   × tooling-work number × billable feet, applied universally on both
   Offering-priced and custom-priced lines) is recorded in
   [`decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`](decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md),
   but not confirmed — could instead be a distinct $/ft rate per tooling-work
   level rather than one rate scaled by the number.
3. How is bought-in **manufacturer moulding** (Roma, Omega, …) represented
   relative to this geometry-first, shop-milled model — a Moulding with an
   external source, a Product, or something else?
4. Can a float **Offering** pin its own gap (a fixed reveal for a standard float
   product), or is the float gap only ever defaulted per DesignMoulding?

## Material / lumber

Material is a small controlled list (8 wood species); lumber is a stored,
time-varying table keyed by species × thickness × width, priced per board foot;
the bare moulding material cost is derived per foot; no glue-ups; no grade
modelling — see
[`decisions/0002-material-and-bare-moulding-material-cost.md`](decisions/0002-material-and-bare-moulding-material-cost.md)
and
[`decisions/0003-milling-orientation-and-lumber-table-keying.md`](decisions/0003-milling-orientation-and-lumber-table-keying.md).
Still open:

5. Can **Material** be a placeholder on a DesignMoulding during early design?
   Do laminated / multi-material profiles ever need modelling?

## Finish

**Settled** (first pass) — a small controlled list of strings (`"oil"`,
`"painted"`, `"stained"`, …), priced with a **two-rate model** (a base rate
covering the shop's minimum footage, a lower marginal rate beyond it — not a
flat per-foot rate as first specified), never scaling with face width, stored
as hardcoded reference data — see
[`decisions/0004-finish-and-extra-pricing.md`](decisions/0004-finish-and-extra-pricing.md)
and
[`decisions/0008-finish-two-rate-pricing.md`](decisions/0008-finish-two-rate-pricing.md).
No Finish-specific open questions remain.

## Extra

Pricing method (`per_length` | `flat`) and the hardcoded-rate storage are
**settled** — see
[`decisions/0004-finish-and-extra-pricing.md`](decisions/0004-finish-and-extra-pricing.md).
Whether an Extra breaks Offering-price eligibility is also **settled**: any
Extra difference from the source Offering's recipe does, uniformly — see
[`decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](decisions/0005-offering-pricing-and-non-offering-labor-charge.md).
Still open:

6. Can an **Offering** contain multiple Extras? (Working assumption: yes.)
7. **Moulding/Extra compatibility** — some mouldings will constrain which
   Extras fit them (e.g. profile too narrow for a given inlay). Real, but
   explicitly deferred — needs a mechanism later.
8. Should **Extras' `per_length` pricing** get the same two-rate treatment
   (base rate to the minimum footage, lower marginal rate beyond) that Finish
   got in
   [`decisions/0008-finish-two-rate-pricing.md`](decisions/0008-finish-two-rate-pricing.md)
   — the same setup-labor reasoning plausibly applies (e.g. inlay)?

## Offering

Offering is **settled** (first pass) as a size-agnostic component recipe
(Moulding + Material + Finish + Extras, no dimensions) with its own
`menu_price_per_foot`, used only on an exact match against a DesignMoulding —
see
[`decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](decisions/0005-offering-pricing-and-non-offering-labor-charge.md).
The flat-rate approach (vs. computing Offering price through the same formula
with a labor discount) was explicitly reconsidered and reaffirmed in
[`decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`](decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md).
Still open:

9. How should **stocked Offering inventory** be represented later, if it ever
   is? (Not needed for now.)
10. Should the **source Offering identity**, and the `menu_price_per_foot` in
    effect at the time, be preserved in an accepted snapshot?

## DesignMoulding

The exact-match rule and its pricing consequence, `quantity` living on Design,
joinery method (vocabulary + flat-per-frame pricing + the Offering/custom
split), and the structured price-breakdown shape are all **settled** — see
[`decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](decisions/0005-offering-pricing-and-non-offering-labor-charge.md)
and
[`decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`](decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md).
Still open:

11. What exactly gets **snapshotted** when a Design (and its DesignMouldings) is
    accepted?
12. Can **Moulding / Material / Finish** be placeholders during early design, and
    what is derivable/priceable from a partial configuration?
13. `PricingContext.default_minimum_footage` exists (settled), but is there a
    broader **shop-settings concept** it belongs to, or does `PricingContext`
    just *is* that concept for pricing purposes?
14. Does the **minimum footage** also scale finish / extra per-foot charges, or
    only the bare moulding material? (Working assumption in the pricing
    pseudocode: yes, Finish and per-length Extras use the same billable
    footage — not confirmed.)

## Design & framing components

15. How should **multiple DesignMouldings in one Design** express their spatial /
    structural relationship (build-up: outer frame + inner liner) — without a
    generic node/edge graph?
16. How should a Design preserve enough structure to derive **both** the
    outward-to-inward representation **and** the exploded schematic?
17. What is the **base reference** a Design's structure is built around (piece
    size / sight size / glass size / frame rabbet), and is it fixed or
    switchable?
18. Which relationships on a **draft Design** are optional? (Customer, Artwork,
    Order — presumably all optional while drafting.)
19. Can a saved Design remain **permanently unattached** to a Customer?
20. How should **draft / held / quoted / accepted / discarded / archived**
    Designs differ conceptually? Which are editable? Which are terminal?
21. Does a Design need **variants / alternatives** (two options for a customer)?
    Out of scope now — flag only.

## Artwork / framed objects

22. Can a Design describe products such as **mirrors** that contain no customer
    Artwork, and if so, what concept represents the thing contained / presented
    by the frame?
23. Does **Artwork** need to exist before acceptance, or only before production?

## Business boundaries

24. What information becomes **required when a Design is quoted**?
25. What information becomes **required when a Design is accepted**?
26. Does **Customer** become required at acceptance, at Order creation, or
    earlier for some paths (trade orders)?
27. Is there a real distinction between "quoted" and "accepted" the model needs,
    or is a quote just a printed draft?

## Order / Work Order

28. Is there a layer between Order and Design (a "job")? Or does an Order group
    accepted Designs directly?
29. One Work Order per physical piece — how does that map when `quantity > 1`?
30. How are Order and Work Order **numbered**?
31. Do **trade / batch orders** (many frames or chops for another shop, with a PO
    and due date) fit the same Order model as retail?

## Pricing

`PricingContext`'s shape and the full Phase 6 moulding-pricing chain (tooling
labor, joinery, material markup) are **settled** — see
[`decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md`](decisions/0006-pricing-context-tooling-labor-joinery-and-markup.md).
The Length/Chop/Join order-form split is also **settled** — see
[`decisions/0009-length-chop-join-order-form.md`](decisions/0009-length-chop-join-order-form.md).
Still open:

32. Which price inputs are **live data** vs **shop-defined pricing config**, and
    how are both snapshotted for accepted work?
33. Is price ever **stored** on a Design (a cached display value), or always
    recomputed?
34. Does **material markup** ever extend beyond the bare lumber cost — to
    Finish, Extras, or the other Design materials (mats, mounting, glazing)
    once those exist — or does it stay lumber-only?
35. **Offering is currently scoped to `JOIN` only (ADR 0009), but the owner
    expects to want it to cover Length/Chop too** (a real supplier catalog
    typically publishes a standard price for all three forms of the same
    recipe, not just the assembled one) — this isn't a maybe, it's known
    future work. Needs its own design pass: does `Offering` get three price
    points (`menu_price_per_foot` per order form), or something else?

## Strainer

36. Should Strainer eventually be a separate Design component (a
    `DesignStrainer`, parallel to `DesignMoulding`)?
37. What conditions should recommend or require a strainer (size, profile
    strength, glazing weight, assembly weight)?
38. Does a strainer need its own geometry / material / fabrication model, and how
    much would it genuinely share with Moulding? (Do **not** pre-emptively
    extract a shared `ProfileGeometry`.)

## State (payment / production / fulfillment)

39. Are payment, production, and fulfillment genuinely **independent facets**,
    tracked separately rather than as one status? (Working assumption: yes.)
40. Which state is **explicitly recorded** by a worker vs **derived** from
    prerequisites?

## Production

41. What are the real **production operations** a frame shop performs, and can
    they be a small fixed set per job type rather than a configurable workflow?
42. How are **daily production / pick / cut lists** derived from canonical data
    (never a stored list as source of truth)?
43. Can frame prep and artwork prep proceed **in parallel** rather than as a
    strict sequence?

## Catalog / vendor / lumber

44. Which catalog attributes are common to all products vs category-specific?
45. How is **catalog / lumber reference data** kept separate from **transaction
    history** so price / availability changes never alter past orders?
46. How is catalog and lumber-price data loaded and updated (hand-edited file,
    spreadsheet import, vendor feed)? For the lumber-sourcing piece
    specifically: **implemented** 2026-10-17 as three hand-editable CSVs (a
    named, species-agnostic stock-size reference table, a per-species price
    table, and a moulding-to-stock-size table) — see
    [`decisions/0010-moulding-lumber-sources-as-tables.md`](decisions/0010-moulding-lumber-sources-as-tables.md)
    and [`domain/lumber.md`](domain/lumber.md). Still open from that work:
    what happens when a Moulding points at a `stock_size_id` that's since
    been removed (currently just a `KeyError` at pricing time, not
    defensively handled). The broader question — spreadsheet import vs.
    vendor feed vs. always hand-edited — remains open for catalog data
    generally, beyond this one table.

## Cross-cutting / architecture

47. Relational database — which one, and when is it introduced?
48. Money representation (integer minor units assumed) and measurement
    representation (decimal inches with fraction input assumed) — confirm.
49. Multi-station simultaneous use — what concurrency guarantees, and when?
50. Auth / roles / who-can-do-what — deferred; flag where it touches the model.
51. Images / an eventual camera over the design table — skeleton only, deferred.
