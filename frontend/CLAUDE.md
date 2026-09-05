# Frontend — rules for this subtree

React 19 + TypeScript + Vite. TanStack Query for server state.

## Commands

```bash
npm run dev        # dev server on :5173, proxies /api -> :8000
npx tsc -b         # typecheck (also in /checks)
npm run build      # production build (also in /checks)
npm run lint       # oxlint
```

## Hard rule: no business logic here

No framing math, no pricing math, no geometry math. The backend returns:

- `price` — a `PriceBreakdown` with line items and a subtotal → render as-is.
- `representations.exploded` — a renderer-agnostic layer model → `layout.ts`
  turns it into SVG coordinates (presentation only), `Schematic.tsx` draws it.
- `representations.outside_in` — the textual spec.

If you find yourself computing what a frame costs or how big a mat is in TS, it
belongs in `backend/app/domain/`.

## Structure

```
src/api/          client.ts (the ONLY place that calls the backend) + types.ts
                  (hand-written mirror of the backend read model — keep in sync)
src/nav.ts        navigate(hash) — hash routing, no router library
src/App.tsx       parseHash() route table + top-level render switch
src/state/        designEditor.tsx — the one editable Design object + optimistic
                  edit + debounced PATCH + reconcile. Panes bind to this.
src/features/
  landing/        Landing.tsx — home screen + Drafts list
  design/         NewDesignGate.tsx — pick type + base dimensions → creates the
                  autosaved draft, then navigates to the editor
  design-editor/  DesignEditor, PiecePanel (type/dims/art/qty/images),
                  ImagesStrip, ComponentList, ComponentParamsPanel (+ shop/customer
                  toggle), PricePanel, SizeReadout, AddToOrderDialog
  schematic/      Schematic.tsx + layout.ts (the SVG exploded view)
  customers/      Customers.tsx — list + quick add
  orders/         Orders.tsx (list) + OrderDetail.tsx (pieces + "add another design")
src/theme.ts      ROLE_COLORS — shared layer vocabulary (list + schematic)
```

Routes (hash): `#/` · `#/design/new[?order=N]` gate · `#/designs/:id[?order=N]`
editor · `#/customers` · `#/orders` · `#/orders/:id`.

## Conventions

- **Getting to the design editor takes no upfront info** — the gate asks only
  "what are you making?" + dimensions; entering both autosaves a draft (loose:
  no customer, no order) and drops into the editor. Leaving keeps the draft.
- The editor `design.complete` is `false` until base dims exist — panels show a
  hint, not a crash.
- Edit a component → optimistic local update → debounced full-list PATCH → the
  backend response is authoritative and reconciles. Field edits (type, dims, art,
  quantity, provenance) go through `patchFields` immediately.
- `design.price` / `design.representations` / `design.summary` can be `null`.
- `types.ts` is maintained by hand — update it with `to_read_model` in the same
  change.
- Keep `useDesignEditor` the single source of truth; panes are pure views.
