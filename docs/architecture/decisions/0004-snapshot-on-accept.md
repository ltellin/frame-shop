# ADR 0004 — Snapshot on accept; historical records are immutable

- **Status:** accepted (design decision; implemented in slice 2)
- **Date:** 2026-09-05

## Context

The brief: historical sales/production records must not silently change when
vendor catalog or pricing changes ("if a moulding costs more next month, an old
invoice must not change"). Live vendor catalog data and historical transaction
data are different concepts. We may need design snapshots/revisions/versioning.

## Decision

- While a Design is `draft | held | quoted` it is fully mutable and always shows
  **live** catalog data and a freshly computed price.
- **Accepting** a Design runs one atomic service:
  1. resolve every `product_id` against the live catalog (descriptions, costs,
     prices, availability at that instant);
  2. run the pricing engine with a **pinned** `PricingProfile` id + version;
  3. serialize the resolved spec + `PriceBreakdown` + profile id/version into an
     **immutable snapshot** (a JSON document);
  4. create one **Work Order** per accepted Design/Artwork, holding the snapshot
     and referencing the source Design for lineage;
  5. set `Design.status = accepted` (locked).
- Editing an accepted Design → a **new** Design row with `supersedes_id` pointing
  at the old one → must be re-accepted → new Work Order revision.
- Order-level invoice totals = sum of the per-Work-Order snapshots, computed once
  at acceptance. No second computation path.

Schema hooks already in place (slice 1): `Design.status`, `Design.supersedes_id`,
`Design.version`, `Design.updated_at`.

## Consequences

- A snapshot, once written, is **never mutated**. Catalog or pricing edits never
  reach it.
- Drafts always re-resolve live catalog (so discontinued warnings are current);
  accepted work always reads its snapshot. There is no in-between.
- Full revision-history tables are deferred — `supersedes_id` + a per-Work-Order
  snapshot is enough until a real need appears.
- **You may not** make invoices, cut lists, or production views read live catalog
  data for accepted work, without revisiting this ADR.

## Alternatives considered

- **Re-derive everything from live data + effective-dated price tables** — one
  source of truth, but every historical read becomes a temporal query and a
  vendor data-quality bug can corrupt history.
- **Copy costs onto each component row at accept time** — a partial snapshot;
  loses the pricing assumptions and the profile version.
