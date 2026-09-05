"""Load fake vendor + product catalog data for development.

Run:  python -m app.seed.sample_catalog
Idempotent: clears and reloads the catalog tables only.
"""
from __future__ import annotations

from sqlalchemy import delete

from app.db.base import SessionLocal
from app.db.models import Product, Vendor

VENDORS = [
    {"name": "Larson-Juhl", "code": "LJ"},
    {"name": "Roma Moulding", "code": "ROMA"},
    {"name": "Crescent", "code": "CRES"},
    {"name": "Tru Vue", "code": "TV"},
    {"name": "Bainbridge", "code": "BB"},
]

# (vendor, kind, sku, name, description, cost$, price$, uom, available, discontinued)
PRODUCTS = [
    ("Larson-Juhl", "moulding", "LJ-100234", "Biltmore Gold", "Ornate gold leaf, 2\" face",
     4.10, 12.75, "per_linear_ft", True, False),
    ("Larson-Juhl", "moulding", "LJ-556001", "Ferrosa Rust", "Textured metallic, 1.25\" face",
     2.80, 8.90, "per_linear_ft", True, False),
    ("Roma Moulding", "moulding", "ROMA-8821", "Tabacchino Walnut", "Italian walnut, 1.5\" face",
     5.50, 16.00, "per_linear_ft", True, False),
    ("Roma Moulding", "moulding", "ROMA-3300", "Nero Matte Black", "Contemporary black, 0.75\" face",
     2.20, 7.25, "per_linear_ft", False, False),
    ("Larson-Juhl", "moulding", "LJ-090111", "Academie Silver", "Discontinued silver profile",
     3.00, 9.50, "per_linear_ft", False, True),
    ("Crescent", "mat", "CRES-1069", "Antique White", "Conservation-grade, cream core",
     0.00, 0.30, "per_united_in", True, False),
    ("Crescent", "mat", "CRES-9502", "Raven Black", "Black-on-black conservation mat",
     0.00, 0.34, "per_united_in", True, False),
    ("Bainbridge", "mat", "BB-8640", "Alphamat Sandstone", "Warm neutral, alpha-cellulose",
     0.00, 0.28, "per_united_in", True, False),
    ("Crescent", "mat", "CRES-0000", "Newsprint Grey", "Old stock, being phased out",
     0.00, 0.22, "per_united_in", True, True),
    ("Tru Vue", "glazing", "TV-CC", "Conservation Clear", "99% UV, anti-outgassing",
     0.90, 3.60, "per_sqft", True, False),
    ("Tru Vue", "glazing", "TV-MUSEUM", "Museum Glass", "Anti-reflective + 99% UV",
     4.50, 14.00, "per_sqft", True, False),
    ("Tru Vue", "glazing", "TV-REG", "Regular Acrylic", "Standard 2mm acrylic",
     0.60, 2.40, "per_sqft", True, False),
    ("Bainbridge", "fillet", "BB-FIL-22", "Gold Bead Fillet", "Slim gold fillet, 0.375\" face",
     1.20, 4.50, "per_linear_ft", True, False),
]


def run() -> None:
    session = SessionLocal()
    try:
        session.execute(delete(Product))
        session.execute(delete(Vendor))
        session.flush()

        vendors: dict[str, Vendor] = {}
        for spec in VENDORS:
            vendor = Vendor(name=spec["name"], code=spec["code"])
            session.add(vendor)
            vendors[spec["name"]] = vendor
        session.flush()

        for (vname, kind, sku, name, desc, cost, price, uom, avail, disc) in PRODUCTS:
            session.add(
                Product(
                    vendor_id=vendors[vname].id,
                    kind=kind,
                    sku=sku,
                    name=name,
                    description=desc,
                    unit_cost_cents=round(cost * 100),
                    unit_price_cents=round(price * 100),
                    price_uom=uom,
                    available=avail,
                    discontinued=disc,
                )
            )
        session.commit()
        print(f"seeded {len(VENDORS)} vendors, {len(PRODUCTS)} products")
    finally:
        session.close()


if __name__ == "__main__":
    run()
