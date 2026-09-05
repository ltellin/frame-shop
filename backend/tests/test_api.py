from __future__ import annotations


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_component_kinds_expose_param_schemas(client):
    r = client.get("/api/catalog/component-kinds")
    assert r.status_code == 200
    keys = {k["key"] for k in r.json()}
    assert {"moulding", "mat", "glazing", "mount", "backing"} <= keys
    moulding = next(k for k in r.json() if k["key"] == "moulding")
    assert "param_schema" in moulding


def test_design_lifecycle(client, seeded_catalog):
    # quick-create a customer inline and start a design
    start = client.post(
        "/api/designs",
        json={
            "customer": {"name": "Grace"},
            "artwork": {"title": "Blueprint", "width_in": "18", "height_in": "24"},
            "components": [
                {
                    "kind": "moulding",
                    "product_id": seeded_catalog["moulding"],
                    "params": {"face_in": "1.25"},
                },
                {"kind": "glazing", "product_id": seeded_catalog["glazing"], "params": {}},
                {
                    "kind": "mat",
                    "product_id": seeded_catalog["mat"],
                    "params": {"border_in": "2.5"},
                },
                {"kind": "backing", "params": {"material": "foamcore"}},
            ],
        },
    )
    assert start.status_code == 201, start.text
    design = start.json()
    design_id = design["id"]

    assert design["price"]["subtotal_cents"] > 0
    assert len(design["components"]) == 4
    assert design["representations"]["outside_in"][0]["kind"] == "moulding"
    assert len(design["representations"]["exploded"]["layers"]) == 5  # 4 + artwork

    # reorder + widen the mat via PATCH (send full desired list)
    comps = design["components"]
    mat = next(c for c in comps if c["kind"] == "mat")
    mat["params"]["border_in"] = "4"
    patch = client.patch(
        f"/api/designs/{design_id}",
        json={
            "components": [
                {
                    "id": c["id"],
                    "kind": c["kind"],
                    "params": c["params"],
                    "product_id": c["product_id"],
                }
                for c in comps
            ]
        },
    )
    assert patch.status_code == 200, patch.text
    assert patch.json()["price"]["subtotal_cents"] != design["price"]["subtotal_cents"]

    # hold, then confirm it persists on reload
    client.patch(f"/api/designs/{design_id}", json={"status": "held"})
    reload = client.get(f"/api/designs/{design_id}")
    assert reload.json()["status"] == "held"
    assert reload.json()["editable"] is True


def test_discontinued_product_warns(client, seeded_catalog):
    start = client.post(
        "/api/designs",
        json={
            "customer": {"name": "Kay"},
            "artwork": {"title": "X", "width_in": "10", "height_in": "10"},
            "components": [{"kind": "moulding", "product_id": seeded_catalog["discontinued"]}],
        },
    )
    assert start.status_code == 201
    assert any("discontinued" in w for w in start.json()["warnings"])


def test_unknown_kind_returns_422(client):
    r = client.post(
        "/api/designs",
        json={
            "customer": {"name": "Zed"},
            "artwork": {"title": "X", "width_in": "10", "height_in": "10"},
            "components": [{"kind": "sasquatch"}],
        },
    )
    assert r.status_code == 422


def test_customers_and_orders_lists(client, seeded_catalog):
    client.post(
        "/api/designs",
        json={
            "customer": {"name": "Rosa Vance", "phone": "555-0100"},
            "artwork": {"title": "Map", "width_in": "12", "height_in": "16"},
        },
    )

    customers = client.get("/api/customers")
    assert customers.status_code == 200
    rosa = next(c for c in customers.json() if c["name"] == "Rosa Vance")
    assert rosa["phone"] == "555-0100"
    assert rosa["order_count"] == 1

    orders = client.get("/api/orders")
    assert orders.status_code == 200
    assert len(orders.json()) == 1
    order = orders.json()[0]
    assert order["customer_name"] == "Rosa Vance"
    assert order["design_count"] == 1
    assert order["number"] >= 5271

    detail = client.get(f"/api/orders/{order['id']}")
    assert detail.status_code == 200
    assert detail.json()["designs"][0]["artwork_title"] == "Map"
