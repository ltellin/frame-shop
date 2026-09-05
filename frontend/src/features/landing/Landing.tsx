import { navigate } from '../../nav'

const OPTIONS = [
  {
    to: '/design/new',
    glyph: '▧',
    title: 'Make a Design',
    blurb: 'Measure a piece, build its framing spec, and see the price and schematic update live.',
  },
  {
    to: '/customers',
    glyph: '☺',
    title: 'Customers',
    blurb: 'Look up a customer or add a new one.',
  },
  {
    to: '/orders',
    glyph: '❏',
    title: 'Orders',
    blurb: 'Browse orders and the pieces on each one.',
  },
]

export function Landing() {
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
            <span className="landing-blurb">{o.blurb}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
