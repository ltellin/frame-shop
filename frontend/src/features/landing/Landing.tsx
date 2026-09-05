import { useQuery } from '@tanstack/react-query'
import { api, formatCents } from '../../api/client'
import { navigate } from '../../nav'

const OPTIONS = [
  { to: '/design/new', glyph: '▧', title: 'Make a Design' },
  { to: '/customers', glyph: '☺', title: 'Customers' },
  { to: '/orders', glyph: '❏', title: 'Orders' },
]

export function Landing() {
  const drafts = useQuery({
    queryKey: ['designs', 'loose'],
    queryFn: () => api.listDesigns({ loose: true }),
  })

  return (
    <div className="landing">
      <h1>What would you like to do?</h1>
      <div className="landing-grid">
        {OPTIONS.map((o) => (
          <button key={o.to} className="landing-card" onClick={() => navigate(o.to)}>
            <span className="landing-glyph" aria-hidden>
              {o.glyph}
            </span>
            <span className="landing-title">{o.title}</span>
          </button>
        ))}
      </div>

      {(drafts.data?.length ?? 0) > 0 && (
        <section className="panel drafts">
          <h3>Drafts</h3>
          <ul className="design-list">
            {drafts.data!.map((d) => (
              <li key={d.id}>
                <button className="link" onClick={() => navigate(`/designs/${d.id}`)}>
                  #{d.id} · {d.name}
                </button>
                <span className="muted">
                  {d.type.replace(/_/g, ' ')}
                  {d.base_width_in != null && ` · ${d.base_width_in}″×${d.base_height_in}″`}
                  {d.subtotal_cents != null && ` · ${formatCents(d.subtotal_cents)}`}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
