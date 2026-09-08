# Open Questions

Unresolved questions, kept deliberately unresolved. Do **not** answer one just
because it is written down or because the docs make an answer look obvious. An
answer lands here only when the human has actually decided — and then it also
moves into the relevant domain file and, if architectural, into
[`decisions/`](decisions/).

---

## Moulding (geometry)

Geometry fields and the tooling-work scale are **settled** (first pass) — see
[`decisions/0001-moulding-geometry-and-tooling-work.md`](decisions/0001-moulding-geometry-and-tooling-work.md).
Still open:

1. Should the STANDARD/FLOAT geometry difference be nullable fields, subtype
   models, separate geometry objects, or inheritance? (Domain distinction is
   documented; the representation is not chosen.)
2. How does tooling / setup work affect **custom** pricing vs **standard
   Offering** pricing, where setup may already be amortized?
3. How is bought-in **manufacturer moulding** (Roma, Omega, …) represented
   relative to this geometry-first, shop-milled model — a Moulding with an
   external source, a Product, or something else?
4. Can a float **Offering** pin its own gap (a fixed reveal for a standard float
   product), or is the float gap only ever defaulted per DesignMoulding?
5. **Waste factor** — multiplier vs percentage; default value; per-Moulding only,
   or could it be derived from tooling work / profile complexity instead of
   stored?
6. **Milling orientation** — its value set and naming; the kerf / oversize
   allowance added on top of the raw geometry dimension when picking stock
   thickness and blank size.

## Material / lumber

Material is a small controlled list (8 wood species); lumber prices are a stored,
time-varying table; the bare moulding material cost is derived per foot — see
[`decisions/0002-material-and-bare-moulding-material-cost.md`](decisions/0002-material-and-bare-moulding-material-cost.md).
Still open:

7. **Unit of lumber pricing** — board foot assumed; confirm. Ever per linear
   foot or per piece?
8. How is the **lumber table keyed** — species × nominal thickness only, or also
   width / length / grade?
9. What **thickness steps** does the shop actually stock (4/4, 5/4, 6/4, 8/4, …)?
10. Can thinner stock be **glued up** to reach a needed thickness, and how does
    that change the cost?
11. Does **lumber grade / quality** (FAS, Select, …) need modelling, or is one
    price per (species, thickness) enough?
12. Can **Material** be a placeholder on a DesignMoulding during early design?
    Do laminated / multi-material profiles ever need modelling?

## Finish

13. What exact information does **Finish** expose to pricing (materials, labor,
    complexity)? Is it priced per foot / per frame / flat?
14. Does Finish need structured colour / product data, or is a name enough for
    now?

## Extra

15. How should **Extras** describe their material / labor / tooling effects?
16. Can an **Offering** contain multiple Extras? (Working assumption: yes.)
17. Do some Extras preserve standard-pricing eligibility while others force
    custom pricing?

## Offering

18. Does an Offering carry **standard dimensions / size options**, or only the
    Moulding + Material + Finish + Extras configuration?
19. How should **stocked Offering inventory** be represented later?
20. Should the **source Offering identity** be preserved in an accepted snapshot?
21. How do we determine whether a DesignMoulding **still exactly matches** its
    source Offering after edits?

## DesignMoulding

22. Does modifying a DesignMoulding that came from an Offering **automatically
    remove standard pricing eligibility**? Can some customizations keep standard
    pricing while others trigger custom pricing?
23. What exactly gets **snapshotted** when a Design (and its DesignMouldings) is
    accepted?
24. Where does **`quantity`** live — on DesignMoulding or on Design?
25. What is the structure of the **"current price result"** a DesignMoulding
    holds?
26. Can **Moulding / Material / Finish** be placeholders during early design, and
    what is derivable/priceable from a partial configuration?
27. What is the **joinery method** vocabulary, and does the choice feed pricing
    and/or production (labor, equipment)?
28. Where does the **shop-default minimum footage** live (a shop-settings /
    pricing-context concept, not literally each Design row)?
29. Does the **minimum footage** also scale finish / other per-foot charges, or
    only the bare moulding material?

