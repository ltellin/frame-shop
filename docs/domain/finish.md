# Finish

> Status: **modest first-pass notes.** Only what is known so far. Do not
> speculate beyond this.

---

# Definition

**Finish** describes how the chosen Material is surface-treated. It is distinct
from Moulding geometry and from Material.

Examples that may eventually apply: natural, oil, stain, paint, lacquer,
ebonized, other shop finishes.

Finish is a choice at the **DesignMoulding / Offering** layer.

---

# Responsibilities

- Name / describe the surface treatment for a configured moulding.
- Eventually, contribute its own **material and labor** information to pricing.

---

# Possible Attributes

Tentative. Not a schema. Deliberately thin — Finish is not being specified in
depth yet.

- name (natural, oil, stain, paint, lacquer, ebonized, …)
- possibly a colour / spec for stains and paints — later
- notes

---

# Relationships

- **DesignMoulding** — references a Finish.
- **Offering** — references a Finish as part of a standard configuration.
- **Pricing** — may consume Finish material + labor inputs.

---

# Derived Values

- finish cost contribution — derived by the pricing engine, not stored here.

---

# Business Rules / Invariants

_TBD._ Candidate: a configured DesignMoulding has exactly one Finish.

---

# Historical / Snapshot Concerns

Finish material and labor costs may change over time; accepted orders must not
move. Same snapshot requirement as Material — mechanism deferred.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- What exact information does Finish expose to pricing (materials, labor,
  complexity)?
- Does Finish need structured colour / product data, or is a name enough for
  now?

---

# Pseudocode Sketch

_None yet._
