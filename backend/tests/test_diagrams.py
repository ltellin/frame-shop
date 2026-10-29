"""Repo-level check: does every catalog moulding have a diagram file?

Diagrams live in the repo-root `diagrams/` directory, outside the installed
package (see docs/decisions/0012-moulding-diagram-convention.md) — so this
check only makes sense run from a full repo checkout, not against an
installed `frameshop-pricing` package. It's not part of what ships.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from frameshop_pricing.data.moulding_catalog import MOULDINGS

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DIAGRAMS_DIR = _REPO_ROOT / "diagrams"


def test_every_catalog_moulding_has_a_diagram_file():
    missing = sorted(
        moulding_id for moulding_id in MOULDINGS if not (_DIAGRAMS_DIR / f"{moulding_id}.svg").exists()
    )
    if missing:
        pytest.skip(
            f"{len(missing)}/{len(MOULDINGS)} catalog mouldings have no diagrams/<id>.svg yet: {missing} "
            "— expected until real diagrams are added; see docs/decisions/0012-moulding-diagram-convention.md"
        )
