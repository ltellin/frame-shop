# Extra

> Status: **modest first-pass notes.** Only what is known so far. Do not
> speculate beyond this.

---

# Definition

An **Extra** is an optional detail / modification / embellishment applied to a
configured moulding.

Examples: carving, inlay, other embellishments or fabrication additions.

---

# Responsibilities

- Describe one optional embellishment / addition.
- Eventually, contribute its own **materials, labor, and fabrication / tooling**
  effects to pricing.

---

# Possible Attributes

Tentative. Not a schema. Deliberately thin.

- name / kind (carving, inlay, …)
- a description or spec of the detail
- notes

---

# Relationships

- **DesignMoulding** — a DesignMoulding may contain **zero, one, or multiple**
  Extras.
- **Offering** — an Offering itself may include Extras (e.g. a signature product
  with a standard inlay).
- **Pricing** — Extras contribute material / labor / tooling inputs.

---

# Derived Values

- extra cost contribution — derived by the pricing engine.

---

# Business Rules / Invariants

- **An Extra does NOT automatically imply a custom / non-standard frame.** An
  Offering can include Extras and still be a standard product.

---

# Historical / Snapshot Concerns

Extra materials / labor may change over time; accepted orders must not move.
Snapshot requirement shared with Material and Finish — mechanism deferred.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- How should Extras describe their material / labor / tooling effects?
- Can an Offering contain multiple Extras? (Working assumption: yes.)
- Do some Extras preserve standard-pricing eligibility while others force custom
  pricing?

---

# Pseudocode Sketch

_None yet._
