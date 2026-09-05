import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { navigate } from '../../nav'

const BASE_LABEL: Record<string, string> = {
  art: 'Art size',
  sight: 'Sight size',
  glass: 'Glass size',
  rabbet: 'Frame rabbet',
  outside: 'Outside size',
}

// The first step of "Make a Design": pick what you're making and enter the
// dimensions it's built around. Filling both dimensions creates the autosaved
// draft and drops you into the editor (Gmail-style — from there, leaving keeps
// the draft).
export function NewDesignGate({ attachOrderId }: { attachOrderId?: number }) {
  const types = useQuery({ queryKey: ['design-types'], queryFn: api.designTypes })

  const [type, setType] = useState('framing')
  const [width, setWidth] = useState('')
  const [height, setHeight] = useState('')
  const [seed, setSeed] = useState(true)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const startedRef = useRef(false)

  const typeMeta = types.data?.find((t) => t.key === type)
  const baseRef = typeMeta?.base_ref ?? 'sight'
  const ready = width.trim() !== '' && height.trim() !== ''

  const start = async () => {
    if (startedRef.current || !ready) return
    startedRef.current = true
    setStarting(true)
    setError(null)
    try {
      const design = await api.startDesign({
        type,
        base_width_in: width.trim(),
        base_height_in: height.trim(),
        seed_starter: seed,
      })
      navigate(`/designs/${design.id}${attachOrderId ? `?order=${attachOrderId}` : ''}`)
    } catch (e) {
      startedRef.current = false
      setStarting(false)
      setError(String((e as Error).message ?? e))
    }
  }

  // Auto-start a short beat after both dimensions are filled.
  useEffect(() => {
    if (!ready || startedRef.current) return
    const t = setTimeout(start, 700)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, width, height, type, seed])

  return (
    <div className="stack">
      <button className="link" onClick={() => navigate('/')}>
        ← home
      </button>
      <h2>Make a Design</h2>

      <section className="panel gate">
        <label className="field">
          <span>What are you making?</span>
          <select value={type} onChange={(e) => setType(e.target.value)}>
            {(types.data ?? []).map((t) => (
              <option key={t.key} value={t.key}>
                {t.label}
              </option>
            ))}
          </select>
        </label>

        <div className="field-row">
          <label className="field">
            <span>{BASE_LABEL[baseRef] ?? 'Width'} — width (in)</span>
            <input
              autoFocus
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
              onKeyDown={(e) => e.key === 'Enter' && start()}
            />
          </label>
        </div>

        <label className="checkbox">
          <input type="checkbox" checked={seed} onChange={(e) => setSeed(e.target.checked)} />
          Start with a typical component stack
        </label>

        <button className="primary" disabled={!ready || starting} onClick={start}>
          {starting ? 'Starting…' : 'Start design →'}
        </button>
        {attachOrderId && <p className="muted">Will be added to order #{attachOrderId}.</p>}
        {error && <p className="error">{error}</p>}
      </section>
    </div>
  )
}
