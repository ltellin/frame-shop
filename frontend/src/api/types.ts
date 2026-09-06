// Hand-written mirror of the backend read model. Keep in sync with
// backend/app/services/design_service.py::to_read_model.

export type PriceLine = {
  component_id: number | null
  kind: string
  label: string
  detail: string
  amount_cents: number
}

export type PriceBreakdown = {
  lines: PriceLine[]
  subtotal_cents: number
  currency: string
  profile_id: string
  profile_version: number
  notes: string[]
}

// The moulding profile (and stubs for other kinds). All fields optional —
// see backend/app/domain/catalog/product_kinds.py.
export type ProductSpec = {
  face_width_in?: number | string
  height_in?: number | string
  rabbet_width_in?: number | string
  rabbet_height_in?: number | string
  material?: string
  finish?: string
  [k: string]: unknown
}

export type ProductSummary = {
  id: number
  name: string
  vendor_name: string
  vendor_is_house: boolean
  sku: string
  price_uom: string
  unit_price_cents: number
  available: boolean
  discontinued: boolean
  spec: ProductSpec
}

export type Provenance = 'shop' | 'customer'

export type DesignComponent = {
  id: number
  kind: string
  sequence: number
  layer_role: string
  params: Record<string, unknown>
  product_id: number | null
  provenance: Provenance
  parent_component_id: number | null
  product: ProductSummary | null
}

export type OutsideInEntry = {
  position: number
  component_id: number | null
  kind: string
  layer_role: string
  provenance: string
  label: string
}

export type ExplodedLayer = {
  component_id: number | null
  kind: string
  layer_role: string
  provenance: string
  label: string
  width_in: number
  height_in: number
  opening_width_in: number | null
  opening_height_in: number | null
  z_index: number
}

export type ExplodedLayout = {
  units: string
  layers: ExplodedLayer[]
  bounds: { width_in: number; height_in: number }
}

export type DesignImage = {
  id: number
  image_id: string
  url: string
  source: 'upload' | 'camera'
  is_primary: boolean
  content_type: string
  created_at: string | null
}

export type DesignArt = {
  title: string | null
  description: string | null
  art_type: string | null
  depth_in: number | null
  notes: string | null
}

export type DesignSummary = {
  finished_width_in: number
  finished_height_in: number
  base_width_in: number
  base_height_in: number
  quantity: number
}

export type DesignRead = {
  id: number
  name: string
  type: string
  status: 'draft' | 'accepted' | 'discarded'
  editable: boolean
  version: number
  order_id: number | null
  customer_id: number | null
  customer_name: string | null
  quantity: number
  base_ref: string
  base_width_in: number | null
  base_height_in: number | null
  art: DesignArt
  updated_at: string | null
  images: DesignImage[]
  components: DesignComponent[]
  complete: boolean
  price: PriceBreakdown | null
  representations: { outside_in: OutsideInEntry[]; exploded: ExplodedLayout } | null
  summary: DesignSummary | null
  warnings: string[]
}

export type DesignTypeMeta = {
  key: string
  label: string
  base_ref: string
  has_art: boolean
  starter_stack: { kind: string; params?: Record<string, unknown>; provenance?: string }[]
}

export type ComponentKindMeta = {
  key: string
  label: string
  default_layer_role: string
  consumes_product: boolean
  param_schema: {
    properties?: Record<string, JsonSchemaProp>
    required?: string[]
  }
}

export type JsonSchemaProp = {
  type?: string
  title?: string
  default?: unknown
  description?: string
  enum?: string[]
  anyOf?: { type?: string; enum?: string[] }[]
}

export type Product = {
  id: number
  kind: string
  sku: string
  name: string
  description: string
  vendor_name: string
  vendor_is_house: boolean
  unit_price_cents: number
  price_uom: string
  available: boolean
  discontinued: boolean
  spec: ProductSpec
}

export type ComponentInput = {
  id?: number
  kind: string
  params: Record<string, unknown>
  layer_role?: string | null
  product_id?: number | null
  provenance?: Provenance
  parent_index?: number | null
}

export type CustomerListItem = {
  id: number
  name: string
  phone: string | null
  email: string | null
  order_count: number
}

export type OrderSummary = {
  id: number
  number: number
  status: string
  customer_id: number
  customer_name: string
  due_date: string | null
  design_count: number
}

export type OrderDetail = {
  id: number
  number: number
  status: string
  customer_id: number
  customer_name: string
  due_date: string | null
  po_number: string | null
  designs: {
    id: number
    name: string
    type: string
    status: string
    art_title: string | null
    base_width_in: number | null
    base_height_in: number | null
    subtotal_cents: number | null
  }[]
}

export type DesignListItem = {
  id: number
  name: string
  type: string
  status: string
  order_id: number | null
  customer_name: string | null
  base_ref: string
  base_width_in: number | null
  base_height_in: number | null
  subtotal_cents: number | null
  updated_at: string | null
}
