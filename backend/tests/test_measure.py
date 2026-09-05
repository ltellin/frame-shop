from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.measure import Dimensions, parse_inches


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("16", Decimal("16")),
        ("16.5", Decimal("16.5")),
        ("16 1/2", Decimal("16.5")),
        ("16-1/2", Decimal("16.5")),
        ("1/2", Decimal("0.5")),
        (20, Decimal("20")),
    ],
)
def test_parse_inches(raw, expected):
    assert parse_inches(raw) == expected


def test_parse_inches_rejects_garbage():
    with pytest.raises(ValueError):
        parse_inches("not a number")


def test_dimensions_derived():
    d = Dimensions.of("16", "20")
    assert d.united_in == Decimal("36")
    assert d.perimeter_in == Decimal("72")
    assert d.area_sqin == Decimal("320")
    assert d.grown_by(Decimal("2")).width_in == Decimal("20")
