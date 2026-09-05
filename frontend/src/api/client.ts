import type {
  ComponentInput,
  ComponentKindMeta,
  DesignRead,
  Product,
} from './types'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
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
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return res.json() as Promise<T>
}

export const api = {
  componentKinds: () => request<ComponentKindMeta[]>('/catalog/component-kinds'),

  products: (kind?: string) =>
    request<Product[]>(`/catalog/products${kind ? `?kind=${kind}` : ''}`),

  listDesigns: () =>
    request<
      {
        id: number
        name: string
        status: string
        artwork_title: string
        width_in: number
        height_in: number
        subtotal_cents: number | null
        updated_at: string | null
      }[]
    >('/designs'),

  getDesign: (id: number) => request<DesignRead>(`/designs/${id}`),

  startDesign: (body: {
    customer?: { name: string; phone?: string; email?: string }
    customer_id?: number
    artwork: { title: string; width_in: string; height_in: string; depth_in?: string }
    name?: string
    components?: ComponentInput[]
  }) =>
    request<DesignRead>('/designs', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  patchDesign: (
    id: number,
    body: {
      name?: string
      status?: string
      artwork?: Record<string, unknown>
      components?: ComponentInput[]
    },
  ) =>
    request<DesignRead>(`/designs/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
}

export function formatCents(cents: number): string {
  return (cents / 100).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
