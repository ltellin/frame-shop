from __future__ import annotations

from decimal import Decimal

from app.domain.design.representations import to_exploded_layout, to_outside_in_list
from app.domain.design.spec import ArtworkSpec, ComponentSpec, DesignSpec


def _design():
    return DesignSpec(
        id=1,
        artwork=ArtworkSpec(title="Sunset", width_in=Decimal("16"), height_in=Decimal("20")),
        components=(
            ComponentSpec(id=1, kind="moulding", sequence=1, params={"face_in": "1.0"}),
            ComponentSpec(id=2, kind="glazing", sequence=2, params={}),
            ComponentSpec(id=3, kind="mat", sequence=3, params={"border_in": "2.0"}),
            ComponentSpec(id=4, kind="mount", sequence=4, params={"method": "hinge"}),
            ComponentSpec(id=5, kind="backing", sequence=5, params={"material": "foamcore"}),
        ),
    )


def test_outside_in_places_artwork_between_front_and_behind():
    entries = to_outside_in_list(_design())
    kinds = [e["kind"] for e in entries]
    assert kinds == ["moulding", "glazing", "mat", "artwork", "mount", "backing"]
    assert [e["position"] for e in entries] == [1, 2, 3, 4, 5, 6]


def test_exploded_layout_has_one_layer_per_component_plus_art():
    layout = to_exploded_layout(_design())
    assert len(layout["layers"]) == 6  # 5 components + artwork
    # z_index is contiguous from 0
    assert sorted(item["z_index"] for item in layout["layers"]) == [0, 1, 2, 3, 4, 5]
    # backing sits at the back, frame at the front
    by_kind = {item["kind"]: item["z_index"] for item in layout["layers"]}
    assert by_kind["backing"] == 0
    assert by_kind["moulding"] == max(by_kind.values())


def test_exploded_bounds_track_outermost_layer():
    layout = to_exploded_layout(_design())
    # 16x20 art + 2" mat (-> 20x24) + 1" moulding (-> 22x26)
    assert layout["bounds"]["width_in"] == 22.0
    assert layout["bounds"]["height_in"] == 26.0
