import { useQuery } from '@tanstack/react-query'
import { api, formatCents } from '../../api/client'
import type { ComponentKindMeta, DesignComponent, Product } from '../../api/types'
import { useDesignEditor } from '../../state/designEditor'
import { fieldsFor } from './paramSchema'

export function ComponentParamsPanel() {
  const { design, selectedId, updateParams, setProduct } = useDesignEditor()
  const kinds = useQuery({ queryKey: ['component-kinds'], queryFn: api.componentKinds })

  const component = design?.components.find((c) => c.id === selectedId) ?? null

  if (!component) {
    return (
      <aside className="panel">
        <h3>Component</h3>
        <p className="muted">Select a component to configure it.</p>
      </aside>
    )
  }

  const meta = kinds.data?.find((k) => k.key === component.kind)

  return (
    <aside className="panel">
      <h3>{meta?.label ?? component.kind}</h3>
      {meta?.consumes_product && (
        <ProductPicker
          kind={component.kind}
          value={component.product_id}
          onChange={(pid) => setProduct(component.id, pid)}
        />
      )}
      {meta && (
        <ParamFields
          meta={meta}
          component={component}
          onChange={(params) => updateParams(component.id, params)}
        />
      )}
    </aside>
  )
}

function ProductPicker({
  kind,
  value,
  onChange,
}: {
  kind: string
  value: number | null
  onChange: (id: number | null) => void
}) {
  const products = useQuery<Product[]>({
    queryKey: ['products', kind],
    queryFn: () => api.products(kind),
  })

  return (
    <label className="field">
      <span>Catalog product</span>
      <select
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
      >
        <option value="">— none (placeholder pricing) —</option>
        {(products.data ?? []).map((p) => (
          <option key={p.id} value={p.id}>
            {p.name} · {p.vendor_name} · {formatCents(p.unit_price_cents)}/{uom(p.price_uom)}
            {p.discontinued ? ' · DISCONTINUED' : p.available ? '' : ' · unavailable'}
          </option>
        ))}
      </select>
    </label>
  )
}

function ParamFields({
  meta,
  component,
  onChange,
}: {
  meta: ComponentKindMeta
  component: DesignComponent
  onChange: (params: Record<string, unknown>) => void
}) {
  const fields = fieldsFor(meta)
  const params = component.params

  const set = (name: string, raw: string, isNumber: boolean) => {
    const next = { ...params }
    if (raw === '') delete next[name]
    else next[name] = isNumber ? Number(raw) : raw
    onChange(next)
  }

  return (
    <div>
      {fields.map((f) => {
        const current = params[f.name]
        const shown = current ?? ''
        if (f.kind === 'enum') {
          return (
            <label className="field" key={f.name} title={f.description}>
              <span>{f.label}</span>
              <select
                value={String(current ?? f.default ?? '')}
                onChange={(e) => set(f.name, e.target.value, false)}
              >
                {f.options!.map((o) => (
                  <option key={o} value={o}>
                    {o.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </label>
          )
        }
        return (
          <label className="field" key={f.name} title={f.description}>
            <span>{f.label}</span>
            <input
              type={f.kind === 'number' ? 'number' : 'text'}
              step={f.kind === 'number' ? '0.125' : undefined}
              value={String(shown)}
              placeholder={f.default != null ? String(f.default) : ''}
              onChange={(e) => set(f.name, e.target.value, f.kind === 'number')}
            />
          </label>
        )
      })}
    </div>
  )
}

function uom(code: string): string {
  return (
    {
      per_linear_ft: 'ft',
      per_united_in: 'united in',
      per_sqft: 'sq ft',
      each: 'each',
      sheet: 'sheet',
    }[code] ?? code
  )
}
