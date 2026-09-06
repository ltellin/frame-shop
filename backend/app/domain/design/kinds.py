"""Component-kind registry.

Each framing component kind is a small class that knows:

* its typed parameter model (validated on every write),
* its default *layer role* for the schematic,
* how it contributes to geometry (the running package size),
* how to label itself in the traditional outside-to-inside description.

Adding a new component type = adding one class and one ``register()`` call. The
Design schema does not change.

The geometry math here is deliberately simple placeholder logic. It is good
enough to drive a schematic and a demo price; it is not a faithful model of
shop cutting allowances. Replacing it must not require touching the Design model.
"""

from __future__ import annotations

from decimal import Decimal
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.design.layers import LayerGeometry
from app.domain.design.spec import ProductResolution
from app.domain.measure import Dimensions

# --- Layer roles: the vocabulary the schematic uses to place/style a layer -----

LAYER_ROLES = (
    "frame",
    "glazing",
    "fillet",
    "mat",
    "art",
    "spacer",
    "substrate",
    "backing",
    "accent",
)


# --- Parameter models --------------------------------------------------------


class MouldingParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    face_in: Decimal = Field(default=Decimal("1.0"), gt=0, description="Visible face width")
    stack_level: int = Field(default=0, ge=0, description="0 = primary frame, >0 stacked outward")


class MatParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    border_in: Decimal = Field(default=Decimal("2.0"), gt=0, description="Uniform border/reveal")
    bottom_weight_in: Decimal | None = Field(default=None, gt=0, description="Weighted bottom")
    color_label: str | None = None


class FilletParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    face_in: Decimal = Field(default=Decimal("0.375"), gt=0)


class GlazingParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    grade_label: str | None = Field(
        default=None, description="e.g. regular / conservation / museum"
    )


class MountParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method: Literal["pressure_mount", "hinge", "photo_corners", "dry_mount", "float"] = "hinge"


class BackingParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    material: Literal["foamcore", "acid_free_foam", "coroplast", "matboard"] = "foamcore"


class SpacerParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    depth_in: Decimal = Field(default=Decimal("0.125"), gt=0)


class FabricParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str | None = None


class ServiceParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str
    quantity: int = Field(default=1, ge=1)


class GenericParams(BaseModel):
    model_config = ConfigDict(extra="allow")


# --- Kind classes ----------------------------------------------------------


class ComponentKind:
    key: ClassVar[str]
    label: ClassVar[str]
    param_model: ClassVar[type[BaseModel]]
    default_layer_role: ClassVar[str]
    consumes_product: ClassVar[bool] = True
    # Whether this component shows up as a layer in the schematic. Services /
    # fees are real line items but not physical layers.
    rendered: ClassVar[bool] = True

    def parse_params(self, raw: dict | None) -> BaseModel:
        return self.param_model.model_validate(raw or {})

    def effective_params(self, params: BaseModel, product: ProductResolution | None) -> BaseModel:
        """Let a selected product override manually-typed params before geometry
        runs. Default: no change. Overridden by moulding/fillet to take the face
        width from the product's real profile."""
        return params

    def geometry(self, params: BaseModel, inner: Dimensions) -> LayerGeometry:
        """Default: a same-size layer that consumes no material."""
        return LayerGeometry(
            inner=inner,
            outer=inner,
            self_size=inner,
            opening=None,
            linear_in=Decimal(0),
            area_sqin=inner.area_sqin,
        )

    def outside_in_label(self, params: BaseModel, product_name: str | None) -> str:
        return product_name or self.label


def _face_from_profile(params: BaseModel, product: ProductResolution | None) -> BaseModel:
    """Take ``face_in`` from a selected product's real profile, if it has one."""
    if product is not None:
        width = product.spec.get("face_width_in")
        if width is not None:
            return params.model_copy(update={"face_in": Decimal(str(width))})
    return params


class MouldingKind(ComponentKind):
    key = "moulding"
    label = "Moulding"
    param_model = MouldingParams
    default_layer_role = "frame"

    def effective_params(self, params: MouldingParams, product: ProductResolution | None):
        return _face_from_profile(params, product)

    def geometry(self, params: MouldingParams, inner: Dimensions) -> LayerGeometry:
        outer = inner.grown_by(params.face_in)
        # Perimeter of the outer edge plus a flat cutting allowance.
        linear_in = outer.perimeter_in + 8 * params.face_in + Decimal(4)
        return LayerGeometry(
            inner=inner,
            outer=outer,
            self_size=outer,
            opening=inner,
            linear_in=linear_in,
            area_sqin=Decimal(0),
        )

    def outside_in_label(self, params: MouldingParams, product_name: str | None) -> str:
        base = product_name or "Moulding"
        return f"{base} (stacked)" if params.stack_level else base


