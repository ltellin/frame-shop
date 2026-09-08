# 0001 — Moulding geometry fields and the "tooling work" scale

Status: accepted (first pass — Phase 1). Date: 2026-09-08.

## Context

Phase 1 specifies [`Moulding`](../domain/moulding.md) as a geometry / fabrication
concept. The first-pass spec left the actual geometry fields and the
tooling-complexity representation as open questions. The shop owner has now
described the real geometry the shop works with (it mills its own profiles), so
these can be pinned down enough to build Material, Offering, DesignMoulding, and
the pricing pseudocode on top of them.

This does not settle *how* the fields are stored (see Consequences).

## Decision

**A Moulding has a `type`: `STANDARD` or `FLOAT` (extensible).**

**Fields common to both types**

- **face width** — visible width of the profile, front view
- **overall height** — profile height / depth, front face to back
- **tooling work** — see below

**STANDARD only**

- **rabbet depth** — how far the front lip laps inward over the glazing / art
  edge. **Default 1/4".** Drives sight size (`sight ≈ glazing − 2·rabbet_depth`).
- **rabbet height** — how far back the recess goes, front to back. Drives whether
  the framing package fits.

**FLOAT only** (no rabbet)

- **internal height** — distance from the float board to the face of the moulding
- **float board thickness** — **default 3/8".**

**Not on Moulding**

- **float gap** (artwork edge → inside of the moulding on a float frame,
  **default 1/4"**) lives on [`DesignMoulding`](../domain/design-moulding.md). It
  is not a moulding-level fact, but a float frame's dimensions cannot be
  specified without it.
- **joinery method** lives on `DesignMoulding`.
- material, finish, extras, stock, price — as already stated in `moulding.md`.

**Tooling work** replaces the earlier working names `tooling_level` /
`fabrication_complexity`. It is a coarse estimate of milling effort on the
**Fibonacci scale 1, 2, 3, 5, 8** (story-point style — a size, not time or
money). Anchor points: `1` = simple square/rectangular profile, table-saw passes
only; `3` = table-saw + one shaping pass on the shaper/moulder; `5` = table-saw +
multiple shaping passes / multiple setups. `2` and `8` are the in-between and
beyond-that steps. The pricing engine may weigh the same value differently for a
one-off custom frame vs an amortized standard Offering.

## Alternatives considered

- **A generic profile-geometry description** (arbitrary cross-section, curves,
  ogees). Rejected for now — the shop's profiles are describable with a few
  scalars, and a richer shape model can be added later as an optional field
  without a rewrite. (See the generic-abstraction warning in `AGENTS.md`.)
- **A free-form or larger tooling scale** (e.g. 1–10, or estimated minutes).
  Rejected — the owner wants a coarse, fast, story-point-like judgement; a
  Fibonacci scale discourages false precision.
- **Putting the float gap and joinery method on Moulding.** Rejected — both are
  decisions made while designing a specific frame, not properties of the profile
  itself.

## Consequences

- Material, Offering, DesignMoulding, and the Phase 6 pricing pseudocode can
  treat these fields as stable facts.
- `sight_size`, `stack_fits`, and `float_finished_size` derivations are now
  well-defined (pseudocode in `moulding.md`).
- **Still open:** whether the STANDARD/FLOAT field split is stored as nullable
  columns, subtypes, a nested geometry object, or inheritance
  ([`OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md) — Moulding geometry #1). This ADR
  is about the domain fields, not the storage shape.
- Measurement storage type (decimal inches assumed) is not settled here.
- If bought-in manufacturer moulding is added later, it must be reconciled with
  this shop-milled, geometry-first model (open question).
