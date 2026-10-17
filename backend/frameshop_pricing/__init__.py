"""Moulding pricing engine.

Implements docs/domain/{moulding,material,lumber,finish,extra,offering,
design-moulding,pricing}.md and the decisions in docs/decisions/0002-0010.

This package is deliberately decoupled from Design/DesignMoulding, which
aren't specified yet — see MouldingLineInput in models.py. A future Design
implementation should build a MouldingLineInput from itself and call
price_moulding_line / price_total; this package should not need to change
when that happens.
"""

from .catalog import get_moulding
from .engine import price_moulding_line, price_total
from .models import (
    Extra,
    ExtraRate,
    FinishRate,
    JoineryMethod,
    MillingOrientation,
    Moulding,
    MouldingLineInput,
    MouldingType,
    Offering,
    OrderForm,
    StockSize,
)
from .pricing_context import PricingContext

__all__ = [
    "Extra",
    "ExtraRate",
    "FinishRate",
    "JoineryMethod",
    "MillingOrientation",
    "Moulding",
    "MouldingLineInput",
    "MouldingType",
    "Offering",
    "OrderForm",
    "PricingContext",
    "StockSize",
    "get_moulding",
    "price_moulding_line",
    "price_total",
]
