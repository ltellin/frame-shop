from __future__ import annotations

import io


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_catalog_metadata(client):
    kinds = {k["key"] for k in client.get("/api/catalog/component-kinds").json()}
    assert {"moulding", "mat", "glazing", "mount", "backing"} <= kinds
    types = {t["key"] for t in client.get("/api/catalog/design-types").json()}
    assert {"framing", "mat_only", "glazing_only", "frame_only", "swap", "repair"} <= types


def test_loose_draft_then_complete(client):
    start = client.post("/api/designs", json={"type": "mat_only"})
    assert start.status_code == 201, start.text
    d = start.json()
    assert d["complete"] is False and d["order_id"] is None

    did = d["id"]
    patched = client.patch(
        f"/api/designs/{did}",
        json={"base_width_in": "20 1/2", "base_height_in": "24", "components": [{"kind": "mat"}]},
    )
    assert patched.status_code == 200, patched.text
    body = patched.json()
    assert body["complete"] is True
    assert body["price"]["subtotal_cents"] > 0
    assert body["summary"]["finished_width_in"] >= 20
    assert body["base_ref"] == "sight"

    # loose-draft list
    loose = client.get("/api/designs?loose=true").json()
    assert did in [x["id"] for x in loose]


def test_customer_supplied_component_via_api(client):
    d = client.post(
        "/api/designs",
        json={
            "type": "swap",
            "base_width_in": "18",
            "base_height_in": "24",
            "components": [
                {"kind": "moulding", "provenance": "customer"},
                {"kind": "glazing"},
            ],
        },
    ).json()
    frame = next(c for c in d["components"] if c["kind"] == "moulding")
    assert frame["provenance"] == "customer"
    price_frame = next(line for line in d["price"]["lines"] if line["kind"] == "moulding")
    assert "handling" in price_frame["detail"]


def test_add_to_order_flow(client):
    d = client.post("/api/designs", json={"base_width_in": "11", "base_height_in": "14"}).json()
    r = client.post(
        f"/api/designs/{d['id']}/add-to-order", json={"customer": {"name": "Wes Kaplan"}}
    )
    assert r.status_code == 200, r.text
    order_id = r.json()["order_id"]

    detail = client.get(f"/api/orders/{order_id}").json()
    assert detail["customer_name"] == "Wes Kaplan"
    assert detail["designs"][0]["id"] == d["id"]

    orders = client.get("/api/orders").json()
    assert any(o["id"] == order_id and o["design_count"] == 1 for o in orders)


def test_image_upload_serve_delete(client):
    d = client.post("/api/designs", json={"base_width_in": "8", "base_height_in": "10"}).json()
    did = d["id"]

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00"
        b"\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    up = client.post(
        f"/api/designs/{did}/images",
        files={"file": ("art.png", io.BytesIO(png), "image/png")},
    )
    assert up.status_code == 201, up.text
    img = up.json()
    assert img["is_primary"] is True and img["source"] == "upload"

    assert client.get(f"/api/designs/{did}").json()["images"][0]["id"] == img["id"]

    served = client.get(img["url"])
    assert served.status_code == 200 and served.content == png

    assert client.delete(img["url"]).status_code == 204
    assert client.get(f"/api/designs/{did}").json()["images"] == []


def test_capture_without_camera_returns_501(client):
    d = client.post("/api/designs", json={"base_width_in": "8", "base_height_in": "10"}).json()
    r = client.post(f"/api/designs/{d['id']}/images/capture")
    assert r.status_code == 501
    assert "camera" in r.json()["detail"].lower()


def test_unknown_kind_returns_422(client):
    r = client.post(
        "/api/designs",
        json={"base_width_in": "10", "base_height_in": "10", "components": [{"kind": "sasquatch"}]},
    )
    assert r.status_code == 422
