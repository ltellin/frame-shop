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
- Declare **how it's priced** — see Pricing method below.

---

# Possible Attributes

Tentative. Not a schema.

- **name / kind** (`"inlay"`, `"matching spacer"`, …)
- **pricing method** — `per_length` | `flat` (see below)
- **rate** — a $/foot value if `per_length`, or a flat $ amount if `flat`
- a description or spec of the detail

---

# Pricing method

Every Extra is priced one of two ways — a property of the Extra itself, not a
one-off rule per extra:

- **`per_length`** — a rate per linear foot, applied to the same **billable
  footage** used for the bare moulding material and Finish (working assumption
  — see Open Questions). Both current extras (inlay, matching spacers) are this
  kind.
- **`flat`** — a single fixed charge regardless of size.

This keeps adding a new extra to a **data change** (add a row with a name,
method, and rate) rather than a code change.

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
  (`rate × billable footage` if `per_length`, else the flat `rate`). Derived,
  not stored here.

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

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- **Moulding/Extra compatibility constraints** — real, but deliberately
  unimplemented for now. Needs a mechanism later (which Extras are valid for a
  given Moulding).
- Does a `per_length` extra use the same billable footage as the bare material
  and Finish? (Working assumption: yes — not confirmed.)

**Settled**: any Extra difference from a source Offering's recipe breaks the
exact match uniformly — there's no notion of some Extras preserving
standard-pricing eligibility while others don't. See
[`../decisions/0005-offering-pricing-and-non-offering-labor-charge.md`](../decisions/0005-offering-pricing-and-non-offering-labor-charge.md).

---

# Pseudocode Sketch

See [`pricing.md`](pricing.md) for `extras_cost`.
