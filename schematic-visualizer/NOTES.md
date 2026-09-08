# Schematic / visualizer — preserved from prototype-v0

A preserved, standalone copy of the framing schematic so it can be rebuilt into
the next version of the app. The four source files (`layout.ts`, `Schematic.tsx`,
`theme.ts`, `schematic.css`) are the last working versions verbatim. This file is
the spec.

The full prior app that these came from: `git checkout prototype-v0`.

---

## Purpose

A **non-photorealistic exploded side-view** of a framing design — frame, glazing,
mats, fillets, artwork, spacers, backing shown as separated, labelled layers,
viewed from a shallow downward angle. It doubles as a visual **"fingerprint"**: a
framer browsing work orders should recognise a piece by its schematic, not just
its number.

Explicitly *not* a photoreal render, and not 3D.

---

## Input contract — the "exploded layout" model

The renderer takes one object (`ExplodedLayout`), which the backend produces as a
**pure function** of a design's flat ordered list of typed components + the base
rectangle it's built around:

```ts
type ExplodedLayout = {
  units: 'in'
  layers: ExplodedLayer[]
  bounds: { width_in: number; height_in: number }   // largest layer footprint
}

type ExplodedLayer = {
  component_id: number | null   // null for the artwork pseudo-layer
  kind: string                  // moulding | mat | glazing | fillet | mount | backing | spacer | fabric | artwork | ...
  layer_role: string            // see vocabulary below
  provenance: 'shop' | 'customer'
  label: string
  width_in: number              // the layer's own footprint
  height_in: number
  opening_width_in: number | null   // the visible window, for framed / matted layers
  opening_height_in: number | null
  z_index: number               // 0 = backmost, ascending toward the viewer
}
```

### How the backend built it (so it can be rebuilt)

- Walk the components from the base rectangle outward, accumulating a running
  size. Each component kind reports its own footprint, its window/opening, and
  the new running outer size (`walk_layers` → `LayerGeometry`).
- `layer_role` vocabulary: `frame, glazing, fillet, mat, art, spacer, substrate,
  backing, accent`. Each component kind has a default role.
- `z_index`: assign a back→front order from a role priority
  (`backing:0, substrate:1, spacer:2, art:3, fillet:5, mat:6, accent:7,
  glazing:8, frame:9`), tie-broken by sequence (more-inside = further back), then
  renumber 0..n-1.
- The **artwork pseudo-layer** (`component_id: null`, `kind: 'artwork'`) is added
  only when the design is built around the art (`base_ref === 'art'`); mat-only /
  glass-only / frame-only designs have no art layer.
- **Services / fees are excluded** — they're line items, not physical layers
  (`ComponentKind.rendered === false`).
- `bounds` = the max width/height over all layers (used to scale the drawing).

---

## Projection & rendering (`layout.ts` → `buildSchematic`)

Turns the layout model into SVG geometry. Pure presentation — no framing rules.

- **Shallow oblique view.** One knob: `VIEW_ANGLE_DEG` (currently `10`). Each
  layer's face is foreshortened vertically to `sin(VIEW_ANGLE_DEG)` of its true
  scaled height, so layers read almost edge-on, like a fanned stack of cards.
  A bounded sideways lean (`LEAN ≈ 1.6 × faceHeight`) gives the 3D feel without
  running off-canvas.
- **Stack order.** Layers are drawn **frontmost-on-top**: the frame sits at the
  top of the diagram, backing at the bottom, artwork low in the stack. (Sort the
  layers by `z_index` **descending**.) Vertical spacing `GAP_Y`, slight
  horizontal drift `GAP_X`.
- **Hollow frames.** A layer whose `layer_role` is `frame` or `fillet` and that
  has an opening is drawn as a **ring**: an SVG `<path>` with an outer subpath +
  an inner (opening) subpath, rendered `fill-rule="evenodd"` so the middle is
  punched out and the striped background shows through — it reads as an empty
  frame. The inner opening is clamped so the border stays visible
  (`RING_BORDER_X/Y`).
- **Other layers.** A solid sheared parallelogram (`<path>`), plus — if it has an
  opening — a faint white inner "window" polygon (e.g. the mat's window).
- **Openings** get a minimum on-screen height (`MIN_OPENING_H`) so they don't
  collapse to a line at the shallow angle.
- **Scale:** fit the widest layer to `MAX_LAYER_W` px.
- **Labels** sit in a right-hand gutter (`LABEL_GUTTER`), each with a thin leader
  line to its layer's top-right corner; a dotted "spine" connects the layer
  corners. Long labels are trimmed (`MAX_LABEL`).
- Everything is emitted as SVG `<path>` `d` strings + a few point lists; the model
  is renderer-agnostic.

---

## Rendering & interaction (`Schematic.tsx`)

- Renders one `<svg>` with a `viewBox` from `model.width/height`.
- Per layer: leader polyline, the face `<path>` (with `fill-rule="evenodd"` when
  `layer.ring`), a hatch `<path>` overlay when `customerSupplied`, the faint
  window polygon when present, and the label `<text>`.
- **Colour** comes from `roleColor(layer_role)` (`theme.ts`) — a small
  role→colour palette. Glazing is drawn semi-transparent.
- **Customer-supplied** layers get a 45° hatch pattern (`<pattern id="com-hatch">`)
  and a " · customer's" label suffix.
- **Selection:** the selected component's layer gets a bold `--accent` stroke.
  Clicking a layer calls `select(componentId)`; the component list and the
  schematic share one `selectedComponentId`. (In the prototype this came from a
  `useDesignEditor()` context providing `design`, `selectedId`, `select`.)

### External dependencies to re-wire when rebuilding

- `buildSchematic(design.representations.exploded)` — the layout model from the
  backend design read model.
- `useDesignEditor()` → `{ design, selectedId, select }` — replace with whatever
  state the new app uses.
- `roleColor()` from `theme.ts` — or map roles to the new design system's colours.
- The CSS custom properties listed at the top of `schematic.css`.

---

## Why inline SVG (keep this choice unless a real 3D need appears)

The requirement is a handful of labelled rectangular layers (< 20) at a slight
angle. SVG gives crisp vector output at any zoom, **text labels as real DOM
nodes**, trivial click hit-testing, and CSS/SMIL animation for the future
"animate apart / highlight on edit" idea — with **no library**. Canvas only wins
with thousands of primitives; WebGL only earns its weight with true perspective /
lighting / camera control, none of which a "fingerprint" diagram needs. The
layout model is renderer-agnostic, so a later swap changes only the renderer.
