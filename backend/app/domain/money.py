"""Money value object.

Money is stored and passed around as an integer number of cents. Never use float
for money. Rounding happens explicitly, once, when a computed amount is turned
into cents.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("1")


def to_cents(amount: Decimal | int | str) -> int:
    """Round a currency amount (in whole units, e.g. dollars) to integer cents."""
    value = Decimal(amount) * 100
    return int(value.quantize(CENTS, rounding=ROUND_HALF_UP))


def cents_to_decimal(cents: int) -> Decimal:
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str = "USD"

    @classmethod
    def zero(cls, currency: str = "USD") -> Money:
        return cls(0, currency)

    @classmethod
    def of(cls, amount: Decimal | int | str, currency: str = "USD") -> Money:
        return cls(to_cents(amount), currency)

    def __add__(self, other: Money) -> Money:
        self._check(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._check(other)
        return Money(self.cents - other.cents, self.currency)

    def _check(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"currency mismatch: {self.currency} vs {other.currency}")

    @property
    def decimal(self) -> Decimal:
        return cents_to_decimal(self.cents)

    def __str__(self) -> str:
        return f"{self.decimal} {self.currency}"
