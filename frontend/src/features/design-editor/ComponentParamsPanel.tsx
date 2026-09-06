import { useQuery } from '@tanstack/react-query'
import { api, formatCents } from '../../api/client'
import type { ComponentKindMeta, DesignComponent, Product, ProductSpec } from '../../api/types'
import { useDesignEditor } from '../../state/designEditor'
import { fieldsFor } from './paramSchema'

const PROFILE_KINDS = new Set(['moulding', 'fillet'])

export function ComponentParamsPanel() {
  const { design, selectedId, updateParams, setProduct, setProvenance } = useDesignEditor()
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
  const customerSupplied = component.provenance === 'customer'

  // When a real moulding/fillet is picked, its profile defines the face width —
  // the manual field is hidden and the profile shown read-only instead.
  const profile = component.product?.spec
  const profileDriven =
    PROFILE_KINDS.has(component.kind) && profile?.face_width_in != null && !customerSupplied
  const hiddenFields = profileDriven ? new Set(['face_in']) : undefined

  return (
    <aside className="panel">
      <h3>{meta?.label ?? component.kind}</h3>

      <div className="provenance-toggle">
        <button
          className={!customerSupplied ? 'seg active' : 'seg'}
          onClick={() => setProvenance(component.id, 'shop')}
        >
          Shop supplied
        </button>
        <button
          className={customerSupplied ? 'seg active' : 'seg'}
          onClick={() => setProvenance(component.id, 'customer')}
        >
          Customer supplied
        </button>
      </div>

      {customerSupplied ? (
        <p className="muted">Customer-supplied — a handling charge applies, no material cost.</p>
      ) : (
        meta?.consumes_product && (
          <ProductPicker
            kind={component.kind}
            value={component.product_id}
            onChange={(pid) => setProduct(component.id, pid)}
          />
        )
      )}

      {profileDriven && <ProfileReadout spec={profile!} />}

      {meta && (
        <ParamFields
          meta={meta}
          component={component}
          hiddenFields={hiddenFields}
          onChange={(params) => updateParams(component.id, params)}
        />
      )}
    </aside>
  )
}

function ProfileReadout({ spec }: { spec: ProductSpec }) {
  const rows: [string, string][] = []
  if (spec.face_width_in != null) rows.push(['Face width', `${spec.face_width_in}″`])
  if (spec.rabbet_height_in != null) rows.push(['Rabbet depth', `${spec.rabbet_height_in}″`])
  if (spec.material) rows.push(['Material', String(spec.material)])
  if (spec.finish) rows.push(['Finish', String(spec.finish)])
  return (
    <dl className="profile-readout">
      {rows.map(([k, v]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd>{v}</dd>
        </div>
      ))}
    </dl>
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
            {p.name} · {p.vendor_name}
            {p.spec?.face_width_in != null ? ` · ${p.spec.face_width_in}″ face` : ''} ·{' '}
            {formatCents(p.unit_price_cents)}/{uom(p.price_uom)}
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
  hiddenFields,
  onChange,
}: {
  meta: ComponentKindMeta
  component: DesignComponent
  hiddenFields?: Set<string>
  onChange: (params: Record<string, unknown>) => void
}) {
  const fields = fieldsFor(meta).filter((f) => !hiddenFields?.has(f.name))
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
