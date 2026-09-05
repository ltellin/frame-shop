from __future__ import annotations

import pytest

from app.services import design_service, order_service
from app.services.errors import DomainValidationError


@pytest.fixture()
def design(session):
    customer = order_service.create_customer(session, name="Ada")
    d = design_service.start_design(
        session,
        {
            "customer_id": customer.id,
            "artwork": {"title": "Ada's Print", "width_in": "16", "height_in": "20"},
        },
    )
    session.commit()
    return d


def test_start_design_creates_order_and_artwork(session, design):
    assert design.order_id is not None
    assert design.artwork.title == "Ada's Print"
    assert design.status == "draft"
    assert design.price_breakdown is not None


def test_replace_components_assigns_contiguous_sequence(session, design):
    design_service.replace_components(
        session,
        design,
        [
            {"kind": "moulding", "params": {"face_in": "1.0"}},
            {"kind": "glazing", "params": {}},
            {"kind": "mat", "params": {"border_in": "2"}},
        ],
    )
    seqs = [c.sequence for c in sorted(design.components, key=lambda c: c.sequence)]
    assert seqs == [1, 2, 3]


def test_replace_components_reorder_and_edit(session, design):
    design_service.replace_components(
        session,
        design,
        [{"kind": "moulding", "params": {}}, {"kind": "mat", "params": {"border_in": "2"}}],
    )
    ids = {c.kind: c.id for c in design.components}
    # swap order, keep ids, widen the mat
    design_service.replace_components(
        session,
        design,
        [
            {"id": ids["mat"], "kind": "mat", "params": {"border_in": "3"}},
            {"id": ids["moulding"], "kind": "moulding", "params": {}},
        ],
    )
    by_seq = {c.sequence: c for c in design.components}
    assert by_seq[1].kind == "mat"
    assert by_seq[1].params["border_in"] == "3"
    assert by_seq[1].id == ids["mat"]  # updated in place, not recreated


def test_replace_components_deletes_omitted(session, design):
    design_service.replace_components(
        session, design, [{"kind": "moulding"}, {"kind": "mat", "params": {"border_in": "2"}}]
    )
    assert len(design.components) == 2
    design_service.replace_components(session, design, [{"kind": "moulding"}])
    assert len(design.components) == 1


def test_invalid_kind_rejected(session, design):
    with pytest.raises(DomainValidationError):
        design_service.replace_components(session, design, [{"kind": "unicorn"}])


def test_invalid_params_rejected(session, design):
    with pytest.raises(DomainValidationError):
        design_service.replace_components(
            session, design, [{"kind": "mat", "params": {"border_in": -3}}]
        )


def test_parent_index_links_component(session, design):
    design_service.replace_components(
        session,
        design,
        [
            {"kind": "moulding", "params": {}},
            {"kind": "moulding", "params": {"stack_level": 1}, "parent_index": 0},
        ],
    )
    child = [c for c in design.components if c.sequence == 2][0]
    parent = [c for c in design.components if c.sequence == 1][0]
    assert child.parent_component_id == parent.id


def test_parent_index_self_reference_rejected(session, design):
    with pytest.raises(DomainValidationError):
        design_service.replace_components(
            session, design, [{"kind": "moulding", "parent_index": 0}]
        )


def test_accepted_design_is_locked(session, design):
    design_service.update_design(session, design, {"status": "accepted"})
    with pytest.raises(DomainValidationError):
        design_service.update_design(session, design, {"name": "new name"})


def test_price_updates_when_component_changes(session, design):
    design_service.update_design(
        session, design, {"components": [{"kind": "mat", "params": {"border_in": "2"}}]}
    )
    first = design.price_breakdown["subtotal_cents"]
    design_service.update_design(
        session, design, {"components": [{"kind": "mat", "params": {"border_in": "5"}}]}
    )
    assert design.price_breakdown["subtotal_cents"] > first