class MatKind(ComponentKind):
    key = "mat"
    label = "Mat"
    param_model = MatParams

    default_layer_role = "mat"

    def geometry(self, params: MatParams, inner: Dimensions) -> LayerGeometry:
        extra_bottom = Decimal(0)
        if params.bottom_weight_in and params.bottom_weight_in > params.border_in:
            extra_bottom = params.bottom_weight_in - params.border_in
        outer = Dimensions(
            inner.width_in + 2 * params.border_in,
            inner.height_in + 2 * params.border_in + extra_bottom,
        )
        # The mat window overlaps the art slightly.
        opening = inner.grown_by(Decimal("-0.25"))
        return LayerGeometry(
            inner=inner,
            outer=outer,
            self_size=outer,
            opening=opening,
            linear_in=Decimal(0),
            area_sqin=outer.area_sqin,
        )

    def outside_in_label(self, params: MatParams, product_name: str | None) -> str:
        base = product_name or params.color_label or "Mat"
        return f'{base} — {params.border_in}" border'


class FilletKind(ComponentKind):
    key = "fillet"
    label = "Fillet"
    param_model = FilletParams
    default_layer_role = "fillet"

    def effective_params(self, params: FilletParams, product: ProductResolution | None):
        return _face_from_profile(params, product)

    def geometry(self, params: FilletParams, inner: Dimensions) -> LayerGeometry:
        outer = inner.grown_by(params.face_in)
        return LayerGeometry(
            inner=inner,
            outer=outer,
            self_size=outer,
            opening=inner,
            linear_in=outer.perimeter_in + Decimal(4),
            area_sqin=Decimal(0),
        )


class GlazingKind(ComponentKind):
    key = "glazing"
    label = "Glazing"
    param_model = GlazingParams
    default_layer_role = "glazing"

    def geometry(self, params: GlazingParams, inner: Dimensions) -> LayerGeometry:
        # Glass is cut to the frame opening; treat as the running size.
        return LayerGeometry(
            inner=inner,
            outer=inner,
            self_size=inner,
            opening=None,
            linear_in=Decimal(0),
            area_sqin=inner.area_sqin,
        )


class MountKind(ComponentKind):
    key = "mount"
    label = "Mounting"
    param_model = MountParams
    default_layer_role = "substrate"
    consumes_product = False

    def geometry(self, params: MountParams, inner: Dimensions) -> LayerGeometry:
        return LayerGeometry(
            inner=inner,
            outer=inner,
            self_size=inner,
            opening=None,
            linear_in=Decimal(0),
            area_sqin=inner.area_sqin,
        )

    def outside_in_label(self, params: MountParams, product_name: str | None) -> str:
        return f"Mount — {params.method.replace('_', ' ')}"


class BackingKind(ComponentKind):
    key = "backing"
    label = "Backing"
    param_model = BackingParams
    default_layer_role = "backing"
    consumes_product = False

    def outside_in_label(self, params: BackingParams, product_name: str | None) -> str:
        return f"Backing — {params.material.replace('_', ' ')}"


class SpacerKind(ComponentKind):
    key = "spacer"
    label = "Spacer"
    param_model = SpacerParams
    default_layer_role = "spacer"
    consumes_product = False

    def geometry(self, params: SpacerParams, inner: Dimensions) -> LayerGeometry:
        return LayerGeometry(
            inner=inner,
            outer=inner,
            self_size=inner,
            opening=None,
            linear_in=inner.perimeter_in,
            area_sqin=Decimal(0),
        )


class FabricKind(ComponentKind):
    key = "fabric"
    label = "Fabric"
    param_model = FabricParams
    default_layer_role = "accent"


class ServiceKind(ComponentKind):
    key = "service"
    label = "Service"
    param_model = ServiceParams
    default_layer_role = "accent"
    consumes_product = False
    rendered = False

    def geometry(self, params: ServiceParams, inner: Dimensions) -> LayerGeometry:
        return LayerGeometry(
            inner=inner,
            outer=inner,
            self_size=inner,
            opening=None,
            linear_in=Decimal(0),
            area_sqin=Decimal(0),
        )

    def outside_in_label(self, params: ServiceParams, product_name: str | None) -> str:
        return params.description


