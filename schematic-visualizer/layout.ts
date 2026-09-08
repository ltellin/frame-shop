// Turn the backend's renderer-agnostic exploded-layout model into 2D SVG
// geometry. This file is pure presentation: no framing rules live here.
import type { ExplodedLayout } from '../../api/types'
import { roleColor } from '../../theme'

export type PlacedLayer = {
  componentId: number | null
  kind: string
  role: string
  label: string
  color: string
  labelText: string
  customerSupplied: boolean
  outline: string // SVG path `d` for the layer face (a ring for frame-type layers)
  ring: boolean // outline has an inner subpath — render with fill-rule evenodd
  opening: string | null // polygon points for a drawn window (non-ring layers, e.g. mat)
  labelAnchor: { x: number; y: number }
  leader: string // polyline points from layer to its label
  z: number
}

export type SchematicModel = {
  width: number
  height: number
  layers: PlacedLayer[]
}

const VIEW_W = 560
const PAD = 28
const GAP_Y = 40 // vertical spacing between exploded layers
const GAP_X = 12 // slight horizontal drift; back layers sit to the right
// How edge-on each layer is drawn: the angle its face makes with the horizontal
// line of sight. Low = seen almost from the side. This is the one knob.
const VIEW_ANGLE_DEG = 10
const FACE_SCALE = Math.sin((VIEW_ANGLE_DEG * Math.PI) / 180) // vertical foreshortening
const LEAN = 1.6 // sideways shift of the far (top) edge, as a multiple of the face's screen height
const MIN_OPENING_H = 6 // px — keep drawn windows visible at a shallow angle
const RING_BORDER_X = 4 // px — min visible frame border, left/right
const RING_BORDER_Y = 3 // px — min visible frame border, top/bottom
const LABEL_GUTTER = 210
const MAX_LAYER_W = 180 // px cap for the widest layer
const MAX_LABEL = 26

const RING_ROLES = new Set(['frame', 'fillet'])

function trim(s: string): string {
  return s.length > MAX_LABEL ? s.slice(0, MAX_LABEL - 1) + '…' : s
}

export function buildSchematic(layout: ExplodedLayout): SchematicModel {
  // Frontmost (highest z_index — the frame) is drawn at the top; backing sits at
  // the bottom, artwork low in the stack.
  const ordered = [...layout.layers].sort((a, b) => b.z_index - a.z_index)
  const n = ordered.length || 1
  const bounds = layout.bounds

  const scale = Math.max(4, MAX_LAYER_W / Math.max(bounds.width_in, 1))
  const tallestFace = Math.max(...ordered.map((l) => l.height_in * scale * FACE_SCALE), 1)
  const height = PAD * 2 + (n - 1) * GAP_Y + tallestFace + 12

  const layers: PlacedLayer[] = ordered.map((layer, i) => {
    const w = layer.width_in * scale
    const faceH = layer.height_in * scale * FACE_SCALE
    const skew = faceH * LEAN

    const x = PAD + i * GAP_X
    const y = PAD + i * GAP_Y

    // Outer face parallelogram, corners TL, TR, BR, BL (top edge sheared right).
    const face: [number, number][] = [
      [x + skew, y],
      [x + skew + w, y],
      [x + w, y + faceH],
      [x, y + faceH],
    ]

    const hasWindow = !!(layer.opening_width_in && layer.opening_height_in)
    const ring = RING_ROLES.has(layer.layer_role) && hasWindow

    let outline: string
    let opening: string | null = null

    if (ring) {
      // Punch a hole so it reads as an empty frame.
      const ow = clamp(layer.opening_width_in! * scale, w * 0.4, w - 2 * RING_BORDER_X)
      const oh = clamp(layer.opening_height_in! * scale * FACE_SCALE, faceH * 0.4, faceH - 2 * RING_BORDER_Y)
      outline = pathD(face) + ' ' + pathD(centeredParallelogram(x, y, w, faceH, ow, oh))
    } else {
      outline = pathD(face)
      if (hasWindow) {
        const ow = layer.opening_width_in! * scale
        const oh = Math.max(layer.opening_height_in! * scale * FACE_SCALE, MIN_OPENING_H)
        opening = poly(centeredParallelogram(x, y, w, faceH, ow, oh))
      }
    }

    const labelAnchor = { x: VIEW_W - LABEL_GUTTER + 8, y: y + faceH / 2 }
    const leader = `${round(x + skew + w)},${round(y + 2)} ${round(labelAnchor.x - 8)},${round(
      labelAnchor.y,
    )}`

    return {
      componentId: layer.component_id,
      kind: layer.kind,
      role: layer.layer_role,
      label: layer.label,
      color: roleColor(layer.layer_role),
      labelText: trim(layer.label),
      customerSupplied: layer.provenance === 'customer' && layer.kind !== 'artwork',
      outline,
      ring,
      opening,
      labelAnchor,
      leader,
      z: layer.z_index,
    }
  })

  return { width: VIEW_W, height, layers }
}

// A parallelogram of size ow x oh, centred in the w x faceH face at (x, y),
// sheared to match the face.
function centeredParallelogram(
  x: number,
  y: number,
  w: number,
  faceH: number,
  ow: number,
  oh: number,
): [number, number][] {
  const ox = x + (w - ow) / 2
  const os = oh * LEAN
  const top = y + faceH / 2 - oh / 2
  const bot = y + faceH / 2 + oh / 2
  return [
    [ox + os, top],
    [ox + os + ow, top],
    [ox + ow, bot],
    [ox, bot],
  ]
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v))
}

function pathD(points: [number, number][]): string {
  return points.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${round(x)},${round(y)}`).join(' ') + ' Z'
}

function poly(points: [number, number][]): string {
  return points.map(([x, y]) => `${round(x)},${round(y)}`).join(' ')
}

function round(n: number): number {
  return Math.round(n * 100) / 100
}
