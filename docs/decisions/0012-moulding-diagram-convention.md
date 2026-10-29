# 0012 — Moulding diagrams are a convention-based file, not a stored field

Status: accepted. Date: 2026-10-18.

## Context

`Moulding.diagram_path` (a free-form string, e.g.
`"diagrams/1002-square-tall.png"`) was never backed by an actual file —
no `diagrams/` directory existed in the repo at all, so every one of the 17
catalog entries was a dangling reference. The owner wants a real system:
each moulding's diagram doubles as its default thumbnail in the website
ordering form now, and eventually the shop's own software UI, and a
*second*, separate system for example photos (website-only, no software
use case) is being built alongside this in `my_photo_site`.

Rebuilding `my_photo_site`'s own (unrelated, pre-existing) attempt at this
surfaced the actual risk of a free-form per-entry path: 13 of its 17
moulding entries pointed at the *wrong* moulding's placeholder image,
because nothing forced the stored string to match the entry's own id.

## Decision

**A diagram is a file, not a Moulding field — `diagrams/<id>.svg` in a new
repo-root `diagrams/` directory**, found by a catalog id alone.
`Moulding.diagram_path` is removed entirely.

- **SVG**, not PNG/raster — scales cleanly from a small catalog-grid
  thumbnail up to a larger detail view, stays crisp, and is small/diffable.
- **Outside the installed package** (`diagrams/`, not
  `frameshop_pricing/data/`) — this is a static UI asset for whatever
  consumes it (a website today, the shop's own software later), not engine
  runtime config. Bundling it into the Python package's data would repeat
  the exact class of bug just fixed in v0.3.2 (silently-missing package
  data) for an asset the engine itself has no reason to load.
- **No filename slug** — just `<id>.svg`. The id is already the unique,
  stable, cross-repo key (the same id `my_photo_site`'s own moulding data
  and the pricing engine both use); a slug derived from the moulding's
  `name` is one more thing that can drift when a moulding is renamed, for
  no benefit a lookup-by-id doesn't already give.
- **A repo-level consistency check** (`backend/tests/test_diagrams.py`)
  reports which catalog ids have no matching file yet, without blocking the
  normal test suite — real diagrams are produced by hand (e.g. a traced
  Fusion 360 cross-section export), not something to fabricate placeholder
  art for.

## Alternatives considered

- **Keep `diagram_path` as a field, just validate it matches `<id>.svg`.**
  Rejected — a validated-but-still-stored field is strictly more moving
  parts than a pure convention, for no actual flexibility gained (no
  realistic scenario needs a moulding's diagram at a different path than
  its own id implies).
- **PNG**, matching the original docstring's "e.g. a Fusion 360 export"
  framing. Rejected — a raster export doesn't scale cleanly across
  thumbnail and larger display sizes the way SVG line art does, and the
  owner confirmed SVG.
- **Store diagrams inside `frameshop_pricing/data/`** alongside the lumber
  CSVs. Rejected — those CSVs are genuinely read by the engine at runtime;
  diagrams never are. Mixing the two blurs "engine config" and "UI asset"
  and risks the same missing-package-data failure mode for no reason.

## Consequences

- `Moulding` loses `diagram_path`. Any code constructing a `Moulding` with
  that keyword now breaks (none does, as of this change — it was unused
  outside the catalog itself).
- `data/moulding_catalog.py`'s 17 entries no longer set it.
- Consumers (a website, the future software UI) resolve a moulding's
  diagram themselves as `diagrams/{id}.svg`, relative to wherever they've
  obtained a copy of `diagrams/` — `my_photo_site` does this via a small
  sync script copying from a sibling frame-shop checkout, documented on
  its own side (`docs/VISION.md`), not this repo's concern.
- Ships with **zero real diagrams** — `test_diagrams.py` reports all 17 ids
  missing until the owner adds real files; this is expected, not a bug.
