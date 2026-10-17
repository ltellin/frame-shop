"""PricingContext bundles every shop-configurable pricing input.

See docs/domain/pricing.md and docs/decisions/0006-*.md and 0010-*.md. A
PricingContext is built from one centralized, hand-editable location per shop
(frameshop_pricing/data/) — the formulas in engine.py never hardcode a shop's
actual numbers.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .models import ExtraRate, FinishRate, JoineryMethod, MillingOrientation, StockSize

_DATA_DIR = Path(__file__).parent / "data"


def _load_stock_sizes(path: Path) -> dict[str, StockSize]:
    with path.open(newline="") as f:
        return {
            row["stock_size_id"]: StockSize(
                nominal_thickness=row["nominal_thickness"],
                thickness_in=float(row["thickness_in"]),
                width_in=float(row["width_in"]),
            )
            for row in csv.DictReader(f)
        }


def _load_lumber_prices(path: Path) -> dict[tuple[str, str], float]:
    with path.open(newline="") as f:
        return {
            (row["species"], row["stock_size_id"]): float(row["price_per_bf"])
            for row in csv.DictReader(f)
        }


def _load_moulding_lumber_sources(path: Path) -> dict[tuple[int, MillingOrientation], str]:
    with path.open(newline="") as f:
        return {
            (int(row["moulding_id"]), MillingOrientation(row["milling_orientation"])): row["stock_size_id"]
            for row in csv.DictReader(f)
        }


@dataclass(frozen=True)
class PricingContext:
    # stock_size_id -> dimensions (reference only; the formulas never read
    # thickness_in/width_in directly, only the id, to look up a price)
    stock_sizes: dict[str, StockSize]
    # (species, stock_size_id) -> $ per board foot
    lumber_prices: dict[tuple[str, str], float]
    # (moulding id, milling orientation) -> stock_size_id
    moulding_lumber_sources: dict[tuple[int, MillingOrientation], str]
    finish_rates: dict[str, FinishRate]  # finish name -> two-rate pricing
    extra_rates: dict[str, ExtraRate]  # extra name -> rate
    joinery_rates: dict[JoineryMethod, float]  # joinery method -> flat $ per frame
    chop_charge_per_frame: float  # flat $ per frame, added for CHOP and JOIN order forms
    tooling_work_rate_per_foot: float
    default_minimum_footage: float
    default_non_offering_labor_charge_per_foot: float
    material_markup_rate: float

    @classmethod
    def load_default(cls) -> "PricingContext":
        """Build a PricingContext from this shop's editable data."""
        from .data import shop_pricing_data as d

        return cls(
            stock_sizes=_load_stock_sizes(_DATA_DIR / "stock_sizes.csv"),
            lumber_prices=_load_lumber_prices(_DATA_DIR / "lumber_prices.csv"),
            moulding_lumber_sources=_load_moulding_lumber_sources(
                _DATA_DIR / "moulding_lumber_sources.csv"
            ),
            finish_rates=d.FINISH_RATES,
            extra_rates=d.EXTRA_RATES,
            joinery_rates=d.JOINERY_RATES,
            chop_charge_per_frame=d.CHOP_CHARGE_PER_FRAME,
            tooling_work_rate_per_foot=d.TOOLING_WORK_RATE_PER_FOOT,
            default_minimum_footage=d.DEFAULT_MINIMUM_FOOTAGE,
            default_non_offering_labor_charge_per_foot=d.DEFAULT_NON_OFFERING_LABOR_CHARGE_PER_FOOT,
            material_markup_rate=d.MATERIAL_MARKUP_RATE,
        )

    def stock_size_for(self, moulding_id: int, orientation: MillingOrientation) -> str:
        """Which stock_size_id a given moulding (milled in a given
        orientation) is cut from."""
        key = (moulding_id, orientation)
        try:
            return self.moulding_lumber_sources[key]
        except KeyError as exc:
            raise KeyError(
                f"No lumber source configured for moulding id={moulding_id!r}, "
                f"orientation={orientation!r} — add a row to data/moulding_lumber_sources.csv"
            ) from exc

    def lumber_price_per_bf(self, species: str, stock_size_id: str) -> float:
        key = (species, stock_size_id)
        try:
            return self.lumber_prices[key]
        except KeyError as exc:
            raise KeyError(
                f"No lumber price for species={species!r}, stock_size_id={stock_size_id!r} "
                "— add it to data/lumber_prices.csv"
            ) from exc
