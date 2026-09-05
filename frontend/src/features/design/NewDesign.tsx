import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, formatCents } from '../../api/client'
import { navigate } from '../../nav'

const STARTER = [
  { kind: 'moulding', params: { face_in: 1.25 } },
  { kind: 'glazing', params: {} },
  { kind: 'mat', params: { border_in: 2.5 } },
  { kind: 'mount', params: { method: 'hinge' } },
  { kind: 'backing', params: { material: 'foamcore' } },
]

export function NewDesign({ onOpen }: { onOpen: (id: number) => void }) {
  const qc = useQueryClient()
  const designs = useQuery({ queryKey: ['designs'], queryFn: api.listDesigns })

  const [name, setName] = useState('')
  const [title, setTitle] = useState('')
  const [width, setWidth] = useState('')
  const [height, setHeight] = useState('')
  const [depth, setDepth] = useState('')
  const [seed, setSeed] = useState(true)

  const create = useMutation({
    mutationFn: () =>
      api.startDesign({
        customer: { name: name.trim() || 'Walk-in' },
        artwork: {
          title: title.trim() || 'Untitled',
          width_in: width.trim(),
          height_in: height.trim(),
          depth_in: depth.trim() || undefined,
        },
        components: seed ? STARTER : [],
      }),
    onSuccess: (design) => {
      qc.invalidateQueries({ queryKey: ['designs'] })
      onOpen(design.id)
    },
  })

  const ready = width.trim() !== '' && height.trim() !== ''

  return (
    <div className="stack">
      <button className="link" onClick={() => navigate('/')}>
        ← home
      </button>
      <h2>Make a Design</h2>

      <div className="home">
        <section className="panel">
          <h3>New design</h3>
          <p className="muted">Measure the artwork and start building a framing specification.</p>

          <label className="field">
            <span>Customer</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Walk-in" />
          </label>
          <label className="field">
            <span>Artwork title</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Untitled"
            />
          </label>
          <div className="field-row">
            <label className="field">
              <span>Width (in)</span>
              <input
                value={width}
                onChange={(e) => setWidth(e.target.value)}
                placeholder="16 1/2"
                inputMode="decimal"
              />
            </label>
            <label className="field">
              <span>Height (in)</span>
              <input
                value={height}
                onChange={(e) => setHeight(e.target.value)}
                placeholder="20"
                inputMode="decimal"
              />
            </label>
            <label className="field">
              <span>Depth (in)</span>
              <input
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
                placeholder="optional"
              />
            </label>
          </div>
          <label className="checkbox">
            <input type="checkbox" checked={seed} onChange={(e) => setSeed(e.target.checked)} />
            Start with a typical component stack
          </label>

          <button
            className="primary"
            disabled={!ready || create.isPending}
            onClick={() => create.mutate()}
          >
            {create.isPending ? 'Creating…' : 'Start design'}
          </button>
          {create.isError && <p className="error">{String((create.error as Error).message)}</p>}
        </section>

        <section className="panel">
          <h3>Designs</h3>
          {designs.isLoading && <p className="muted">Loading…</p>}
          <ul className="design-list">
            {(designs.data ?? []).map((d) => (
              <li key={d.id}>
                <button className="link" onClick={() => onOpen(d.id)}>
                  #{d.id} · {d.artwork_title}
                </button>
                <span className="muted">
                  {d.width_in}″×{d.height_in}″ · {d.status}
                  {d.subtotal_cents != null && ` · ${formatCents(d.subtotal_cents)}`}
                </span>
              </li>
            ))}
            {designs.data?.length === 0 && <li className="muted">No designs yet.</li>}
          </ul>
        </section>
      </div>
    </div>
  )
}
