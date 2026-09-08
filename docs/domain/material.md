# Material

> Status: **first-pass specification.** Documented as a current domain assumption.
> Not final, not an implementation instruction.

---

# Definition

**Material** is what a moulding is physically made from. It is a **small
controlled list**, and for now it holds **wood species only**.

Initial species: **maple, poplar, white oak, red oak, walnut, sapele, ash,
cherry**.

Material is a **choice made at the DesignMoulding / Offering layer** — it belongs
to `DesignMoulding`, **not** to `Moulding`. The same Moulding geometry can be
milled in any species on the list.

---

# Responsibilities

- Name the species chosen for a configured moulding, from the controlled list.
- Identify *which species* the pricing engine looks up in the lumber-price
  records — see [`lumber.md`](lumber.md).

---

# Possible Attributes

Tentative. Not a schema.

- **species name** (the controlled-list value)
- possibly a category later (domestic hardwood / exotic / softwood / non-wood) —
  not needed yet

Material does **not** hold: geometry, finish, embellishment, a price, inventory
levels, or board thicknesses (that is lumber stock — see `lumber.md`).

---

# Relationships

- **DesignMoulding** — references a Material. Required for a complete
  configuration (a placeholder may be allowed during early design — open
  question).
- **Offering** — references a Material as part of a standard configuration.
- **Lumber** ([`lumber.md`](lumber.md)) — Material names the species; the lumber
  records hold the stock thicknesses the shop buys in that species and their
  current price.
- **Moulding** — a Moulding's geometry, together with a Material, determines the
  **bare price per foot** of an unfinished, unjoined stick (see
  [`pricing.md`](pricing.md)).
- **Pricing** — consumes the current lumber price for the chosen species while a
  Design is being priced.

---

# Derived Values

- **bare moulding price per foot** — a function of the Material (species) + the
  Moulding geometry (blank size, required stock thickness) + current lumber
  prices + the Moulding's waste factor. Derived, not stored on Material. See
  `pricing.md`.
- board footage / yield needed for a given frame — depends on Moulding geometry
  and finished size, not on Material alone.

---

# Business Rules / Invariants

Candidates:

- A configured DesignMoulding has exactly one Material (multi-material laminated
  profiles are out of scope for now — flag if they come up).
- Material carries no price of its own; price comes from separate, time-varying
  lumber records.
- Species is chosen from the controlled list, not free text.

---

# Historical / Snapshot Concerns

Lumber prices change and are updated periodically. An **accepted** order must
preserve enough pricing data that it does not change when lumber prices are later
updated. Preserve this requirement; do not decide the snapshot mechanism.

Key conceptual split to keep:

| Concept | Role |
|---|---|
| **Material** | the species choice (stable identity, controlled list) |
| **Lumber** ([`lumber.md`](lumber.md)) | stock the shop buys (species × thickness) + its changing price |
| **DesignMoulding** | references a Material |
| **Pricing engine** | consumes the current lumber price while pricing a live Design |
| **Accepted-order snapshot** | must preserve enough that old orders don't move |

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- Which Moulding geometry dimension maps to the **required board thickness**, and
  what standard stock thicknesses does the shop stock?
- Can Material be a placeholder on a DesignMoulding during early design?
- Do laminated / multi-material profiles ever need modelling? (Out of scope now.)
- When does a species category (hardwood / exotic / …) start to matter?

---

# Pseudocode Sketch

_See [`pricing.md`](pricing.md) for the bare-moulding price-per-foot chain that
consumes Material._
