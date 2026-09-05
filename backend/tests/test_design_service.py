from __future__ import annotations

import pytest

from app.services import design_service, order_service
from app.services.errors import DomainValidationError


@pytest.fixture()
def draft(session):
    d = design_service.start_design(
        session,
        {"type": "framing", "base_width_in": "16", "base_height_in": "20"},
    )
    session.commit()
    return d


def test_loose_draft_needs_nothing(session):
    d = design_service.start_design(session, {})
    session.commit()
    assert d.status == "draft"
    assert d.order_id is None
    assert d.customer_id is None
    assert d.type == "framing"


def test_dimensions_gate_completeness(session):
    d = design_service.start_design(session, {"type": "mat_only"})
    session.commit()
    rm = design_service.to_read_model(session, d)
    assert rm["complete"] is False
    assert rm["price"] is None and rm["representations"] is None

    design_service.update_design(session, d, {"base_width_in": "20", "base_height_in": "24"})
    session.commit()
    rm = design_service.to_read_model(session, d)
    assert rm["complete"] is True
    assert rm["price"]["subtotal_cents"] > 0
    assert rm["summary"]["finished_width_in"] >= 20


def test_type_seeds_and_reseeds_starter_stack(session):
    d = design_service.start_design(
        session,
        {"type": "framing", "base_width_in": "16", "base_height_in": "20", "seed_starter": True},
    )
    session.commit()
    assert [c.kind for c in d.components] == ["moulding", "glazing", "mat", "mount", "backing"]

    # switching type on an untouched (freshly seeded... not empty) design does NOT reseed
    design_service.update_design(session, d, {"components": []})
    design_service.update_design(session, d, {"type": "mat_only"})
    session.commit()
    assert [c.kind for c in d.components] == ["mat", "service"]


def test_base_ref_follows_type(session, draft):
    design_service.update_design(session, draft, {"type": "glazing_only"})
    session.commit()
    assert draft.base_ref == "glass"


def test_provenance_round_trips(session, draft):
    design_service.replace_components(
        session, draft, [{"kind": "moulding", "provenance": "customer"}]
    )
    session.commit()
    assert draft.components[0].provenance == "customer"
    rm = design_service.to_read_model(session, draft)
    assert rm["components"][0]["provenance"] == "customer"


def test_add_to_order_creates_customer_and_order(session, draft):
    order = design_service.add_to_order(session, draft, customer={"name": "Nadia Rivers"})
    session.commit()
    assert draft.order_id == order.id
    assert draft.customer_id == order.customer_id
    assert order.customer.name == "Nadia Rivers"
    assert order.number >= 5271


def test_add_to_order_twice_is_rejected(session, draft):
    design_service.add_to_order(session, draft, customer={"name": "X"})
    session.commit()
    with pytest.raises(DomainValidationError):
        design_service.add_to_order(session, draft, customer={"name": "Y"})


def test_second_design_reuses_open_order(session):
    c = order_service.create_customer(session, name="Repeat")
    d1 = design_service.start_design(
        session, {"base_width_in": "10", "base_height_in": "10", "customer_id": c.id}
    )
    o1 = design_service.add_to_order(session, d1, customer_id=c.id)
    d2 = design_service.start_design(session, {"base_width_in": "12", "base_height_in": "12"})
    o2 = design_service.add_to_order(session, d2, customer_id=c.id)
    session.commit()
    assert o1.id == o2.id


def test_accepted_design_is_locked(session, draft):
    design_service.update_design(session, draft, {"status": "accepted"})
    with pytest.raises(DomainValidationError):
        design_service.update_design(session, draft, {"name": "new name"})


def test_invalid_kind_rejected(session, draft):
    with pytest.raises(DomainValidationError):
        design_service.replace_components(session, draft, [{"kind": "unicorn"}])
