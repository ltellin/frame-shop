"""The shop's own moulding catalog — one entry per profile, keyed by a plain
integer ID.

Add your mouldings here directly, one per ID. `diagram_path` is just a
reference string (e.g. a path to your Fusion 360 cross-section export) — the
pricing engine never reads it, it's purely for visually matching a catalog
entry to the real profile.

Only `source_lumber_size[FROM_BOARD_EDGE]` is required; add a
`FROM_BOARD_FACE` entry too only if you'd actually mill that profile rotated.

See docs/domain/moulding.md for what each field means.

ID ranges in use so far:
  1000s - 1/2" wide profiles
  2000s - 3/4" wide profiles
  3000s - 1" wide profiles (same shapes as the 2000s, just wider)
"""

from __future__ import annotations

from ..models import MillingOrientation, Moulding, MouldingType

# int id -> Moulding. Add new entries below with the next integer id.
MOULDINGS: dict[int, Moulding] = {
    1001: Moulding(
        name='1/2" Square',
        type=MouldingType.STANDARD,
        face_width_in=0.5,
        overall_height_in=0.75,
        tooling_work=1,  # simple square profile, table-saw passes only
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.5, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/1001-square.png",  # placeholder — point at your real export
    ),
    1002: Moulding(
        name='1/2" Square tall',
        type=MouldingType.STANDARD,
        face_width_in=0.5,
        overall_height_in=1.75,
        tooling_work=1,  # simple square profile, table-saw passes only
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.5, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/1002-square-tall.png",  # placeholder — point at your real export
    ),
    2001: Moulding(
        name='3/4" Square',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=0.75,
        tooling_work=1,  # simple square profile, table-saw passes only
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),  # 4/4 S4S x 3-1/2" wide
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/2001-square.png",  # placeholder — point at your real export
    ),
    2002: Moulding(
        name='3/4" Square, tall',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.75,
        tooling_work=1,
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/2002-square-tall.png",
    ),
    2003: Moulding(
        name='3/4" slant',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.25,
        tooling_work=2,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/2003-slant.png",
    ),
    2004: Moulding(
        name='3/4" slant tall',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.875,
        tooling_work=2,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/2004-slant-tall.png",
    ),
    2005: Moulding(
        name='3/4" rounded slant',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.25,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/2005-rounded-slant.png",
    ),
    2006: Moulding(
        name='3/4" rounded slant tall',
        type=MouldingType.STANDARD,
        face_width_in=0.75,
        overall_height_in=1.875,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (0.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/2006-rounded-slant-tall.png",
    ),
    # --- 3000s: 1" wide versions of the 2000s — same heights/tooling/waste,
    # just a wider face and matching board thickness ---
    3001: Moulding(
        name='1" Square',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=0.75,
        tooling_work=1,
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.0, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/3001-square.png",
    ),
    3002: Moulding(
        name='1" Square, tall',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.75,
        tooling_work=1,
        waste_factor=1.1,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.0, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/3002-square-tall.png",
    ),
    3003: Moulding(
        name='1" slant',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.25,
        tooling_work=2,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.0, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/3003-slant.png",
    ),
    3004: Moulding(
        name='1" slant tall',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.875,
        tooling_work=2,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.0, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/3004-slant-tall.png",
    ),
    3005: Moulding(
        name='1" rounded slant',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.25,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.0, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.375,
        diagram_path="diagrams/3005-rounded-slant.png",
    ),
    3006: Moulding(
        name='1" rounded slant tall',
        type=MouldingType.STANDARD,
        face_width_in=1.0,
        overall_height_in=1.875,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.0, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=1.625,
        diagram_path="diagrams/3006-rounded-slant-tall.png",
    ),
    4001: Moulding(
        name='outside round inside slant',
        type=MouldingType.STANDARD,
        face_width_in=1.25,
        overall_height_in=1,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_EDGE: (1.25, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.5,
        diagram_path="diagrams/4001-outside-round-inside-slant.png",
    ),
    5001: Moulding(
        name='outside slant',
        type=MouldingType.STANDARD,
        face_width_in=1.75,
        overall_height_in=.75,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_FACE: (.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.625,
        diagram_path="diagrams/5001-slant.png",
    ),
    5002: Moulding(
        name='outside scoop inside bevel',
        type=MouldingType.STANDARD,
        face_width_in=1.75,
        overall_height_in=.75,
        tooling_work=3,
        waste_factor=1.25,
        source_lumber_size={
            MillingOrientation.FROM_BOARD_FACE: (.75, 3.5),
        },
        rabbet_depth_in=0.25,
        rabbet_height_in=0.625,
        diagram_path="diagrams/5002-outside-scoop-inside-bevel.png",
    ),
}
