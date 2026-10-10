import pytest

from frameshop_pricing.catalog import get_moulding
from frameshop_pricing.models import MillingOrientation, MouldingType


def test_get_moulding_returns_the_catalog_entry():
    moulding = get_moulding(2001)
    assert moulding.type == MouldingType.STANDARD
    assert MillingOrientation.FROM_BOARD_EDGE in moulding.source_lumber_size


def test_get_moulding_raises_a_helpful_error_for_an_unknown_id():
    with pytest.raises(KeyError, match="999"):
        get_moulding(999)
