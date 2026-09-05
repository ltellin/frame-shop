import { formatCents } from '../../api/client'
import { useDesignEditor } from '../../state/designEditor'

export function PricePanel() {
  const { design, saving } = useDesignEditor()
  if (!design) return null
  const { price } = design

  if (!price) {
    return (
      <section className="panel price-panel">
        <div className="panel-head">
          <h3>Price</h3>
        </div>
        <p className="muted">Enter the piece dimensions to see pricing.</p>
      </section>
    )
  }

  return (
    <section className="panel price-panel">
      <div className="panel-head">
        <h3>Price</h3>
        <span className={saving ? 'badge saving' : 'badge'}>{saving ? 'pricing…' : 'live'}</span>
      </div>

      <table className="price-table">
        <tbody>
          {price.lines.map((line, i) => (
            <tr key={i}>
              <td>
                {line.label}
                <small>{line.detail}</small>
              </td>
              <td className="amount">{formatCents(line.amount_cents)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td>Subtotal</td>
            <td className="amount">{formatCents(price.subtotal_cents)}</td>
          </tr>
        </tfoot>
      </table>

      <p className="profile-note">
        pricing profile: <code>{price.profile_id}</code> v{price.profile_version} · placeholder
        rules
      </p>

      {price.notes.length > 0 && (
        <ul className="notes">
          {price.notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      )}
    </section>
  )
}
