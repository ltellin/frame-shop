# Custom Frame Shop Software — Project Brief

> This is the original project brief, reproduced verbatim. It is the source of
> truth for *intent*. Where later decisions refine or diverge from it, that is
> recorded in `docs/architecture/decisions/` and `docs/roadmap.md`.

---

I want to build a browser-based application for running a custom picture framing shop.

LifeSaver framing software is a useful reference for the breadth of functionality and established frame-shop workflows. It is powerful but archaic and difficult to use. I am not trying to reinvent every standard framing-shop business process. The main area where I want to innovate is the user experience, while keeping the underlying architecture and data model flexible and conventional enough to support real shop operations.

This is currently a prototype. Do not over-engineer it, but do not make early architectural decisions that unnecessarily prevent the system from growing into full shop-management software.

## Development preferences

* Browser-based application.
* Python backend. I am comfortable with Python and would like domain/business logic to live there.
* JavaScript/TypeScript frontend is fine.
* Frontend and backend should be cleanly separated.
* Important framing/pricing/business rules should not live only in the frontend.
* Use a relational database unless there is a compelling reason otherwise.
* Prefer boring, understandable technology over unnecessary infrastructure.
* The application may eventually be used simultaneously at a front counter, wood shop, mounting/matting area, and pickup area.
* Design the backend so different interfaces/views can eventually sit on top of the same data.

Do not assume a specific frontend framework or Python framework merely because it is popular. Recommend a practical stack for this project and explain the important tradeoffs briefly.

# Core domain concepts

The terminology below is our current working model. It may evolve.

## Customer

A customer can have multiple orders over time. We need normal customer/contact/history functionality similar to other frame-shop management software.

## Artwork / Piece

A physical item brought into the shop to be framed.

It has dimensions and potentially other attributes relevant to framing and production.

## Design

A Design is what the framer creates interactively with the customer.

When the customer brings in artwork, the framer starts entering:

* artwork information and measurements
* moulding(s)
* matting
* fillets
* glazing
* mounting method
* backing
* fabric or other relevant materials/services
* other framing components

As selections change, the application should continuously show pricing.

A Design is an editable specification, not yet necessarily a production commitment.

A Design may eventually be:

* discarded
* put on hold
* saved as a quote
* accepted/submitted and used to generate a Work Order

### Important: design structure

Do NOT assume a design is just a fixed schema like:

* moulding
* mat_1
* mat_2
* glass
* mounting

Custom framing can contain arbitrary combinations such as:

* multiple stacked mouldings
* multiple mats
* fillets
* unusual mounting arrangements
* glazing
* backing
* additional components

At the same time, do NOT lock the domain into the idea that a Design is literally just one linear "stack."

There are multiple useful representations of a framing design.

One important representation is the traditional framing-industry **outside-to-inside** description.

Another is a spatial/exploded representation showing the physical relationship between layers/components.

The underlying domain model should preserve the components and their relevant relationships sufficiently well that multiple representations can be derived later.

The UI representation should not dictate the database model.

## Order

An Order represents the customer-facing commercial transaction.

A customer may bring in several pieces at once. That should normally be represented as one Order containing several pieces/designs rather than several unrelated customer transactions.

The Order is the natural place for concepts such as:

* subtotal
* discounts
* tax
* payments
* deposit
* total balance
* invoice
* overall customer transaction

## Work Order

A Work Order represents **one physical finished piece the shop has committed to producing and delivering**.

Conceptually:

Customer
→ Order
→ one or more Work Orders

Each Work Order corresponds to a physical piece and is generated from an accepted Design.

Example:

Order #5271

* Work Order #5271-1 → Artwork A → accepted Design A
* Work Order #5271-2 → Artwork B → accepted Design B
* Work Order #5271-3 → Artwork C → accepted Design C

This distinction is important because the individual pieces can move through production independently while still belonging to one customer transaction.

Treat the exact database relationship between Work Order and Design as a design problem. We may eventually need design snapshots/revisions/versioning so historical production specifications cannot accidentally change when later edits occur.

# Intake / sales workflow

A typical interaction currently works roughly like this:

1. Customer brings in artwork.
2. Framer measures it and begins a Design.
3. Framer and customer experiment with moulding, mats, glazing, mounting, etc.
4. Price updates as the Design changes.
5. The Design may be discarded, put on hold, quoted, or accepted.
6. If accepted, the customer typically pays either:

   * 50% deposit, or
   * payment in full.
7. An invoice is generated.
8. A Work Order is generated for each accepted physical piece.
9. Artwork is tagged/associated with its Work Order number.
10. The Work Order enters production.

Financial state, production state, and fulfillment state should not be collapsed into one giant status value.

For example, a job may simultaneously be:

* production: assembled
* payment: deposit paid / balance remaining
* fulfillment: still in shop

# Production workflow

Broadly, production includes parallel or semi-independent work on the frame and artwork.

For example:

Frame:

* needs frame fabrication
* frame in progress
* frame ready

Artwork:

* needs mounting/attachment
* artwork preparation in progress
* artwork ready

Assembly/fitting:

* waiting for prerequisites
* ready to fit
* fit/assembled

Once the frame and artwork are ready, they can be fit together.

When fitting/assembly is complete, the Work Order is considered assembled/complete from a production perspective.

When the customer picks it up and settles any outstanding balance, it is marked delivered.

## Production-state philosophy

