# Artwork / Piece

> Status: **not yet specified.** Lightweight template only. Do not implement from
> it.

# Definition

The physical thing being framed, or its stand-in (a photo to be printed, an
object destined for a shadowbox). Some Designs have no artwork at all — an empty
frame, loose mats, a raw material sale, or a standard framed **product** such as
a mirror sold online with no customer artwork and no bespoke design
consultation. This reinforces that **Artwork must not be a prerequisite for
Design**. What concept represents "the thing being framed/presented" when it is
not customer artwork is an open question.

# Responsibilities

_TBD._ Likely: describe/identify the piece, record its dimensions and nature,
carry handling notes, possibly hold an image.

# Possible Attributes

Tentative. Not a schema.

- description / title
- kind (paper, canvas, photo, textile, object, …)
- dimensions
- condition / handling notes
- image(s)

# Relationships

- **Design** — a Design may be *about* an artwork. Optional while designing.
  Whether Artwork must exist before acceptance or only before production is an
  open question.
- **Customer** — the piece belongs to someone, but that association may arrive
  late.

# Derived Values

_TBD._

# Business Rules / Invariants

- A Design can exist with no Artwork.

# Historical / Snapshot Concerns

_TBD._

# Open Questions

Tracked in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

# Pseudocode Sketch

_None yet._
