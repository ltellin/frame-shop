import pytest

from frameshop_pricing.catalog import get_moulding
from frameshop_pricing.data.moulding_catalog import MOULDINGS
from frameshop_pricing.models import MillingOrientation, MouldingType
from frameshop_pricing.pricing_context import PricingContext


def test_get_moulding_returns_the_catalog_entry():
    moulding = get_moulding(2001)
    assert moulding.type == MouldingType.STANDARD
    assert MillingOrientation.FROM_BOARD_EDGE in moulding.source_lumber_size


def test_get_moulding_raises_a_helpful_error_for_an_unknown_id():
    with pytest.raises(KeyError, match="999"):
        get_moulding(999)


def test_every_catalog_moulding_has_a_cherry_lumber_price():
    """A source_lumber_size with no row in LUMBER_PRICES makes that moulding unpriceable."""
    prices = PricingContext.load_default().lumber_prices
    missing = [
        id_ for id_, m in MOULDINGS.items()
        if any(("cherry", t, w) not in prices for t, w in m.source_lumber_size.values())
    ]
    assert not missing, f"mouldings with no cherry lumber price: {missing}"
