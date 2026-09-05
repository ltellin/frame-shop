import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { navigate } from '../../nav'

const STATUS_LABEL: Record<string, string> = {
  draft: 'Draft',
  held: 'On hold',
  quoted: 'Quoted',
  accepted: 'Accepted',
  discarded: 'Discarded',
}

export function Orders({ onOpenDesign }: { onOpenDesign: (id: number) => void }) {
  const orders = useQuery({ queryKey: ['orders'], queryFn: api.listOrders })

  return (
    <div className="stack">
      <button className="link" onClick={() => navigate('/')}>
        ← home
      </button>
      <h2>Orders</h2>

      <section className="panel">
        {orders.isLoading && <p className="muted">Loading…</p>}
        {orders.data?.length === 0 && <p className="muted">No orders yet.</p>}
        <ul className="order-list">
          {(orders.data ?? []).map((o) => (
            <li key={o.id}>
              <OrderRow orderId={o.id} onOpenDesign={onOpenDesign} summary={o} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

function OrderRow({
  orderId,
  summary,
  onOpenDesign,
}: {
  orderId: number
  summary: { number: number; customer_name: string; status: string; piece_count: number }
  onOpenDesign: (id: number) => void
}) {
  const detail = useQuery({ queryKey: ['order', orderId], queryFn: () => api.getOrder(orderId) })

  return (
    <div className="order-row">
      <div className="order-head">
        <strong>Order #{summary.number}</strong>
        <span className="muted">
          {summary.customer_name} · {STATUS_LABEL[summary.status] ?? summary.status} ·{' '}
          {summary.piece_count} {summary.piece_count === 1 ? 'piece' : 'pieces'}
        </span>
      </div>
      <ul className="order-designs">
        {(detail.data?.designs ?? []).map((d) => (
          <li key={d.id}>
            <button className="link" onClick={() => onOpenDesign(d.id)}>
              #{d.id} · {d.artwork_title}
            </button>
            <span className="muted">{STATUS_LABEL[d.status] ?? d.status}</span>
          </li>
        ))}
        {detail.data?.designs.length === 0 && <li className="muted">No designs on this order.</li>}
      </ul>
    </div>
  )
}
