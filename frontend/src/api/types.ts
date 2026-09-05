// Hand-written mirror of the backend read model. For a later milestone these
// can be generated from the FastAPI OpenAPI schema via openapi-typescript.

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

export type ProductSummary = {
  id: number
  name: string
  vendor_name: string
  sku: string
  price_uom: string
  unit_price_cents: number
  available: boolean
  discontinued: boolean
}

export type DesignComponent = {
  id: number
  kind: string
  sequence: number
  layer_role: string
  params: Record<string, unknown>
  product_id: number | null
  parent_component_id: number | null
  product: ProductSummary | null
}

export type OutsideInEntry = {
  position: number
  component_id: number | null
  kind: string
  layer_role: string
  label: string
}

export type ExplodedLayer = {
  component_id: number | null
  kind: string
  layer_role: string
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

export type Artwork = {
  id: number
  title: string
  description: string | null
  width_in: number
  height_in: number
  depth_in: number | null
  notes: string | null
}

export type DesignRead = {
  id: number
  order_id: number
  artwork_id: number
  name: string
  status: 'draft' | 'held' | 'quoted' | 'accepted' | 'discarded'
  version: number
  editable: boolean
  updated_at: string | null
  artwork: Artwork
  components: DesignComponent[]
  price: PriceBreakdown
  representations: {
    outside_in: OutsideInEntry[]
    exploded: ExplodedLayout
  }
  warnings: string[]
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
  unit_price_cents: number
  price_uom: string
  available: boolean
  discontinued: boolean
}

export type ComponentInput = {
  id?: number
  kind: string
  params: Record<string, unknown>
  layer_role?: string | null
  product_id?: number | null
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
  piece_count: number
  design_count: number
}

export type OrderDetail = {
  id: number
  number: number
  status: string
  customer_id: number
  customer_name: string
  artworks: { id: number; title: string; width_in: number; height_in: number; depth_in: number | null }[]
  designs: { id: number; name: string; status: string; artwork_title: string }[]
}
