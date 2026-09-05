import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { useDesignEditor } from '../../state/designEditor'
import { roleColor } from '../../theme'

export function ComponentList() {
  const { design, selectedId, select, addComponent, removeComponent, moveComponent } =
    useDesignEditor()
  const kinds = useQuery({ queryKey: ['component-kinds'], queryFn: api.componentKinds })

  if (!design) return null
  const components = design.components

  return (
    <section className="panel">
      <div className="panel-head">
        <h3>Components · outside → inside</h3>
        {design.editable && (
          <select
            value=""
            onChange={(e) => {
              const k = kinds.data?.find((m) => m.key === e.target.value)
              if (k) addComponent(k.key, k.default_layer_role)
              e.target.value = ''
            }}
          >
            <option value="">+ add…</option>
            {(kinds.data ?? []).map((k) => (
              <option key={k.key} value={k.key}>
                {k.label}
              </option>
            ))}
          </select>
        )}
      </div>

      <ol className="component-list">
        {components.map((c, i) => (
          <li
            key={c.id}
            className={c.id === selectedId ? 'component selected' : 'component'}
            onClick={() => select(c.id)}
          >
            <span className="swatch" style={{ background: roleColor(c.layer_role) }} />
            <span className="component-label">
              <strong>{labelFor(c.kind)}</strong>
              <small>{c.product?.name ?? summarize(c.params)}</small>
            </span>
            {design.editable && (
              <span className="component-actions" onClick={(e) => e.stopPropagation()}>
                <button disabled={i === 0} onClick={() => moveComponent(c.id, -1)} title="Move out">
                  ↑
                </button>
                <button
                  disabled={i === components.length - 1}
                  onClick={() => moveComponent(c.id, 1)}
                  title="Move in"
                >
                  ↓
                </button>
                <button onClick={() => removeComponent(c.id)} title="Remove">
                  ✕
                </button>
              </span>
            )}
          </li>
        ))}
        {components.length === 0 && <li className="muted">No components yet — add one above.</li>}
      </ol>
    </section>
  )
}

function labelFor(kind: string): string {
  return kind.charAt(0).toUpperCase() + kind.slice(1)
}

function summarize(params: Record<string, unknown>): string {
  const parts = Object.entries(params).map(([k, v]) => `${k.replace(/_in$/, '')}: ${v}`)
  return parts.join(', ') || '—'
}
