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
  outline: string // polygon points for the layer face
  opening: string | null // polygon points for the visible window, if any
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
const MIN_OPENING_H = 6 // px — keep mat windows visible at a shallow angle
const LABEL_GUTTER = 210
const MAX_LAYER_W = 180 // px cap for the widest layer
const MAX_LABEL = 26

function trim(s: string): string {
  return s.length > MAX_LABEL ? s.slice(0, MAX_LABEL - 1) + '…' : s
}

export function buildSchematic(layout: ExplodedLayout): SchematicModel {
  const ordered = [...layout.layers].sort((a, b) => a.z_index - b.z_index)
  const n = ordered.length || 1
  const bounds = layout.bounds

  const scale = Math.max(4, MAX_LAYER_W / Math.max(bounds.width_in, 1))
  const tallestFace = Math.max(...ordered.map((l) => l.height_in * scale * FACE_SCALE), 1)
  const height = PAD * 2 + (n - 1) * GAP_Y + tallestFace + 12

  const layers: PlacedLayer[] = ordered.map((layer, i) => {
    const w = layer.width_in * scale
    const faceH = layer.height_in * scale * FACE_SCALE
    const skew = faceH * LEAN

    // Frontmost layer (highest z) sits lowest / leftmost; backmost highest / right.
    const fromFront = n - 1 - i
    const x = PAD + fromFront * GAP_X
    const y = PAD + i * GAP_Y

    const outline = poly([
      [x + skew, y],
      [x + skew + w, y],
      [x + w, y + faceH],
      [x, y + faceH],
    ])

    let opening: string | null = null
    if (layer.opening_width_in && layer.opening_height_in) {
      const ow = layer.opening_width_in * scale
      const oh = Math.max(layer.opening_height_in * scale * FACE_SCALE, MIN_OPENING_H)
      const os = oh * LEAN
      const ox = x + (w - ow) / 2
      const cyTop = y + faceH / 2 - oh / 2
      const cyBot = y + faceH / 2 + oh / 2
      opening = poly([
        [ox + os, cyTop],
        [ox + os + ow, cyTop],
        [ox + ow, cyBot],
        [ox, cyBot],
      ])
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
      opening,
      labelAnchor,
      leader,
      z: layer.z_index,
    }
  })

  return { width: VIEW_W, height, layers }
}

function poly(points: [number, number][]): string {
  return points.map(([x, y]) => `${round(x)},${round(y)}`).join(' ')
}

function round(n: number): number {
  return Math.round(n * 100) / 100
}
