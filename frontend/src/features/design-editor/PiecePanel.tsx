import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { useDesignEditor } from '../../state/designEditor'
import { ImagesStrip } from './ImagesStrip'

const BASE_LABEL: Record<string, string> = {
  art: 'Art size',
  sight: 'Sight size',
  glass: 'Glass size',
  rabbet: 'Frame rabbet',
  outside: 'Outside size',
}

const ART_TYPES = ['print_photo', 'canvas', 'works_on_paper', 'textile', 'object_3d']

export function PiecePanel() {
  const { design, patchFields, saving } = useDesignEditor()
  const types = useQuery({ queryKey: ['design-types'], queryFn: api.designTypes })

  const [w, setW] = useState('')
  const [h, setH] = useState('')

  useEffect(() => {
    setW(design?.base_width_in != null ? String(design.base_width_in) : '')
    setH(design?.base_height_in != null ? String(design.base_height_in) : '')
  }, [design?.id, design?.base_width_in, design?.base_height_in])

  if (!design) return null
  const editable = design.editable
  const typeMeta = types.data?.find((t) => t.key === design.type)
  const baseLabel = BASE_LABEL[design.base_ref] ?? 'Size'

  const commitSize = () => {
    const patch: Record<string, unknown> = {}
    if (w.trim() && w.trim() !== String(design.base_width_in ?? '')) patch.base_width_in = w.trim()
    if (h.trim() && h.trim() !== String(design.base_height_in ?? '')) patch.base_height_in = h.trim()
    if (Object.keys(patch).length) patchFields(patch)
  }

  return (
    <section className="panel piece-panel">
      <div className="panel-head">
        <h3>Piece</h3>
        <span className="muted">{saving ? 'saving…' : 'saved'}</span>
      </div>

      <label className="field">
        <span>What are you making?</span>
        <select
          value={design.type}
          disabled={!editable}
          onChange={(e) => patchFields({ type: e.target.value })}
        >
          {(types.data ?? []).map((t) => (
            <option key={t.key} value={t.key}>
              {t.label}
            </option>
          ))}
        </select>
      </label>

      <div className="field-row">
        <label className="field">
          <span>{baseLabel} — width (in)</span>
          <input
            value={w}
            disabled={!editable}
            onChange={(e) => setW(e.target.value)}
            onBlur={commitSize}
            onKeyDown={(e) => e.key === 'Enter' && commitSize()}
            inputMode="decimal"
          />
        </label>
        <label className="field">
          <span>Height (in)</span>
          <input
            value={h}
            disabled={!editable}
            onChange={(e) => setH(e.target.value)}
            onBlur={commitSize}
            onKeyDown={(e) => e.key === 'Enter' && commitSize()}
            inputMode="decimal"
          />
        </label>
      </div>

      {typeMeta?.has_art && (
        <details className="art-block" open={!!design.art.title}>
          <summary>Artwork details</summary>
          <label className="field">
            <span>Title</span>
            <input
              defaultValue={design.art.title ?? ''}
              disabled={!editable}
              onBlur={(e) => patchFields({ art: { title: e.target.value } })}
            />
          </label>
          <label className="field">
            <span>Type</span>
            <select
              value={design.art.art_type ?? ''}
              disabled={!editable}
              onChange={(e) => patchFields({ art: { art_type: e.target.value || null } })}
            >
              <option value="">—</option>
              {ART_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Notes</span>
            <input
              defaultValue={design.art.notes ?? ''}
              disabled={!editable}
              onBlur={(e) => patchFields({ art: { notes: e.target.value } })}
            />
          </label>
        </details>
      )}

      <label className="field inline-qty">
        <span>Quantity</span>
        <input
          type="number"
          min={1}
          value={design.quantity}
          disabled={!editable}
          onChange={(e) => patchFields({ quantity: Math.max(1, Number(e.target.value) || 1) })}
        />
      </label>

      <ImagesStrip />
    </section>
  )
}