class OtherKind(ComponentKind):
    key = "other"
    label = "Other component"
    param_model = GenericParams
    default_layer_role = "accent"
    consumes_product = False


_REGISTRY: dict[str, ComponentKind] = {}


def register(kind: ComponentKind) -> None:
    _REGISTRY[kind.key] = kind


for _cls in (
    MouldingKind,
    MatKind,
    FilletKind,
    GlazingKind,
    MountKind,
    BackingKind,
    SpacerKind,
    FabricKind,
    ServiceKind,
    OtherKind,
):
    register(_cls())


def get_kind(key: str) -> ComponentKind:
    try:
        return _REGISTRY[key]
    except KeyError:
        raise ValueError(f"unknown component kind: {key!r}") from None


def kind_keys() -> list[str]:
    return list(_REGISTRY)


def kind_catalog() -> list[dict]:
    """Metadata for the frontend's 'add component' picker."""
    return [
        {
            "key": k.key,
            "label": k.label,
            "default_layer_role": k.default_layer_role,
            "consumes_product": k.consumes_product,
            "param_schema": k.param_model.model_json_schema(),
        }
        for k in _REGISTRY.values()
    ]


# --- Design types + starter stacks ----------------------------------------
#
# `type` is a light tag: it picks which base dimension is asked for, whether the
# artwork block is shown, and a starter component stack. It does NOT restrict
# which components a design may contain. Production task templates key off it
# later.

DESIGN_TYPES: dict[str, dict] = {
    "framing": {"label": "Framing", "base_ref": "art", "has_art": True},
    "mat_only": {"label": "Mat only", "base_ref": "sight", "has_art": False},
    "glazing_only": {"label": "Glass only", "base_ref": "glass", "has_art": False},
    "frame_only": {"label": "Frame only", "base_ref": "rabbet", "has_art": False},
    "canvas_stretch": {"label": "Canvas stretch", "base_ref": "art", "has_art": True},
    "object_box": {"label": "Shadowbox", "base_ref": "art", "has_art": True},
    "swap": {"label": "Art swap / reframe", "base_ref": "art", "has_art": True},
    "repair": {"label": "Repair", "base_ref": "sight", "has_art": False},
    "other": {"label": "Other", "base_ref": "sight", "has_art": False},
}

_S = "service"

STARTER_STACKS: dict[str, list[dict]] = {
    "framing": [
        {"kind": "moulding"},
        {"kind": "glazing"},
        {"kind": "mat", "params": {"border_in": 2.5}},
        {"kind": "mount", "params": {"method": "hinge"}},
        {"kind": "backing", "params": {"material": "foamcore"}},
    ],
    "mat_only": [
        {"kind": "mat", "params": {"border_in": 2.5}},
        {"kind": _S, "params": {"description": "Cut mat"}},
    ],
    "glazing_only": [
        {"kind": "glazing"},
        {"kind": _S, "params": {"description": "Cut glazing to size"}},
    ],
    "frame_only": [
        {"kind": "moulding"},
        {"kind": _S, "params": {"description": "Join frame"}},
    ],
    "canvas_stretch": [
        {"kind": _S, "params": {"description": "Build stretcher bars"}},
        {"kind": _S, "params": {"description": "Stretch canvas"}},
    ],
    "object_box": [
        {"kind": "moulding"},
        {"kind": "glazing"},
        {"kind": "spacer", "params": {"depth_in": 1.0}},
        {"kind": "backing", "params": {"material": "foamcore"}},
        {"kind": _S, "params": {"description": "Mount objects"}},
    ],
    "swap": [
        {"kind": "moulding", "provenance": "customer"},
        {"kind": _S, "params": {"description": "Fit to customer frame"}},
    ],
    "repair": [
        {"kind": "moulding", "provenance": "customer"},
        {"kind": "glazing"},
        {"kind": _S, "params": {"description": "Remove & replace glazing, refit"}},
    ],
    "other": [],
}


def design_type_catalog() -> list[dict]:
    return [
        {"key": key, **meta, "starter_stack": STARTER_STACKS.get(key, [])}
        for key, meta in DESIGN_TYPES.items()
    ]


def starter_stack(design_type: str) -> list[dict]:
    return [dict(item) for item in STARTER_STACKS.get(design_type, [])]
