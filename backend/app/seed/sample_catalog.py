"""Load the catalog from ``catalog.json``.

Run:  python -m app.seed.sample_catalog

Upserts vendors by name and products by (vendor, sku), so re-running updates
rows in place. Each product's ``spec`` is validated against its kind's schema
(domain/catalog/product_kinds.py); a bad row aborts the load with a clear
message. This same shape is the seam a CSV / vendor-feed importer would target.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models import Product, Vendor
from app.domain.catalog.product_kinds import parse_spec

CATALOG_FILE = Path(__file__).with_name("catalog.json")


def _dollars_to_cents(value) -> int:
    return round(float(value or 0) * 100)


def _validate(row: dict) -> dict:
    kind = row["kind"]
    try:
        spec = parse_spec(kind, row.get("spec"))
    except ValidationError as exc:
        raise SystemExit(
            f"bad spec for {row.get('vendor')} {row.get('sku')} ({kind}):\n{exc}"
        ) from None
    if kind in ("moulding", "fillet") and not spec.get("face_width_in"):
        raise SystemExit(f"{row.get('vendor')} {row.get('sku')}: a {kind} needs spec.face_width_in")
    return spec


def load(path: Path = CATALOG_FILE) -> tuple[int, int]:
    data = json.loads(path.read_text())
    session = SessionLocal()
    try:
        vendors: dict[str, Vendor] = {}
        for spec in data["vendors"]:
            v = session.scalar(select(Vendor).where(Vendor.name == spec["name"]))
            if v is None:
                v = Vendor(name=spec["name"])
                session.add(v)
            v.code = spec.get("code")
            v.is_house = bool(spec.get("is_house", False))
            vendors[v.name] = v
        session.flush()

        for row in data["products"]:
            spec = _validate(row)
            vendor = vendors[row["vendor"]]
            product = session.scalar(
                select(Product).where(Product.vendor_id == vendor.id, Product.sku == row["sku"])
            )
            if product is None:
                product = Product(vendor_id=vendor.id, sku=row["sku"])
                session.add(product)
            product.kind = row["kind"]
            product.name = row["name"]
            product.description = row.get("description", "")
            product.unit_cost_cents = _dollars_to_cents(row.get("cost"))
            product.unit_price_cents = _dollars_to_cents(row.get("price"))
            product.price_uom = row.get("uom", "each")
            product.available = bool(row.get("available", True))
            product.discontinued = bool(row.get("discontinued", False))
            product.spec = spec

        session.commit()
        return len(data["vendors"]), len(data["products"])
    finally:
        session.close()


def run() -> None:
    vendors, products = load()
    print(
        f"loaded {vendors} vendors, {products} products from {CATALOG_FILE.name}", file=sys.stderr
    )


if __name__ == "__main__":
    run()
