# ADR 0011 — SVG for the schematic

- **Status:** accepted
- **Date:** 2026-09-05

## Context

A signature UX goal: a non-photorealistic exploded technical diagram of each
Design — frame, glazing, mats, fillets, artwork, mounting/backing — viewed from
the side at a slight downward angle, with separated, labeled layers. It should
become a visual "fingerprint" for a job. Eventually layers might animate
apart/together or highlight on edit. The brief: "Do not choose a heavy 3D
solution unless it is actually justified. For the first prototype, a simplified
schematic is sufficient."

## Decision

Render the schematic as **inline SVG**. The backend produces a renderer-agnostic
exploded-layout model (`to_exploded_layout()` — one entry per layer with size,
opening, `z_index`, role, label). The frontend's `layout.ts` maps that to SVG
polygon coordinates (a shear transform gives the "slight angle"); `Schematic.tsx`
draws polygons + labels + leader lines and wires click-to-select.

## Consequences

- Crisp at any zoom; text labels are first-class DOM nodes; hit-testing for
  click-to-select is trivial; CSS/SMIL transitions cover the future
  animate/highlight ideas — all with **no library**.
- The layout model is renderer-agnostic, so a specific view could later swap to
  Canvas or WebGL without touching the domain.
- Current limitation: with many layers the SVG explode looks cramped and leader
  lines can cross — a presentation-only polish task (`../roadmap.md`), not an
  architecture problem.
- **You may not** move layer geometry into the frontend (ADR 0002) — `layout.ts`
  is coordinate mapping only.

## Alternatives considered

- **Canvas 2D** — only wins with thousands of primitives or pixel effects; loses
  easy text, DOM hit-testing, and CSS animation.
- **WebGL / Three.js** — earns its weight only with true 3D perspective,
  lighting, or camera control, none of which a labeled "fingerprint" diagram
  needs. Revisit only if a concrete 3D requirement appears.
