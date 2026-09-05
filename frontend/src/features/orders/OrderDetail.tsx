import { useQuery } from '@tanstack/react-query'
import { api, formatCents } from '../../api/client'
import { navigate } from '../../nav'

const STATUS_LABEL: Record<string, string> = {
  draft: 'Draft',
  accepted: 'Accepted',
  discarded: 'Discarded',
}

export function OrderDetail({ orderId }: { orderId: number }) {
  const order = useQuery({ queryKey: ['order', orderId], queryFn: () => api.getOrder(orderId) })

  if (order.isLoading) return <p className="pad">Loading…</p>
  if (!order.data) return <p className="pad error">Order not found.</p>
  const o = order.data

  const total = o.designs.reduce((sum, d) => sum + (d.subtotal_cents ?? 0), 0)

  return (
    <div className="stack">
      <button className="link" onClick={() => navigate('/orders')}>
        ← orders
      </button>
      <h2>
        Order #{o.number} <span className="muted">· {o.customer_name}</span>
      </h2>
      <p className="muted">
        {STATUS_LABEL[o.status] ?? o.status}
        {o.due_date && ` · due ${o.due_date}`}
        {o.po_number && ` · PO ${o.po_number}`}
      </p>

      <section className="panel">
        <div className="panel-head">
          <h3>Pieces ({o.designs.length})</h3>
          <button onClick={() => navigate(`/design/new?order=${o.id}`)}>+ add another design</button>
        </div>
        <ul className="design-list">
          {o.designs.map((d) => (
            <li key={d.id}>
              <button className="link" onClick={() => navigate(`/designs/${d.id}`)}>
                #{d.id} · {d.art_title || d.type.replace(/_/g, ' ')}
              </button>
              <span className="muted">
                {d.base_width_in != null && `${d.base_width_in}″×${d.base_height_in}″ · `}
                {STATUS_LABEL[d.status] ?? d.status}
                {d.subtotal_cents != null && ` · ${formatCents(d.subtotal_cents)}`}
              </span>
            </li>
          ))}
          {o.designs.length === 0 && <li className="muted">No pieces yet.</li>}
        </ul>
        {total > 0 && (
          <p className="order-total">
            Subtotal <strong>{formatCents(total)}</strong>
          </p>
        )}
      </section>
    </div>
  )
}
