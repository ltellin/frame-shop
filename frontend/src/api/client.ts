import type {
  ComponentInput,
  ComponentKindMeta,
  CustomerListItem,
  DesignImage,
  DesignListItem,
  DesignRead,
  DesignTypeMeta,
  OrderDetail,
  OrderSummary,
  Product,
} from './types'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: init?.body instanceof FormData ? undefined : { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? JSON.stringify(body)
    } catch {
      /* keep statusText */
    }
    const err = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    ;(err as Error & { status?: number }).status = res.status
    throw err
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export type DesignStartBody = {
  name?: string
  type?: string
  base_ref?: string
  base_width_in?: string
  base_height_in?: string
  art?: Record<string, unknown>
  quantity?: number
  customer_id?: number
  order_id?: number
  seed_starter?: boolean
  components?: ComponentInput[]
}

export type DesignPatchBody = {
  name?: string
  status?: string
  type?: string
  base_ref?: string
  base_width_in?: string
  base_height_in?: string
  art?: Record<string, unknown>
  quantity?: number
  customer_id?: number | null
  components?: ComponentInput[]
}

export const api = {
  componentKinds: () => request<ComponentKindMeta[]>('/catalog/component-kinds'),
  designTypes: () => request<DesignTypeMeta[]>('/catalog/design-types'),

  products: (kind?: string) =>
    request<Product[]>(`/catalog/products${kind ? `?kind=${kind}` : ''}`),

  listDesigns: (opts?: { loose?: boolean; orderId?: number }) => {
    const qs = new URLSearchParams()
    if (opts?.loose) qs.set('loose', 'true')
    if (opts?.orderId != null) qs.set('order_id', String(opts.orderId))
    return request<DesignListItem[]>(`/designs${qs.toString() ? `?${qs}` : ''}`)
  },

  getDesign: (id: number) => request<DesignRead>(`/designs/${id}`),
  startDesign: (body: DesignStartBody) =>
    request<DesignRead>('/designs', { method: 'POST', body: JSON.stringify(body) }),
  patchDesign: (id: number, body: DesignPatchBody) =>
    request<DesignRead>(`/designs/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  addToOrder: (
    id: number,
    body: {
      order_id?: number
      customer_id?: number
      customer?: { name: string; phone?: string; email?: string }
      due_date?: string
    },
  ) =>
    request<{ order_id: number; order_number: number; design: DesignRead }>(
      `/designs/${id}/add-to-order`,
      { method: 'POST', body: JSON.stringify(body) },
    ),

  uploadDesignImage: (id: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<DesignImage>(`/designs/${id}/images`, { method: 'POST', body: form })
  },
  captureDesignImage: (id: number) =>
    request<DesignImage>(`/designs/${id}/images/capture`, { method: 'POST' }),
  deleteDesignImage: (id: number, imageId: string) =>
    request<void>(`/designs/${id}/images/${imageId}`, { method: 'DELETE' }),

  listCustomers: () => request<CustomerListItem[]>('/customers'),
  createCustomer: (body: { name: string; phone?: string; email?: string }) =>
    request<{ id: number; name: string }>('/customers', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  listOrders: () => request<OrderSummary[]>('/orders'),
  getOrder: (id: number) => request<OrderDetail>(`/orders/${id}`),
}

export function formatCents(cents: number): string {
  return (cents / 100).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
