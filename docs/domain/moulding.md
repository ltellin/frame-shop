# Moulding

> Status: **first-pass specification.** Enough has been discussed to write this
> down as a current domain assumption. It is still not final and not an
> implementation instruction. Open questions are meant to stay open.

---

# Definition

A **Moulding is a geometry / fabrication specification** — the shape and
dimensions of a frame profile, plus a coarse sense of how much shop tooling it
takes to mill. It answers "what profile is this, and how hard is it to make?"

A Moulding **does not represent**:

- wood species / material
- finish
- carving, inlay, or other embellishment
- joinery method
- stock quantity / inventory
- retail price
- customer, order, or work order
- a finished frame configuration

Those live at the **DesignMoulding / Offering** layer, not on the geometry.

---

# Responsibilities

- Describe a frame profile precisely enough to mill it and to compute the
  finished size of a frame built from it.
- Carry a coarse **tooling work** estimate.
- Expose geometry as *facts* a pricing engine can consume — not pricing methods.

---

# Types

Moulding **type** currently has at least two major categories. More may be added.

- **STANDARD** — traditional frame moulding with a lip / rabbet at the back inner
  edge that receives the framing package (glazing, mats, mount, artwork,
  backing).
- **FLOAT** — float-frame geometry for stretched canvas: a visible gap around the
  canvas, with the canvas / stretcher assembly supported from behind (on a float
  board) rather than by a front lip. A FLOAT moulding has **no rabbet**.

**Not all geometry fields are meaningful for all types.** A STANDARD moulding has
a rabbet (depth + height); a FLOAT moulding has an internal height and a float
board thickness instead, and no rabbet. Whether this becomes nullable fields,
subtype models, separate geometry objects, or inheritance is **deliberately not
decided** — see Open Questions. Document the domain distinction first.

---

# Possible Attributes

First-pass **settled** (not a schema, and the STANDARD/FLOAT split can still be
represented several ways — see Open Questions). Measurements shown with their
defaults; decimal inches assumed elsewhere but the storage type is not settled
here.

### All types

- **type** — STANDARD | FLOAT (extensible)
- **face width** — the visible width of the profile viewed from the front
- **overall height** — the profile's height / depth, front face to back
- **tooling work** — a coarse Fibonacci value: 1, 2, 3, 5, or 8 (see below)
- **waste factor** — milling yield-loss multiplier (≥ 1.0), **settled as a
  multiplier** (e.g. `1.15`, not `15%`). How much bigger the blank is than the
  finished profile, plus chips hogged out shaping it, *and* the leftover width
  when a board yields multiple side-by-side sticks (see Pricing inputs below —
  that leftover is folded in here rather than modelled separately). A *pricing
  input*, not a price; bumps the bare price per foot. Rough starting guidance,
  not a fixed table:

  | Tooling work | Waste factor |
  |---|---|
  | 1–2 (simple square/rectangular) | ~1.1 |
  | 3–5 (shaped: ogee, cove, …) | ~1.2–1.3 |
  | 8 (complex geometry) | ~1.4–1.5 |

  This is a correlation to start from, not a formula — waste factor stays its
  own field, set per Moulding.
- **minimum footage (optional override)** — if set, replaces the shop-default
  minimum footage for this profile. Usually unset; some profiles warrant a higher
  minimum. See [`design-moulding.md`](design-moulding.md) and
  [`pricing.md`](pricing.md) for how the minimum is applied.
- **`id`** — a stable integer identity, assigned by the shop catalog. Exists
  specifically so an external, hand-editable table (see below) can reference
  a Moulding without duplicating or embedding any of its other fields.

### Not on Moulding (moved out — ADR 0010)

- **Which lumber stock this profile is milled from** — originally a
  `source_lumber_size` field directly on Moulding (ADR 0007), naming a
  `(thickness, width)` pair per milling orientation. **Superseded**: this is
  now a separate, hand-editable table,
  `PricingContext.moulding_lumber_sources` (keyed by `(moulding.id,
  milling_orientation) → stock_size_id`), not a Moulding fact at all — see
  [`lumber.md`](lumber.md) and
  [`../decisions/0010-moulding-lumber-sources-as-tables.md`](../decisions/0010-moulding-lumber-sources-as-tables.md).
  The reasoning that originally motivated putting it on the Moulding record
  (not computed from geometry; a shop may deliberately over-spec a board;
  species-independent) still holds — only *where* the fact lives changed.

### STANDARD only

- **rabbet depth** — how far the front lip laps inward over the glazing / art
  edge. **Default 1/4" (0.25).** Drives sight size (`sight ≈ glazing − 2·depth`).
- **rabbet height** — how far back the recess goes, front to back. Drives whether
  the framing package fits (`stack_fits`).

### FLOAT only

- **internal height** — distance from the float board to the face of the
  moulding (the depth of the well behind the canvas).
- **float board thickness** — **default 3/8" (0.375).**

### Not on Moulding

