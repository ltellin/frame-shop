import pytest

from frameshop_pricing.catalog import get_moulding
from frameshop_pricing.data.moulding_catalog import MOULDINGS
from frameshop_pricing.models import MouldingType
from frameshop_pricing.pricing_context import PricingContext


def test_get_moulding_returns_the_catalog_entry():
    moulding = get_moulding(2001)
    assert moulding.type == MouldingType.STANDARD
    assert moulding.id == 2001


def test_get_moulding_raises_a_helpful_error_for_an_unknown_id():
    with pytest.raises(KeyError, match="999"):
        get_moulding(999)


def test_every_catalog_moulding_has_a_lumber_source():
    """A moulding with zero rows in moulding_lumber_sources.csv is
    unpriceable in any orientation — this is the table-shaped version of the
    guarantee Moulding.__post_init__ used to enforce directly."""
    sources = PricingContext.load_default().moulding_lumber_sources
    sourced_ids = {moulding_id for moulding_id, _orientation in sources}
    missing = sorted(set(MOULDINGS) - sourced_ids)
    assert not missing, f"mouldings with no lumber source configured at all: {missing}"


def test_every_catalog_moulding_has_a_cherry_lumber_price():
    """A lumber source with no matching row in lumber_prices.csv makes that
    moulding unpriceable. Cherry is just a canary species with full price
    coverage, not something pricing-significant — this is a cross-table
    consistency check, not a pricing-correctness test."""
    ctx = PricingContext.load_default()
    missing = [
        (moulding_id, orientation)
        for (moulding_id, orientation), stock_size_id in ctx.moulding_lumber_sources.items()
        if ("cherry", stock_size_id) not in ctx.lumber_prices
    ]
    assert not missing, f"moulding/orientation pairs with no cherry lumber price: {missing}"