## Design & framing components

30. How should **multiple DesignMouldings in one Design** express their spatial /
    structural relationship (build-up: outer frame + inner liner) — without a
    generic node/edge graph?
31. How should a Design preserve enough structure to derive **both** the
    outward-to-inward representation **and** the exploded schematic?
32. What is the **base reference** a Design's structure is built around (piece
    size / sight size / glass size / frame rabbet), and is it fixed or
    switchable?
33. Which relationships on a **draft Design** are optional? (Customer, Artwork,
    Order — presumably all optional while drafting.)
34. Can a saved Design remain **permanently unattached** to a Customer?
35. How should **draft / held / quoted / accepted / discarded / archived**
    Designs differ conceptually? Which are editable? Which are terminal?
36. Does a Design need **variants / alternatives** (two options for a customer)?
    Out of scope now — flag only.

## Artwork / framed objects

37. Can a Design describe products such as **mirrors** that contain no customer
    Artwork, and if so, what concept represents the thing contained / presented
    by the frame?
38. Does **Artwork** need to exist before acceptance, or only before production?

## Business boundaries

39. What information becomes **required when a Design is quoted**?
40. What information becomes **required when a Design is accepted**?
41. Does **Customer** become required at acceptance, at Order creation, or
    earlier for some paths (trade orders)?
42. Is there a real distinction between "quoted" and "accepted" the model needs,
    or is a quote just a printed draft?

## Order / Work Order

43. Is there a layer between Order and Design (a "job")? Or does an Order group
    accepted Designs directly?
44. One Work Order per physical piece — how does that map when `quantity > 1`?
45. How are Order and Work Order **numbered**?
46. Do **trade / batch orders** (many frames or chops for another shop, with a PO
    and due date) fit the same Order model as retail?

## Pricing

47. What is the shape of a **pricing context** (shop-defined rules, rates, and
    current lumber prices in effect)?
48. Which price inputs are **live data** vs **shop-defined pricing config**, and
    how are both snapshotted for accepted work?
49. Beyond the bare material cost (Phase 2), how does the **rest of moulding
    pricing** work — tooling-work labour, finish, extras, joinery, markup,
    quantity, Offering context? (Phase 6.)
50. Is price ever **stored** on a Design (a cached display value), or always
    recomputed?

## Strainer

51. Should Strainer eventually be a separate Design component (a
    `DesignStrainer`, parallel to `DesignMoulding`)?
52. What conditions should recommend or require a strainer (size, profile
    strength, glazing weight, assembly weight)?
53. Does a strainer need its own geometry / material / fabrication model, and how
    much would it genuinely share with Moulding? (Do **not** pre-emptively
    extract a shared `ProfileGeometry`.)

## State (payment / production / fulfillment)

54. Are payment, production, and fulfillment genuinely **independent facets**,
    tracked separately rather than as one status? (Working assumption: yes.)
55. Which state is **explicitly recorded** by a worker vs **derived** from
    prerequisites?

## Production

56. What are the real **production operations** a frame shop performs, and can
    they be a small fixed set per job type rather than a configurable workflow?
57. How are **daily production / pick / cut lists** derived from canonical data
    (never a stored list as source of truth)?
58. Can frame prep and artwork prep proceed **in parallel** rather than as a
    strict sequence?

## Catalog / vendor / lumber

59. Which catalog attributes are common to all products vs category-specific?
60. How is **catalog / lumber reference data** kept separate from **transaction
    history** so price / availability changes never alter past orders?
61. How is catalog and lumber-price data loaded and updated (hand-edited file,
    spreadsheet import, vendor feed)?

## Cross-cutting / architecture

62. Relational database — which one, and when is it introduced?
63. Money representation (integer minor units assumed) and measurement
    representation (decimal inches with fraction input assumed) — confirm.
64. Multi-station simultaneous use — what concurrency guarantees, and when?
65. Auth / roles / who-can-do-what — deferred; flag where it touches the model.
66. Images / an eventual camera over the design table — skeleton only, deferred.