The backend should be capable of representing meaningful production state without requiring employees to manually update every tiny state transition.

Every state change requiring human interaction is a worker "touch." Too many touches make the system annoying and will cause workers to stop maintaining accurate state.

Therefore distinguish conceptually between:

* explicit state: something a worker actually records
* derived state: something the system can infer from prerequisites
* display state: a simpler label shown in the UI

Example:

frame ready + artwork ready
→ system can derive "ready to fit"

The internal production model can be more granular than the interface.

Also avoid modeling production as a single rigid sequential state machine. Frame fabrication and artwork preparation may happen in parallel.

A Work Order will probably have production requirements/operations/tasks with dependencies, from which higher-level progress can be derived.

Do not over-engineer this into a generic enterprise workflow engine for the prototype.

# Daily closing / production lists

LifeSaver uses a process called "daily closing."

Several orders are taken during the day. At closing, the software generates separate production/material lists such as:

* moulding
* matboard
* glazing
* fabrics
* potentially other categories

These are effectively pick/cut/work lists used by people in different shop areas.

I want to preserve the broad capability, but the database should NOT make a particular printed "daily closing" list the fundamental source of truth.

Prefer canonical Design / Work Order / production requirement data from which things like:

* today's moulding cut list
* matboard list
* glazing list
* wood-shop queue
* mounting queue
* reprinted historical lists
* rush additions

can be derived.

Whether "Daily Closing" remains an explicit user action can be decided later.

# Products and vendors

The software needs a product/catalog system for things such as:

* mouldings
* matboards
* glazing
* fabrics
* potentially mounting products and other materials

Products should be associated with vendors/manufacturers and useful catalog metadata.

The software should eventually be able to ingest whatever supported data vendors expose, especially:

* product information
* vendor SKU
* pricing/cost
* availability
* discontinued status

If a user adds or has added a discontinued/unavailable product to an active Design, the system should warn them appropriately.

Historical orders must remain historically accurate.

Live vendor catalog data and historical transaction data are different concepts.

For example, if a moulding costs more next month, an old invoice must not change.

Design/order components therefore probably need appropriate snapshots of descriptions, costs, prices, pricing assumptions, etc., at the relevant point in the sales lifecycle.

Exact vendor APIs/integration mechanisms are out of scope for the first prototype, but architecture should leave an obvious place for them.

# Pricing

Interactive Design editing should continuously produce a price.

Pricing logic belongs in the backend/domain layer even if the frontend updates optimistically for responsiveness.

The exact framing pricing system has NOT been fully specified yet.

Do not invent detailed framing pricing rules.

Create an architecture where pricing rules can evolve without rewriting the Design model.

# Visual Design representation — important UX goal

One of the signature UX ideas for this application is a schematic representation of each framing Design.

This is NOT intended to be a photorealistic rendering.

Imagine an exploded technical diagram viewed from the side at a slight downward angle:

* frame/moulding
* glazing
* mats
* fillets
* artwork
* mounting/backing
* etc.

Components can be visually separated and labeled, similar to an exploded mechanical diagram.

Eventually components might animate apart/together or highlight when edited.

This should also create a visual "fingerprint" for a job. When browsing Work Orders, users should be able to recognize the piece visually instead of relying only on work-order number, dimensions, or customer name.

This visualization is a frontend concern driven from Design data.

Potential technologies could include SVG, Canvas, or a WebGL/Three.js-style approach. Do not choose a heavy 3D solution unless it is actually justified.

For the first prototype, a simplified schematic is sufficient.

# Important architectural principles

1. Preserve domain information independently of its current UI representation.

2. Do not prematurely lock framing Designs into fixed component slots.

3. Also do not prematurely lock Designs into one canonical "stack" representation.

4. Separate:

   * Design/specification
   * customer Order/commercial transaction
   * Work Order/production commitment
   * payment state
   * production state
   * fulfillment state
   * vendor/catalog reference data

5. Generated artifacts and operational views such as invoices, work-order sheets, labels, pick lists, and cut lists should generally derive from canonical business data.

6. Historical sales/production records must not silently change when vendor catalog information or pricing changes.

7. The production model may be more detailed than the UI. Minimize unnecessary worker touches.

8. Favor flexibility through a good domain model rather than through a generic abstraction framework.

9. Do not build a generic ERP engine. This is purpose-built custom framing software.

10. Where LifeSaver or similar software already solves an ordinary framing-shop requirement adequately, treat that as a parity requirement rather than assuming we need a novel solution.

The primary innovation target is the experience of using the software.

# Prototype objective

The first prototype should concentrate on the central interaction:

**Create a Design for one piece of artwork and interactively build/edit its framing specification while seeing its price and schematic representation.**

I do NOT expect the first implementation to include the entire ERP.

However, its architecture should fit naturally into the larger model above.

A reasonable first vertical slice may include:

* create/select a customer, possibly extremely simplified
* create a new Design
* enter artwork dimensions
* add/remove/reorder/configure some representative component types
* use fake/sample product catalog data
* show current calculated price using deliberately simple placeholder pricing rules
* render a simple schematic/exploded representation from the Design
* save a Design
* distinguish a draft/held Design from an accepted Design
* accept a Design and generate a simple Work Order
* persist everything to a local development database

Do not attempt real vendor integrations, accounting, complete production management, authentication/permissions, or sophisticated pricing in this first vertical slice unless they are necessary to establish architecture.
