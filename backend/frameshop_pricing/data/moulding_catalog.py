"""The shop's own moulding catalog — one entry per profile, keyed by a plain
integer ID.

Add your mouldings here directly, one per ID — the `id=` field must match the
dict key (checked below at import time).

Each entry's diagram (a cross-section SVG, for visually matching a catalog
entry to the real profile) is **not** a field here — it's a file named
`<id>.svg` in the repo-root `diagrams/` directory (outside the installed
package; a catalog id is all that's needed to find it). See
docs/decisions/0012-moulding-diagram-convention.md.

Which lumber stock each moulding is milled from (thickness x width, per
milling orientation) is **not** set here — see data/moulding_lumber_sources.csv
and data/stock_sizes.csv, a separate hand-editable table. See
docs/decisions/0010-moulding-lumber-sources-as-tables.md for why.

See docs/domain/moulding.md for what each field means.

ID ranges in use so far:
  1000s - 1/2" wide profiles
  2000s - 3/4" wide profiles
  3000s - 1" wide profiles (same shapes as the 2000s, just wider)
"""

from __future__ import annotations

from ..models import Moulding, MouldingType

# int id -> Moulding. Add new entries below with the next integer id.
MOULDINGS: dict[int, Moulding] = {
    1001: Moulding(
        id=1001,
        name='1/2" Square',
        type=MouldingType.STANDARD,
        face_width_in=0.5,
        overall_height_in=0.75,
        tooling_work=1,  # simple square profile, table-saw passes only
        waste_factor=1.1,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    1002: Moulding(
        id=1002,
        name='1/2" Square tall',
        type=MouldingType.STANDARD,
        face_width_in=0.5,
        overall_height_in=1.75,
        tooling_work=1,  # simple square profile, table-saw passes only
        waste_factor=1.1,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    2001: Moulding(
        id=2001,
        name='3/4" Square',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=0.75,
        tooling_work=1,  # simple square profile, table-saw passes only
        waste_factor=1.1,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    2002: Moulding(
        id=2002,
        name='3/4" Square, tall',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.75,
        tooling_work=1,
        waste_factor=1.1,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    2003: Moulding(
        id=2003,
        name='3/4" slant',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.25,
        tooling_work=2,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    2004: Moulding(
        id=2004,
        name='3/4" slant tall',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.875,
        tooling_work=2,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    2005: Moulding(
        id=2005,
        name='3/4" rounded slant',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.25,
        tooling_work=3,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    2006: Moulding(
        id=2006,
        name='3/4" rounded slant tall',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.875,
        tooling_work=3,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    2020: Moulding(
        id=2020,
        name='3/4" double slant',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.75,
        tooling_work=5,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    # --- 3000s: 1" wide versions of the 2000s — same heights/tooling/waste,
    # just a wider face, milled from 5/4 S4S (1-1/16") stock ---
    3001: Moulding(
        id=3001,
        name='1" Square',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=0.75,
        tooling_work=1,
        waste_factor=1.1,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    3002: Moulding(
        id=3002,
        name='1" Square, tall',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.75,
        tooling_work=1,
        waste_factor=1.1,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    3003: Moulding(
        id=3003,
        name='1" slant',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.25,
        tooling_work=2,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    3004: Moulding(
        id=3004,
        name='1" slant tall',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.875,
        tooling_work=2,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    3005: Moulding(
        id=3005,
        name='1" rounded slant',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.25,
        tooling_work=3,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
    ),
    3006: Moulding(
        id=3006,
        name='1" rounded slant tall',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.875,
        tooling_work=3,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
    ),
    4007: Moulding(
        id=4007,
        name='outside round inside slant',
        type=MouldingType.STANDARD,
        face_width_in=1.25,
        overall_height_in=1,
        tooling_work=3,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.5,
    ),
    5001: Moulding(
        id=5001,
        name='outside slant',
        type=MouldingType.STANDARD,
        face_width_in=1.75,
        overall_height_in=.75,
        tooling_work=2,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.625,
    ),
    5002: Moulding(
        id=5002,
        name='outside scoop inside bevel',
        type=MouldingType.STANDARD,
        face_width_in=1.75,
        overall_height_in=.75,
        tooling_work=3,
        waste_factor=1.25,
        rabbet_depth_in=0.25,
        rabbet_height_in=0.625,
    ),
}

for _key, _moulding in MOULDINGS.items():
    if _moulding.id != _key:
        raise ValueError(
            f"Moulding dict key {_key} does not match its id field {_moulding.id} — "
            "fix the mismatched entry in moulding_catalog.py"
        )
del _key, _moulding
