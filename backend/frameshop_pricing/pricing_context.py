"""PricingContext bundles every shop-configurable pricing input.

See docs/domain/pricing.md and docs/decisions/0006-*.md. A PricingContext is
built from one centralized, hand-editable location per shop
(frameshop_pricing/data/shop_pricing_data.py) — the formulas in engine.py never hardcode
a shop's actual numbers.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import ExtraRate, FinishRate, JoineryMethod


@dataclass(frozen=True)
class PricingContext:
    # (species, thickness_in, width_in) -> $ per board foot
    lumber_prices: dict[tuple[str, float, float], float]
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
        """Build a PricingContext from this shop's editable data module."""
        from .data import shop_pricing_data as d

        return cls(
            lumber_prices=d.LUMBER_PRICES,
            finish_rates=d.FINISH_RATES,
            extra_rates=d.EXTRA_RATES,
            joinery_rates=d.JOINERY_RATES,
            chop_charge_per_frame=d.CHOP_CHARGE_PER_FRAME,
            tooling_work_rate_per_foot=d.TOOLING_WORK_RATE_PER_FOOT,
            default_minimum_footage=d.DEFAULT_MINIMUM_FOOTAGE,
            default_non_offering_labor_charge_per_foot=d.DEFAULT_NON_OFFERING_LABOR_CHARGE_PER_FOOT,
            material_markup_rate=d.MATERIAL_MARKUP_RATE,
        )

    def lumber_price_per_bf(self, species: str, thickness_in: float, width_in: float) -> float:
        key = (species, thickness_in, width_in)
        try:
            return self.lumber_prices[key]
        except KeyError as exc:
            raise KeyError(
                f"No lumber price for species={species!r}, thickness={thickness_in!r}in, "
                f"width={width_in!r}in — add it to shop_pricing_data.LUMBER_PRICES"
            ) from exc
