"""The pricing engine.

Input: a resolved DesignSpec (products already attached) + a PricingProfile.
Output: a PriceBreakdown value object. No I/O, no ORM, no persistence.

The engine walks the same layer model the schematic uses, so geometry stays in
one place.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.domain.design.geometry import walk_layers
from app.domain.design.kinds import get_kind
from app.domain.design.spec import DesignSpec
from app.domain.pricing.profiles import PlaceholderProfile, PricingProfile


@dataclass(frozen=True, slots=True)
class PriceLine:
    component_id: int | None
    kind: str
    label: str
    detail: str
    amount_cents: int


@dataclass(frozen=True, slots=True)
class PriceBreakdown:
    lines: list[PriceLine]
    subtotal_cents: int
    currency: str
    profile_id: str
    profile_version: int
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        data = asdict(self)
        return data


def price_design(
    design: DesignSpec,
    profile: PricingProfile | None = None,
    currency: str = "USD",
) -> PriceBreakdown:
    profile = profile or PlaceholderProfile()
    lines: list[PriceLine] = []
    notes: list[str] = []

    for layer in walk_layers(design):
        component = _find_component(design, layer.component_id)
        product = component.product if component else None
        kind = get_kind(layer.kind)

        if layer.provenance == "customer":
            notes.append(f"{layer.label}: customer-supplied — handling charge only.")
            priced = profile.price_customer_supplied(layer)
            lines.append(
                PriceLine(
                    component_id=layer.component_id,
                    kind=layer.kind,
                    label=layer.label,
                    detail=priced.detail,
                    amount_cents=priced.amount_cents,
                )
            )
            continue

        if kind.consumes_product and product is None:
            notes.append(f"{layer.label}: no catalog product selected — used a placeholder rate.")
        if product and product.discontinued:
            notes.append(f"{layer.label}: product '{product.name}' is discontinued.")
        elif product and not product.available:
            notes.append(f"{layer.label}: product '{product.name}' is currently unavailable.")

        priced = profile.price_layer(layer, product)
        lines.append(
            PriceLine(
                component_id=layer.component_id,
                kind=layer.kind,
                label=layer.label,
                detail=priced.detail,
                amount_cents=priced.amount_cents,
            )
        )

    for extra in profile.design_level_lines(design):
        lines.append(
            PriceLine(
                component_id=None,
                kind="fee",
                label=extra.label,
                detail=extra.detail,
                amount_cents=extra.amount_cents,
            )
        )

    subtotal = sum(line.amount_cents for line in lines)
    return PriceBreakdown(
        lines=lines,
        subtotal_cents=subtotal,
        currency=currency,
        profile_id=profile.id,
        profile_version=profile.version,
        notes=notes,
    )


def _find_component(design: DesignSpec, component_id: int | None):
    if component_id is None:
        return None
    for comp in design.components:
        if comp.id == component_id:
            return comp
    return None
