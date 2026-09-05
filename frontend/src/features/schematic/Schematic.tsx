import { useMemo } from 'react'
import { useDesignEditor } from '../../state/designEditor'
import { buildSchematic } from './layout'

const BASE_LABEL: Record<string, string> = {
  art: 'artwork',
  sight: 'sight opening',
  glass: 'glass',
  rabbet: 'frame rabbet',
  outside: 'outside',
}

export function Schematic() {
  const { design, selectedId, select } = useDesignEditor()

  const model = useMemo(
    () => (design?.representations ? buildSchematic(design.representations.exploded) : null),
    [design],
  )

  if (!design) return null

  if (!design.complete || !model) {
    return (
      <section className="panel schematic-panel">
        <div className="panel-head">
          <h3>Schematic</h3>
        </div>
        <p className="muted pad">Enter the piece dimensions to see the schematic.</p>
      </section>
    )
  }

  return (
    <section className="panel schematic-panel">
      <div className="panel-head">
        <h3>Schematic</h3>
        <span className="muted">
          {design.base_width_in}″ × {design.base_height_in}″ {BASE_LABEL[design.base_ref] ?? ''}
        </span>
      </div>

      <svg
        className="schematic"
        viewBox={`0 0 ${model.width} ${model.height}`}
        role="img"
        aria-label="Exploded schematic of the design"
      >
        <defs>
          <pattern
            id="com-hatch"
            patternUnits="userSpaceOnUse"
            width={6}
            height={6}
            patternTransform="rotate(45)"
          >
            <rect width={6} height={6} fill="#fff" fillOpacity={0.55} />
            <line x1={0} y1={0} x2={0} y2={6} stroke="rgba(0,0,0,0.4)" strokeWidth={1.5} />
          </pattern>
        </defs>

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
              {layer.customerSupplied && (
                <polygon
                  points={layer.outline}
                  fill="url(#com-hatch)"
                  stroke="none"
                  pointerEvents="none"
                />
              )}
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
                {layer.labelText}
                {layer.customerSupplied ? " · customer's" : ''}
              </text>
            </g>
          )
        })}
      </svg>
    </section>
  )
}
