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
src/state/        designEditor.tsx — the one editable Design object + optimistic
                  edit + debounced PATCH + reconcile. Both panes bind to this.
src/features/
  home/           start-a-design form + design list
  design-editor/  ComponentList, ComponentParamsPanel (schema-driven), PricePanel
  schematic/      Schematic.tsx + layout.ts (the SVG exploded view)
src/theme.ts      ROLE_COLORS — shared layer vocabulary (list + schematic)
```

## Conventions

- Edit a component → update local state optimistically → the store debounce-PATCHes
  the full component list → the backend response is authoritative and reconciles.
- `types.ts` is maintained by hand for now. If the backend read model changes,
  update `types.ts` in the same change. (Generating from OpenAPI is a deferred
  nice-to-have — see `docs/roadmap.md`.)
- Keep `useDesignEditor` the single source of truth; panes are pure views.