- **float gap** — the space between the edge of the artwork and the inside of the
  moulding on a float frame (**default 1/4"**). This is *not* a moulding-level
  fact, but a float frame's dimensions cannot be specified without it, so it
  lives on [`DesignMoulding`](design-moulding.md).

### Reference only

- **`diagram_path`** — a path/filename pointing at a cross-section diagram
  (e.g. a Fusion 360 export), for visually matching a catalog entry to the
  real profile. Purely reference metadata — the pricing engine never reads it,
  and it isn't one of the "no material/finish/price" exclusions above because
  it isn't a fabrication or pricing fact at all.

### Explicitly deferred

- Detailed **profile shape** (curved, slanted, ogee, stepped, coved). For now the
  geometry is just the scalar dimensions above; a richer shape description comes
  later and must not force a rewrite. `diagram_path` (above) is a stopgap for
  visual identification in the meantime, not a structured shape description.

---

# Tooling work

Every Moulding takes some shop tooling / setup effort to produce. Model this as
**tooling work** — a coarse estimate on the Fibonacci scale **1, 2, 3, 5, 8**,
similar to story points. It is a rough size, **not** exact time or dollars.

| Tooling work | Example |
|---|---|
| **1** | a simple square / rectangular profile; table-saw passes only |
| **2** | a few more table-saw passes / a bit more setup |
| **3** | table-saw operations + one shaping pass on the shaper / moulder |
| **5** | table-saw operations + multiple shaping passes / multiple setups |
| **8** | complex geometry; many passes and setups |

(1, 3, and 5 are the anchor points; 2 and 8 are judgement calls in between and
beyond.)

The pricing engine may later **interpret the same value differently by context** —
setup complexity matters much more for a one-off custom frame than for a standard
Offering that has been batch-produced and effectively amortized its setup.
Preserve that distinction; do not bake a single cost into the value.

---

# Pricing inputs, not prices

A Moulding exposes facts a pricing engine consumes — **tooling work**, **waste
factor**, an optional **minimum footage** override — plus its geometry. It still
carries **no prices** and no material / finish / joinery.

The **waste factor** is *milling* waste: the blank is bigger than the finished
profile, and shaping hogs out chips. It inflates the bare price per foot. The
bare price per foot itself is *derived* from geometry + Material + current lumber
prices; see [`pricing.md`](pricing.md).

## The milling convention (fixed shop practice, not a Moulding field)

A moulding stick is milled from a board in one of two ways. **Which way applies
to a given piece is chosen at the [`DesignMoulding`](design-moulding.md) level
(`milling_orientation`), not stored here** — the same Moulding geometry can be
milled either way for different Designs:

- **`from_board_edge`** (the default / common case): the moulding's **face
  width** becomes the required **board thickness**; the **overall height**
  becomes the required **board width**. A board can yield more than one
  side-by-side stick this way — e.g. two 3/4"-wide × 2"-tall sticks out of one
  3/4"-thick × 5½"-wide board. The moulding's decorative face is what was the
  board's edge.
- **`from_board_face`** (rotated 90° from the above): **overall height**
  becomes the required board thickness; **face width** becomes the required
  board width. The moulding's decorative face is what was the board's broad
  face.

Same lumber lookup shape either way — see [`pricing.md`](pricing.md). Which
*specific* board size (thickness × width) is used for each orientation is not
computed from this convention — it's an explicit, per-Moulding fact, now held
in `PricingContext.moulding_lumber_sources` rather than on the Moulding
itself (see "Not on Moulding" above).

---

# Relationships

- **DesignMoulding** — references a Moulding as the chosen geometry. The
  DesignMoulding, not the Moulding, carries Material / Finish / Extras / joinery
  method / size / float gap / milling orientation.
- **Offering** — references a Moulding as part of a standard configuration.
- **Material, Finish, Extra, joinery method** — **not** directly related to
  Moulding. They attach at the DesignMoulding / Offering layer.
- **Pricing** — consumes Moulding geometry + tooling work as facts.
- **Strainer** — **not** a Moulding. Do not extract a shared `ProfileGeometry`
  abstraction just because both may be milled from wood profiles (see the generic
  abstraction warning in AGENTS.md).
- **Vendor / Product** — whether bought-in manufacturer moulding (Roma, Omega,
  …) is represented as a Moulding + external source, or as a Product, or as
  something else, is an **open question**. The current model is oriented around
  the shop milling its own profiles.

Required vs optional: a DesignMoulding presumably must reference *some* Moulding
geometry to be meaningful; whether that can be a placeholder early in design is
an open question.

---

# Derived Values

- **which lumber row to read** — `pricing_context.stock_size_for(moulding.id,
  design_moulding.milling_orientation)` gives a `stock_size_id`; combined
  with Material's species, this selects the row in [`lumber.md`](lumber.md)
  the pricing chain reads. A direct lookup against a hand-editable table, not
  computed from `face width × overall height` (that bounding box is still
  used for the blank-volume calculation, just not for picking the stock size
  — see [`pricing.md`](pricing.md)).
- **linear footage** required for a frame — a function of the finished size and
  the profile's face width. (A cutting allowance for mitres is deferred.)
- **finished / outer size** of a framed piece — the package (STANDARD) or
  artwork-plus-gap (FLOAT) size grown by the face width on each side (and by any
  additional build-up moulding).
- **sight size** (STANDARD) — the glazing size minus twice the rabbet depth.
- **stack fits the recess?** (STANDARD only) — compare the framing package depth
  to the rabbet height.
- **bare price per foot** — derived downstream from geometry + the
  DesignMoulding's milling orientation + Material + lumber prices + waste
  factor; see [`pricing.md`](pricing.md).

None of these are stored on the Moulding — they depend on the Design and on
current lumber prices.

---

# Business Rules / Invariants

- face width > 0 and overall height > 0.
- A STANDARD moulding has a rabbet depth and a rabbet height; a FLOAT moulding
  has an internal height and a float board thickness, and **no rabbet**. Which
  fields are required depends on the type.
- `tooling work` ∈ {1, 2, 3, 5, 8}.
- `waste factor` ≥ 1.0.
- `id` is unique across the catalog and is the key `moulding_lumber_sources`
  (see [`lumber.md`](lumber.md)) joins against — not a Moulding-level
  invariant to check here, but a catalog-level one (enforced at import time
  in `data/moulding_catalog.py`).
- A Moulding should have a `moulding_lumber_sources` row for **at least one**
  milling orientation — whichever one(s) it's actually ever milled in;
  neither orientation is required by default. This is now a property of that
  external table, not something `Moulding.__post_init__` validates. Pricing a
  DesignMoulding in an orientation with no such row is an error condition.
- A Moulding carries **no** material, finish, embellishment, joinery method,
  milling orientation, stock, or price — only geometry, identity (`id`), and
  the pricing-input facts (tooling work, waste factor, optional
  minimum-footage override).
- House-milled and (eventually) bought-in mouldings are represented uniformly
  enough that a DesignMoulding doesn't care which it is — mechanism TBD.

---

# Historical / Snapshot Concerns

When a Design that uses a moulding is accepted, the system must eventually be
able to reproduce the exact geometry, tooling work, waste factor, the
`stock_size_id` the Moulding resolved to for that orientation, the
DesignMoulding's milling orientation, and the lumber price used, as of
acceptance. Later edits to the `moulding_lumber_sources` table (pointing a
Moulding at a different stock size) or to lumber prices must not reach
backward. Snapshot mechanism is **not being designed now**.

---

# Open Questions

The geometry fields and the tooling-work scale are settled (first pass) —
recorded in [`../decisions/0001-moulding-geometry-and-tooling-work.md`](../decisions/0001-moulding-geometry-and-tooling-work.md).
The milling convention, waste factor representation, and the lumber-table shape
are also settled (first pass) — recorded in
[`../decisions/0003-milling-orientation-and-lumber-table-keying.md`](../decisions/0003-milling-orientation-and-lumber-table-keying.md).
**Which lumber stock a Moulding is milled from**, per orientation — originally
an explicit per-Moulding field (`source_lumber_size`,
[`../decisions/0007-source-lumber-size.md`](../decisions/0007-source-lumber-size.md)),
now a separate hand-editable table instead
([`../decisions/0010-moulding-lumber-sources-as-tables.md`](../decisions/0010-moulding-lumber-sources-as-tables.md)) —
**resolves the "stocked board widths" question below** either way (there's no
longer a generic stocked-widths list to define; each Moulding is pointed at
its own board size).
Still open, mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

1. Should the STANDARD/FLOAT geometry difference be nullable fields, subtype
   models, separate geometry objects, or inheritance? (Domain distinction is
   documented; the representation is not chosen.)
2. How does tooling work affect **custom** pricing vs **standard Offering**
   (amortized) pricing?
3. How is bought-in manufacturer moulding represented relative to this
   geometry-first model?
4. Can a float **Offering** pin its own gap (so a standard float product has a
   fixed reveal), or is the float gap only ever defaulted per DesignMoulding?

---

# Pseudocode Sketch

Illustrative. Not a decision about where these values live.

```python
def linear_feet_for_frame(finished_w_in, finished_h_in, face_width_in):
    # each side's outer length grows by the face width at both ends
    # (a mitre cutting allowance is deferred)
    perimeter_in = 2 * (finished_w_in + face_width_in) \
                 + 2 * (finished_h_in + face_width_in)
    return perimeter_in / 12


def sight_size(glazing_w_in, glazing_h_in, rabbet_depth_in):
    # STANDARD only: the lip covers `rabbet_depth` on every edge
    return (glazing_w_in - 2 * rabbet_depth_in,
            glazing_h_in - 2 * rabbet_depth_in)


def stack_fits(package_depth_in, rabbet_height_in):
    # STANDARD only; FLOAT mouldings have no rabbet
    return package_depth_in <= rabbet_height_in


def float_finished_size(art_w_in, art_h_in, gap_in, face_width_in):
    # FLOAT only: gap comes from the DesignMoulding, not the Moulding
    return (art_w_in + 2 * gap_in + 2 * face_width_in,
            art_h_in + 2 * gap_in + 2 * face_width_in)
```
