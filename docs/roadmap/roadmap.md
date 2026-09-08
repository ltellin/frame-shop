# Roadmap

This is a **domain-development sequence**, not a product/feature roadmap. It is
the order in which we intend to *think through and specify* concepts.

**This ordering is provisional** and will be revised as the domain becomes
clearer.

**Claude does not advance from one phase to the next on its own.** The human
decides when a conceptual area is done and when to move on. Finishing the
documentation for a phase does not authorize starting the next one.

Each phase is SPECIFY → (later) IMPLEMENT → (later still) INTEGRATE, and those
stages are not collapsed.

| Phase | Focus |
|---|---|
| **0** | Domain skeleton — this documentation structure. |
| **1** | **Moulding** specification — geometry, types (STANDARD / FLOAT), tooling work. |
| **2** | **Material** (species table) + **Lumber** (stock / pricing) + the **bare-moulding material price-per-foot** model — geometry + material + milling waste + minimum footage. |
| **3** | **Finish** and **Extra** specification. |
| **4** | **Offering** specification — standard configurations, repeatability, stock / pricing implications. |
| **5** | **DesignMoulding** specification — Offering path, customized-Offering path, fully-custom path. |
| **6** | **The rest of moulding pricing** (pseudocode only) — tooling-work labour, finish, extras, joinery, markup, quantity, Offering context, on top of the Phase 2 bare material cost. |
| **7** | **Artwork / framed-object** specification (includes non-artwork products like mirrors). |
| **8** | **Design** specification. |
| **9** | Relationship between a Design and its multiple framing components. |
| **10** | **Pricing engine** specification (general). |
| **11** | Implement: save / reopen a Design. |
| **12** | Accept a Design / historical snapshot. |
| **13** | **Order** and **Work Order**. |
| **14** | Production. |
| **15** | Broader catalog / vendor / lumber / inventory / operations work. |

## Status

- Phase 0: complete — skeleton created.
- Phase 1 (Moulding): geometry fields (STANDARD rabbet depth/height, FLOAT
  internal height + board thickness, shared face width + overall height) and the
  **tooling work** 1–8 Fibonacci scale are **settled** (first pass) — see
  `docs/decisions/0001-moulding-geometry-and-tooling-work.md`. Also added: waste
  factor, milling orientation, optional minimum-footage override. Still open: how
  the STANDARD/FLOAT split is represented in storage. Not implemented.
- Phase 2 (Material / Lumber / bare material cost): **settled** (first pass) —
  8-species Material list, a lumber-price table keyed by species × thickness, and
  the derived bare-moulding price-per-foot chain with a 4 ft shop-default minimum
  footage — see `docs/decisions/0002-material-and-bare-moulding-material-cost.md`.
  Still open: milling-geometry details (thickness mapping, stock steps, kerf,
  waste-factor representation). Not implemented.
- Phases 3–5: first-pass specs drafted for Offering, DesignMoulding; modest notes
  for Finish / Extra / Strainer. Not finalized.
- Phases 6+: not started.
