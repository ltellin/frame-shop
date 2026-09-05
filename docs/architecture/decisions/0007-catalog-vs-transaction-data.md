# ADR 0007 — Catalog reference data is separate from transaction data

- **Status:** accepted
- **Date:** 2026-09-05

## Context

The brief: "Live vendor catalog data and historical transaction data are
different concepts." The software should eventually ingest vendor-exposed data
(product info, SKU, cost, price, availability, discontinued status). Real vendor
APIs are out of scope for the prototype, but the architecture must "leave an
obvious place for them."

## Decision

- `Vendor` and `Product` are **reference data**: the current state of what can be
  bought. They are mutable and are expected to be overwritten by future imports.
- A `DesignComponent` references a `Product` by nullable `product_id`. For a
  live/draft Design the product is **resolved fresh** on every read
  (`catalog_service.resolve` → `ProductResolution`). For accepted work the
  resolved values are frozen into the snapshot (ADR 0004).
- **The ingestion seam is `services/catalog_service`.** Real vendor importers
  will land as `app/catalog/adapters/<vendor>.py` writing `Product` rows through
  this service; nothing downstream changes.
- `Product.attributes` (JSON) holds vendor-specific metadata we don't want as
  columns yet.

## Consequences

- Catalog edits/imports never affect historical records (they read snapshots).
- Draft Designs always reflect current availability, so discontinued/unavailable
  warnings are meaningful (`design_service._warnings`).
- Adding a vendor integration is a new adapter module + a scheduled call, not a
  schema change.
- **You may not** point historical/accepted records at live `Product` rows for
  their prices or descriptions, without revisiting this ADR.

## Alternatives considered

- **One `product` table with effective-dated rows** — turns every catalog read
  into a temporal query; snapshotting at accept time (ADR 0004) is simpler and
  more robust to vendor data errors.
