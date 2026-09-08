# Offering

> Status: **first-pass specification.** Documented as a current domain assumption.
> Not final, not an implementation instruction.

---

# Definition

An **Offering** is a deliberate shop-standard frame configuration — a curated
point in the shop's larger capability space that the shop intends to sell
repeatedly.

An Offering references:

- a **Moulding** (geometry)
- a **Material**
- a **Finish**
- zero or more **Extras**

Example — `"Black Maple Square"`:

```
moulding = 1-inch square geometry
material = maple
finish   = black
extras   = []
```

Example — `"Black Maple with Walnut Inlay"`:

```
moulding = 1-inch square geometry
material = maple
finish   = black
extras   = [walnut inlay]
```

**An Offering is not merely a UI preset.** It is commercially and operationally
meaningful.

---

# Responsibilities

- Define a repeatable, named configuration the shop wants to get efficient at
  making.
- Serve as an **optional** starting point for a `DesignMoulding`.
- Eventually anchor the commercial/operational behavior that standard products
  get (below).

---

# Possible Attributes

Tentative. Not a schema.

- name (`"Black Maple Square"`)
- references: Moulding, Material, Finish, Extras[]
- possibly a description, product photography, marketing copy — later
- possibly standard dimensions or size options — later / open question

Not now, but an Offering may eventually relate to:

- stock / on-hand inventory
- batch manufacturing
- standard pricing (distinct from one-off custom pricing)
- preferred production methods / known labor
- marketing, online sales, sales-channel availability
- lead times

**Do not implement any of those systems now.**

---

# Relationships

- **Moulding / Material / Finish / Extra** — an Offering bundles one of each
  (Extras: zero or more).
- **DesignMoulding** — an Offering may be the `source_offering` a DesignMoulding
  was instantiated from. **Optional** — many DesignMouldings have none.
- **Pricing** — whether a configuration came from an Offering may change how it
  is priced (standard vs custom, amortized setup, batch efficiencies).

---

# Derived Values

- Whether a given DesignMoulding still **exactly matches** its source Offering
  after edits — derived by comparison, not stored. (How to compute this is an
  open question.)

---

# Business Rules / Invariants

- **Offering represents a curated, repeatable shop product/configuration** — that
  is the load-bearing rule.
- An Offering is **optional** as a source for a DesignMoulding. The shop can
  fabricate arbitrary configurations with no Offering involved.
- An Offering may include Extras and still be a standard product.

---

# Historical / Snapshot Concerns

- When a Design sourced from an Offering is accepted, the accepted snapshot must
  preserve enough about the Offering (identity? full configuration?) to reproduce
  what was sold. Whether the **Offering identity itself** is part of the snapshot
  is an open question.
- Offering definitions, standard pricing, and stock all change over time;
  accepted orders must not move.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- Can an Offering contain multiple Extras? (Working assumption: yes.)
- Does an Offering carry standard dimensions / size options, or only the
  configuration?
- How is stocked Offering inventory represented later?
- Should the source Offering identity be preserved in an accepted snapshot?
- How do we determine whether a DesignMoulding still matches its source Offering?

---

# Pseudocode Sketch

_None yet._
