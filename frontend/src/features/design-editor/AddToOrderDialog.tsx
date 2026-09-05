import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'

export function AddToOrderDialog({
  designId,
  onClose,
  onDone,
  onReload,
}: {
  designId: number
  onClose: () => void
  onDone: (orderId: number) => void
  onReload: () => Promise<void>
}) {
  const customers = useQuery({ queryKey: ['customers'], queryFn: api.listCustomers })

  const [mode, setMode] = useState<'existing' | 'new'>('existing')
  const [search, setSearch] = useState('')
  const [customerId, setCustomerId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const matches = useMemo(() => {
    const q = search.trim().toLowerCase()
    const list = customers.data ?? []
    return q ? list.filter((c) => c.name.toLowerCase().includes(q)) : list
  }, [customers.data, search])

  const canSubmit =
    (mode === 'existing' && customerId != null) || (mode === 'new' && name.trim() !== '')

  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      const res = await api.addToOrder(designId, {
        customer_id: mode === 'existing' ? customerId! : undefined,
        customer:
          mode === 'new'
            ? { name: name.trim(), phone: phone.trim() || undefined, email: email.trim() || undefined }
            : undefined,
        due_date: dueDate || undefined,
      })
      await onReload()
      onDone(res.order_id)
    } catch (e) {
      setError(String((e as Error).message ?? e))
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>Add to an order</h3>

        <div className="provenance-toggle">
          <button
            className={mode === 'existing' ? 'seg active' : 'seg'}
            onClick={() => setMode('existing')}
          >
            Existing customer
          </button>
          <button className={mode === 'new' ? 'seg active' : 'seg'} onClick={() => setMode('new')}>
            New customer
          </button>
        </div>

        {mode === 'existing' ? (
          <>
            <label className="field">
              <span>Search</span>
              <input value={search} onChange={(e) => setSearch(e.target.value)} autoFocus />
            </label>
            <ul className="picker-list">
              {matches.map((c) => (
                <li
                  key={c.id}
                  className={c.id === customerId ? 'selected' : ''}
                  onClick={() => setCustomerId(c.id)}
                >
                  {c.name}
                  <span className="muted">
                    {c.phone ?? ''} {c.order_count > 0 ? `· ${c.order_count} orders` : ''}
                  </span>
                </li>
              ))}
              {matches.length === 0 && <li className="muted">No matches</li>}
            </ul>
          </>
        ) : (
          <>
            <label className="field">
              <span>Name</span>
              <input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
            </label>
            <div className="field-row">
              <label className="field">
                <span>Phone</span>
                <input value={phone} onChange={(e) => setPhone(e.target.value)} />
              </label>
              <label className="field">
                <span>Email</span>
                <input value={email} onChange={(e) => setEmail(e.target.value)} />
              </label>
            </div>
          </>
        )}

        <label className="field">
          <span>Due date (optional)</span>
          <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
        </label>

        {error && <p className="error">{error}</p>}

        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button className="primary" disabled={!canSubmit || busy} onClick={submit}>
            {busy ? 'Adding…' : 'Add to order'}
          </button>
        </div>
      </div>
    </div>
  )
}
