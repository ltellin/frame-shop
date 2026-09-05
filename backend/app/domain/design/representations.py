"""Derived representations of a Design.

Both are pure functions of the component list. Neither is stored; the UI renders
from these and never from the raw storage shape.

* ``to_outside_in_list`` — the traditional framing-industry description.
* ``to_exploded_layout`` — a renderer-agnostic model for the schematic.

The artwork pseudo-layer is present only when ``design.shows_artwork_layer``
(i.e. ``base_ref == 'art'``); mat-only / glass-only / frame-only jobs have no art.
"""

from __future__ import annotations

from decimal import Decimal

from app.domain.design.geometry import walk_layers
from app.domain.design.kinds import get_kind
from app.domain.design.spec import DesignSpec

# Physical stacking order, back (0) to front. Used to place layers in the
# exploded view and to decide where the artwork sits in the outside-in list.
_ROLE_Z = {
    "backing": 0,
    "substrate": 1,
    "spacer": 2,
    "art": 3,
    "fillet": 5,
    "mat": 6,
    "accent": 7,
    "glazing": 8,
    "frame": 9,
}
_BEHIND_ART_ROLES = {"backing", "substrate", "spacer"}


def _num(value: Decimal | float) -> float:
    return float(value)


def _art_label(design: DesignSpec) -> str:
    if design.artwork and design.artwork.title:
        return design.artwork.title
    return "Artwork"


def _rendered(layers):
    return [layer for layer in layers if get_kind(layer.kind).rendered]


def to_outside_in_list(design: DesignSpec) -> list[dict]:
    layers = _rendered(walk_layers(design))  # outside-in already

    front, behind = [], []
    for layer in layers:
        (behind if layer.layer_role in _BEHIND_ART_ROLES else front).append(layer)

    entries: list[dict] = []
    for layer in front:
        entries.append(
            {
                "component_id": layer.component_id,
                "kind": layer.kind,
                "layer_role": layer.layer_role,
                "provenance": layer.provenance,
                "label": layer.label,
            }
        )
    if design.shows_artwork_layer:
        entries.append(
            {
                "component_id": None,
                "kind": "artwork",
                "layer_role": "art",
                "provenance": "customer",
                "label": _art_label(design),
            }
        )
    for layer in behind:
        entries.append(
            {
                "component_id": layer.component_id,
                "kind": layer.kind,
                "layer_role": layer.layer_role,
                "provenance": layer.provenance,
                "label": layer.label,
            }
        )

    for position, entry in enumerate(entries, start=1):
        entry["position"] = position
    return entries


def to_exploded_layout(design: DesignSpec) -> dict:
    layers = _rendered(walk_layers(design))
    base = design.base_dimensions

    raw: list[dict] = []
    if design.shows_artwork_layer:
        raw.append(
            {
                "component_id": None,
                "kind": "artwork",
                "layer_role": "art",
                "provenance": "customer",
                "label": _art_label(design),
                "width_in": _num(base.width_in),
                "height_in": _num(base.height_in),
                "opening_width_in": None,
                "opening_height_in": None,
                "_z_role": _ROLE_Z["art"],
                "_seq": 999,
            }
        )
    for layer in layers:
        g = layer.geometry
        raw.append(
            {
                "component_id": layer.component_id,
                "kind": layer.kind,
                "layer_role": layer.layer_role,
                "provenance": layer.provenance,
                "label": layer.label,
                "width_in": _num(g.self_size.width_in),
                "height_in": _num(g.self_size.height_in),
                "opening_width_in": _num(g.opening.width_in) if g.opening else None,
                "opening_height_in": _num(g.opening.height_in) if g.opening else None,
                "_z_role": _ROLE_Z.get(layer.layer_role, 7),
                "_seq": layer.sequence,
            }
        )

    # Back to front: lower role-z first; within a role, more-inside (higher
    # sequence) sits further back.
    raw.sort(key=lambda item: (item["_z_role"], -item["_seq"]))

    layers_out = []
    for z_index, item in enumerate(raw):
        item.pop("_z_role")
        item.pop("_seq")
        item["z_index"] = z_index
        layers_out.append(item)

    bounds_w = max((item["width_in"] for item in layers_out), default=_num(base.width_in))
    bounds_h = max((item["height_in"] for item in layers_out), default=_num(base.height_in))

    return {
        "units": "in",
        "layers": layers_out,
        "bounds": {"width_in": bounds_w, "height_in": bounds_h},
    }
