"""Pricing profiles.

A profile is a versioned bundle of rules that turns a resolved layer into a
priced line. Profiles are the *only* place framing rates live. The Design model
knows nothing about them.

``PlaceholderProfile`` uses deliberately crude, clearly-fake numbers. Replacing
it with real rules (rate tables, size breaks, vendor-specific markups, ...) must
not require any change to the Design schema or the component registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.domain.design.layers import LayerView
from app.domain.design.spec import DesignSpec, ProductResolution
from app.domain.money import to_cents


@dataclass(frozen=True, slots=True)
class LayerPrice:
    amount_cents: int
    detail: str


@dataclass(frozen=True, slots=True)
class ExtraLine:
    label: str
    amount_cents: int
    detail: str


class PricingProfile(Protocol):
    id: str
    version: int

    def price_layer(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice: ...

    def design_level_lines(self, design: DesignSpec) -> list[ExtraLine]: ...


# --- Placeholder implementation -------------------------------------------

_D = Decimal


class PlaceholderProfile:
    """Obvious fake pricing. Do not ship to a real shop."""

    id = "placeholder"
    version = 1

    # Fallback rates when a component has no catalog product.
    MOULDING_PER_FT = _D("8.50")
    MAT_PER_UNITED_IN = _D("0.35")
    MAT_CUT_FEE = _D("12.00")
    FILLET_PER_FT = _D("4.00")
    GLAZING_PER_SQFT = _D("3.50")
    SPACER_PER_FT = _D("2.00")
    FABRIC_FLAT = _D("30.00")
    MOUNT_FLAT = {
        "hinge": _D("15.00"),
        "pressure_mount": _D("25.00"),
        "photo_corners": _D("10.00"),
        "dry_mount": _D("35.00"),
        "float": _D("45.00"),
    }
    BACKING_FLAT = {
        "foamcore": _D("8.00"),
        "acid_free_foam": _D("16.00"),
        "coroplast": _D("12.00"),
        "matboard": _D("10.00"),
    }
    SERVICE_EACH = _D("25.00")
    FITTING_FEE = _D("28.00")

    def price_layer(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        method = getattr(self, f"_price_{layer.kind}", None)
        if method is None:
            return LayerPrice(0, "no charge")
        return method(layer, product)

    def design_level_lines(self, design: DesignSpec) -> list[ExtraLine]:
        return [
            ExtraLine(
                label="Fitting & assembly",
                amount_cents=to_cents(self.FITTING_FEE),
                detail="flat shop fee (placeholder)",
            )
        ]

    # -- per-kind rules --

    def _price_moulding(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        feet = layer.geometry.linear_in / 12
        if product and product.price_uom == "per_linear_ft":
            rate = _cents_dec(product.unit_price_cents)
            src = product.name
        else:
            rate = self.MOULDING_PER_FT
            src = "placeholder rate"
        return LayerPrice(
            to_cents(feet * rate),
            f"{feet:.2f} lin ft @ ${rate:.2f}/ft ({src})",
        )

    def _price_mat(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        united = layer.geometry.self_size.united_in
        if product and product.price_uom == "per_united_in":
            rate = _cents_dec(product.unit_price_cents)
            src = product.name
        else:
            rate = self.MAT_PER_UNITED_IN
            src = "placeholder rate"
        amount = united * rate + self.MAT_CUT_FEE
        return LayerPrice(
            to_cents(amount),
            f"{united:.1f} united in @ ${rate:.2f} + ${self.MAT_CUT_FEE:.0f} cut ({src})",
        )

    def _price_fillet(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        feet = layer.geometry.linear_in / 12
        rate = (
            _cents_dec(product.unit_price_cents)
            if product and product.price_uom == "per_linear_ft"
            else self.FILLET_PER_FT
        )
        return LayerPrice(to_cents(feet * rate), f"{feet:.2f} lin ft @ ${rate:.2f}/ft")

    def _price_glazing(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        sqft = layer.geometry.area_sqin / 144
        if product and product.price_uom == "per_sqft":
            rate = _cents_dec(product.unit_price_cents)
            src = product.name
        else:
            rate = self.GLAZING_PER_SQFT
            src = "placeholder rate"
        return LayerPrice(to_cents(sqft * rate), f"{sqft:.2f} sq ft @ ${rate:.2f}/sq ft ({src})")

    def _price_mount(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        method = layer.params.get("method", "hinge")
        amount = self.MOUNT_FLAT.get(method, _D("15.00"))
        return LayerPrice(to_cents(amount), f"{method.replace('_', ' ')} (flat)")

    def _price_backing(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        material = layer.params.get("material", "foamcore")
        amount = self.BACKING_FLAT.get(material, _D("8.00"))
        return LayerPrice(to_cents(amount), f"{material.replace('_', ' ')} (flat)")

    def _price_spacer(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        feet = layer.geometry.linear_in / 12
        return LayerPrice(
            to_cents(feet * self.SPACER_PER_FT), f"{feet:.2f} lin ft @ ${self.SPACER_PER_FT:.2f}/ft"
        )

    def _price_fabric(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        if product:
            return LayerPrice(product.unit_price_cents, f"{product.name} (each)")
        return LayerPrice(to_cents(self.FABRIC_FLAT), "placeholder flat")

    def _price_service(self, layer: LayerView, product: ProductResolution | None) -> LayerPrice:
        qty = int(layer.params.get("quantity", 1) or 1)
        return LayerPrice(to_cents(self.SERVICE_EACH * qty), f"{qty} @ ${self.SERVICE_EACH:.2f}")


def _cents_dec(cents: int) -> Decimal:
    return Decimal(cents) / 100
