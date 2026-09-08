# Domain Overview

This is the entry point for the domain model of the frame-shop system. Read this
first. Then read the specific domain file for whatever concept you are about to
work on, and check [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md).

The system is a browser-based ERP / order-management / production system for a
custom picture-framing shop. Established framing software (e.g. LifeSaver) is a
useful parity reference for *what* a shop needs; the goal here is a substantially
better workflow and UX.

We are building the domain **one concept at a time**. Most of the concepts below
are named but not yet specified. A name here does **not** imply a database table,
an API route, or a frontend component.

---

## Relationship map

An **illustrative sketch**, not a schema and not a pipeline.

### The framing-configuration layer

The shop can fabricate a huge **capability space** of frame configurations. The
pieces that combine into one configuration:

```
      Moulding  ----\        (geometry / fabrication profile)
      Material  -----\       (wood species, etc.)
      Finish  --------> DesignMoulding
      Extra(s)  -----/       (carving, inlay, …)
                        ^
                        |  optional source
                        |
                     Offering            (a curated, repeatable shop-standard
                                          combination of the four above)
```

- A **DesignMoulding** is the actual moulding configuration selected for one
  Design. It references a Moulding + Material + Finish + zero-or-more Extras, and
  *optionally* records the Offering it started from.
- An **Offering** bundles the same four things as a deliberate standard product.
  It is optional — a DesignMoulding can be fully custom with **no Offering**.

### The Design layer

```
      Design
        |
        +-- DesignMoulding(s)
        +-- (future) DesignGlazing
        +-- (future) DesignMounting
        +-- (future) other components

      Design  -- optionally -->  Customer
      Design  -- optionally -->  Artwork  (or another framed object — e.g. a mirror)
```

### Later commercial / production boundaries

```
      Design --(accepted)--> Order --> Work Order --> Production
```

### Elsewhere

```
      Vendor  --------  Product catalog        (bought-in goods; glazing, board,
                                                possibly manufacturer moulding)

      Strainer                                 (structural support behind a frame —
                                                a separate, unresolved concept)
```

### What this diagram does *not* mean

- **Not a database schema.** Boxes are not tables; lines are not foreign keys.
- Arrows do **not** indicate ownership.
- Arrows do **not** indicate a required creation order.
- A Design may exist with **no Customer**.
- A Design may exist with **no Artwork** (mirrors and other framed products have
  none).
- A DesignMoulding may exist with **no Offering**.
- Offerings are **optional** standard starting configurations, not prerequisites
  for custom fabrication.
- Exact cardinalities are **not yet decided** for any of these relationships.

### The one principle to carry everywhere

**Model business boundaries, not screen sequence.**

The domain model should not care which screen the user started on (artwork
intake, customer lookup, a blank Design, a reopened draft, something else). It
should care about *what information becomes required when something crosses a
meaningful business boundary* — being quoted, being accepted, being ordered,
being produced.

Do not infer workflow order from a relationship. `Design → Customer` existing as
a relationship does **not** mean a Customer must exist before a Design.

---

## Glossary

Working definitions. Each gets its own domain file for a real specification. A
term appearing here is not a commitment to a table.

| Term | Working definition |
|---|---|
| **Customer** | A person or business the shop does work for. May be retail or trade. |
| **Artwork** / **Piece** | The physical thing being framed, or its stand-in. Some Designs have none (empty frame, mirror, loose mats, material sale). |
| **Design** | The editable framing specification being explored or developed. Independently meaningful: can exist anonymous, unattached, and be discarded without ever becoming an Order. |
| **DesignMoulding** | The actual moulding configuration selected for one Design — a Moulding + Material + Finish + Extras + joinery method, optionally sourced from an Offering, plus design-specific dimensions (including the float gap for float frames) and a live price result. |
| **Moulding** | A **geometry / fabrication specification** for a frame profile: type (STANDARD / FLOAT), face width, overall height, the STANDARD rabbet (depth + height) or the FLOAT internal height + board thickness, and **tooling work** (a 1–8 Fibonacci estimate of milling effort). **Not** species, finish, embellishment, joinery, stock, price, or a finished configuration. |
| **Material** | What a moulding is made from — a small controlled list of wood species (maple, poplar, white oak, red oak, walnut, sapele, ash, cherry). Belongs to DesignMoulding, not Moulding. |
| **Lumber** | The rough stock the shop buys to mill its own mouldings — a species at a nominal thickness — and its current price. Reference data, periodically updated, kept separate from transaction history. |
| **Finish** | How the chosen material is surface-treated (natural, oil, stain, paint, lacquer, ebonized, …). Belongs to the configuration layer, not to Moulding. |
| **Extra** | An optional embellishment or fabrication addition (carving, inlay, …). Zero or more per DesignMoulding. Does **not** by itself make a frame "custom" — an Offering may include Extras. |
| **Offering** | A deliberately curated, repeatable shop-standard configuration: Moulding + Material + Finish + Extras. Commercially and operationally meaningful (batching, stock, standard pricing, marketing). **Not** merely a UI preset. |
| **Product** | A catalog entry for a bought-in good from a vendor (glazing, mat board, possibly manufacturer moulding). Commercial/vendor data. |
| **Vendor** | A source of bought-in products, and eventually lumber suppliers. |
| **Strainer** | An internal support frame fitted behind a visible frame when the moulding alone can't structurally carry the piece. A **separate, unresolved** concept — **not** a Moulding. |
| **Order** | The customer-facing commercial transaction. Occurs at a commercial boundary after one or more Designs are accepted. |
| **Work Order** | One physical finished piece the shop has committed to producing, derived from an accepted Design. |
| **Production Operation** | A step of shop work performed against a Work Order. Framing vocabulary, not a generic workflow engine. |

---

## Capability space vs Offerings

The shop is capable of making far more frame configurations than it intentionally
sells as standard products.

```
Moulding × Material × Finish × Extras × Dimensions × Custom details  =  capability space
```

An **Offering** is a deliberately curated subset of that space — something the
shop intends to sell repeatedly, get efficient at, possibly batch, possibly
stock, and possibly price differently from one-off custom fabrication. This
distinction (curated standard product vs arbitrary capability) is load-bearing
and appears throughout the domain docs.

---

## How to work in this repo

See [`../../AGENTS.md`](../../AGENTS.md). In short: implement only what is asked,
specify before implementing, keep unresolved questions unresolved, and stop and
explain if a request conflicts with an existing domain assumption.
