"""Measurement value objects and helpers.

All measurements are in inches, held as Decimal. Fractional shop input like
``16 1/2`` or ``16-1/2`` is parsed to Decimal at the edge.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

_FRACTION_RE = re.compile(
    r"^\s*(?:(?P<whole>\d+(?:\.\d+)?)\s+)?(?:(?P<num>\d+)\s*/\s*(?P<den>\d+))?\s*$"
)


def parse_inches(value: str | int | float | Decimal) -> Decimal:
    """Parse a measurement into inches as Decimal.

    Accepts plain numbers ("16", "16.5") and mixed fractions ("16 1/2", "16-1/2",
    "1/2").
    """
    if isinstance(value, (int, Decimal)):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))

    text = value.strip().replace("-", " ")
    if not text:
        raise ValueError("empty measurement")

    # Pure decimal / integer.
    try:
        return Decimal(text)
    except Exception:
        pass

    match = _FRACTION_RE.match(text)
    if not match or (match.group("num") is None and match.group("whole") is None):
        raise ValueError(f"cannot parse measurement: {value!r}")

    whole = Decimal(match.group("whole")) if match.group("whole") else Decimal(0)
    if match.group("num") is not None:
        whole += Decimal(match.group("num")) / Decimal(match.group("den"))
    return whole


@dataclass(frozen=True, slots=True)
class Dimensions:
    """A width x height rectangle in inches."""

    width_in: Decimal
    height_in: Decimal

    @classmethod
    def of(cls, width: object, height: object) -> Dimensions:
        return cls(parse_inches(width), parse_inches(height))  # type: ignore[arg-type]

    @property
    def united_in(self) -> Decimal:
        """United inches: width + height. Common framing pricing input."""
        return self.width_in + self.height_in

    @property
    def perimeter_in(self) -> Decimal:
        return 2 * (self.width_in + self.height_in)

    @property
    def area_sqin(self) -> Decimal:
        return self.width_in * self.height_in

    def grown_by(self, delta_each_side: Decimal) -> Dimensions:
        """Return a rectangle expanded by ``delta_each_side`` on every edge."""
        return Dimensions(
            self.width_in + 2 * delta_each_side,
            self.height_in + 2 * delta_each_side,
        )

    def __str__(self) -> str:
        return f"{self.width_in} x {self.height_in} in"
