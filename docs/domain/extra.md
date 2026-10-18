# Extra

> Status: **first-pass specification.** Documented as a current domain assumption.
> Not final, not an implementation instruction.

---

# Definition

An **Extra** is an optional detail / modification / embellishment applied to a
configured moulding.

Starting extras: **inlay** (priced by length) and **matching spacers** (priced
by length). More to be added later.

---

# Responsibilities

- Describe one optional embellishment / addition.
- Declare **how it's priced** — see Pricing components below.

---

# Possible Attributes

Tentative. Not a schema.

- **name / kind** (`"inlay"`, `"matching spacer"`, …)
- **flat charge** — a fixed $ amount, 0 if unused (see below)
- **per-length charge** — a $/foot rate, 0 if unused (see below)
- a description or spec of the detail

---

# Pricing components

**Settled (ADR 0011, revising ADR 0004's either/or `method`):** every Extra
carries **two independent chargeable components**, not a choice between two
kinds of Extra. Either may be zero — most Extras today only use one — but
both can be set on the same Extra at once (e.g. a per-foot inlay rate plus a
flat hardware/setup fee on one named Extra):

- **per-length charge** — a rate per linear foot, applied to the same
  **billable footage** used for the bare moulding material and Finish
  (working assumption — see Open Questions). Both current extras (inlay,
  matching spacers) use this. **Applies at every Length/Chop/Join order
  form** — a continuous inlay runs along the stick whether it's cut or not.
- **flat charge** — a single fixed charge regardless of size. **Applies at
  `JOIN` only** — a flat charge typically describes something about the
  finished, assembled piece (e.g. a hardware kit), which doesn't exist yet
  at Length or Chop. See [`pricing.md`](pricing.md) and
  [`../decisions/0009-length-chop-join-order-form.md`](../decisions/0009-length-chop-join-order-form.md).

This keeps adding a new extra, or adding a second charge to an existing one,
a **data change** (set a flat amount, a per-foot rate, or both) rather than
a code change.

---

# Relationships

- **DesignMoulding** — a DesignMoulding may contain **zero, one, or multiple**
  Extras.
- **Offering** — an Offering itself may include Extras (e.g. a signature product
  with a standard inlay).
- **Moulding** — **some mouldings will constrain which Extras are compatible**
  with them (e.g. a profile too narrow for a given inlay). **Not implemented
  now — explicitly noted as a real future requirement**, not silently dropped.
  See Open Questions.
- **Pricing** — looks up each Extra's rate by name; see [`pricing.md`](pricing.md).

---

# Derived Values

- **extra cost contribution** — sum over the DesignMoulding's Extras of
  (`per_length_charge × billable footage`) plus, at `JOIN` only, sum of
  `flat_charge`. Both components can contribute from the same Extra.
  Derived, not stored here.

---

# Business Rules / Invariants

- **An Extra does NOT automatically imply a custom / non-standard frame.** An
  Offering can include Extras and still be a standard product.
- **Extra rates are hardcoded reference data**, stored alongside Material/
  Finish/Lumber pricing constants in one easy-to-edit place — see
  [`../architecture/overview.md`](../architecture/overview.md). Not built yet.

---

# Historical / Snapshot Concerns

Extra rates may change over time; accepted orders must not move. Snapshot
requirement shared with Material and Finish — mechanism deferred.

---

# Open Questions

**Settled**: pricing is two independent components (flat + per-length), not
a method choice — see
[`../decisions/0011-extra-rate-combines-flat-and-per-length.md`](../decisions/0011-extra-rate-combines-flat-and-per-length.md).
Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md), still open:

- **Moulding/Extra compatibility constraints** — real, but deliberately
  unimplemented for now. Needs a mechanism later (which Extras are valid for a
  given Moulding).
- Does the per-length charge use the same billable footage as the bare
  material and Finish? (Working assumption: yes — not confirmed.)

**Settled**: any Extra difference from a source Offering's recipe breaks the
exact match uniformly — there's no notion of some Extras preserving
standard-pricing eligibility while others don't. See
[`../decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](../decisions/0005-offering-pricing-and-non-offering-labor-charge.md).

---

# Pseudocode Sketch

See [`pricing.md`](pricing.md) for `per_length_extras_cost` and
`flat_extras_cost` (split by Length/Chop/Join tier — ADR 0009).
