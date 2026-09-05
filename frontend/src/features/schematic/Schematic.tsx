import { useMemo } from 'react'
import { useDesignEditor } from '../../state/designEditor'
import { buildSchematic } from './layout'

export function Schematic() {
  const { design, selectedId, select } = useDesignEditor()

  const model = useMemo(
    () => (design ? buildSchematic(design.representations.exploded) : null),
    [design],
  )

  if (!design || !model) return null

  return (
    <section className="panel schematic-panel">
      <div className="panel-head">
        <h3>Schematic</h3>
        <span className="muted">
          {design.artwork.width_in}″ × {design.artwork.height_in}″ artwork
        </span>
      </div>

      <svg
        className="schematic"
        viewBox={`0 0 ${model.width} ${model.height}`}
        role="img"
        aria-label="Exploded schematic of the framing design"
      >
        {/* connector spine between layer corners */}
        <polyline
          points={model.layers.map((l) => l.leader.split(' ')[0]).join(' ')}
          fill="none"
          stroke="var(--hair)"
          strokeWidth={1}
          strokeDasharray="3 3"
        />

        {model.layers.map((layer) => {
          const active = layer.componentId != null && layer.componentId === selectedId
          return (
            <g
              key={`${layer.kind}-${layer.z}`}
              className={layer.componentId != null ? 'layer clickable' : 'layer'}
              onClick={() => layer.componentId != null && select(layer.componentId)}
            >
              <polyline points={layer.leader} fill="none" stroke="var(--hair)" strokeWidth={1} />
              <polygon
                points={layer.outline}
                fill={layer.color}
                fillOpacity={layer.kind === 'glazing' ? 0.4 : 0.92}
                stroke={active ? 'var(--accent)' : 'rgba(0,0,0,0.35)'}
                strokeWidth={active ? 3 : 1}
              />
              {layer.opening && (
                <polygon
                  points={layer.opening}
                  fill="#fff"
                  fillOpacity={0.16}
                  stroke="rgba(0,0,0,0.25)"
                  strokeWidth={1}
                />
              )}
              <text
                x={layer.labelAnchor.x}
                y={layer.labelAnchor.y}
                dominantBaseline="middle"
                className={active ? 'layer-label active' : 'layer-label'}
              >
                {layer.label}
              </text>
            </g>
          )
        })}
      </svg>

      {design.warnings.length > 0 && (
        <ul className="notes warn">
          {design.warnings.map((w, i) => (
            <li key={i}>⚠ {w}</li>
          ))}
        </ul>
      )}
    </section>
  )
}
