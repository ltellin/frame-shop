"""Moulding catalog lookup.

Raw catalog data lives in data/moulding_catalog.py — add/edit mouldings there
directly, no code changes needed. This module is just the lookup, mirroring
pricing_context.py's relationship to data/shop_pricing_data.py.

Deliberately kept inside the `pricing` package for now, since pricing is the
only current consumer of the moulding catalog (Design/DesignMoulding aren't
implemented yet). If/when something else needs to look up mouldings by id,
this module and data/moulding_catalog.py can move out to their own package
without any change to their contents.
"""

from __future__ import annotations

from .models import Moulding


def get_moulding(moulding_id: int) -> Moulding:
    from .data import moulding_catalog as c

    try:
        return c.MOULDINGS[moulding_id]
    except KeyError as exc:
        raise KeyError(
            f"No moulding with id={moulding_id!r} in the catalog — "
            "add it to frameshop_pricing/data/moulding_catalog.py"
        ) from exc
