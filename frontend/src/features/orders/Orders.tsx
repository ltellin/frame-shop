import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { navigate } from '../../nav'

const STATUS_LABEL: Record<string, string> = {
  draft: 'Draft',
  accepted: 'Accepted',
  discarded: 'Discarded',
}

export function Orders() {
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
        <ul className="design-list">
          {(orders.data ?? []).map((o) => (
            <li key={o.id}>
              <button className="link" onClick={() => navigate(`/orders/${o.id}`)}>
                Order #{o.number} · {o.customer_name}
              </button>
              <span className="muted">
                {STATUS_LABEL[o.status] ?? o.status} · {o.design_count}{' '}
                {o.design_count === 1 ? 'piece' : 'pieces'}
                {o.due_date && ` · due ${o.due_date}`}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
