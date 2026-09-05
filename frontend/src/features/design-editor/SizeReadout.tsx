import { useDesignEditor } from '../../state/designEditor'

export function SizeReadout() {
  const { design } = useDesignEditor()
  if (!design?.summary) return null
  const s = design.summary
  return (
    <div className="size-readout">
      <div>
        <span className="muted">Finished size</span>
        <strong>
          {round(s.finished_width_in)}″ × {round(s.finished_height_in)}″
        </strong>
      </div>
      <div>
        <span className="muted">United inches</span>
        <strong>{round(s.united_in)}″</strong>
      </div>
      {s.quantity > 1 && (
        <div>
          <span className="muted">Quantity</span>
          <strong>×{s.quantity}</strong>
        </div>
      )}
    </div>
  )
}

function round(n: number): number {
  return Math.round(n * 100) / 100
}
