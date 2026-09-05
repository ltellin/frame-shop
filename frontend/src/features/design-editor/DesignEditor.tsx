import { useState } from 'react'
import { api } from '../../api/client'
import { DesignEditorProvider, useDesignEditor } from '../../state/designEditor'
import { navigate } from '../../nav'
import { Schematic } from '../schematic/Schematic'
import { AddToOrderDialog } from './AddToOrderDialog'
import { ComponentList } from './ComponentList'
import { ComponentParamsPanel } from './ComponentParamsPanel'
import { PiecePanel } from './PiecePanel'
import { PricePanel } from './PricePanel'
import { SizeReadout } from './SizeReadout'

export function DesignEditor({
  designId,
  attachOrderId,
}: {
  designId: number
  attachOrderId?: number
}) {
  return (
    <DesignEditorProvider designId={designId}>
      <EditorBody attachOrderId={attachOrderId} />
    </DesignEditorProvider>
  )
}

function EditorBody({ attachOrderId }: { attachOrderId?: number }) {
  const { design, loading, error, saving, patchFields, reload } = useDesignEditor()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [attaching, setAttaching] = useState(false)

  if (loading) return <p className="pad">Loading design…</p>
  if (!design) return <p className="pad error">{error ?? 'Design not found.'}</p>

  const onOrder = design.order_id != null
  const locked = design.status !== 'draft'

  const attachToKnownOrder = async () => {
    setAttaching(true)
    try {
      const res = await api.addToOrder(design.id, { order_id: attachOrderId })
      navigate(`/orders/${res.order_id}`)
    } finally {
      setAttaching(false)
    }
  }

  return (
    <div className="editor">
      <header className="editor-head">
        <div>
          <button className="link" onClick={() => navigate('/')}>
            ← home
          </button>
          <h2>
            {design.art.title || design.name} <span className="muted">#{design.id}</span>
          </h2>
          <p className="muted">
            {design.status === 'draft' ? (
              <>{saving ? 'saving…' : 'draft · saved'}</>
            ) : (
              <span className={`status-pill status-${design.status}`}>{design.status}</span>
            )}
            {onOrder && <> · on order #{design.order_id}</>}
            {design.quantity > 1 && <> · ×{design.quantity}</>}
          </p>
        </div>
        {!locked && !onOrder && (
          <div className="status-controls">
            {attachOrderId ? (
              <button className="primary" disabled={attaching} onClick={attachToKnownOrder}>
                {attaching ? 'Adding…' : `Add to order #${attachOrderId}`}
              </button>
            ) : (
              <button className="primary" onClick={() => setDialogOpen(true)}>
                Add to order
              </button>
            )}
            <button
              className="danger"
              onClick={() => patchFields({ status: 'discarded' }).then(() => navigate('/'))}
            >
              Discard
            </button>
          </div>
        )}
        {onOrder && (
          <div className="status-controls">
            <button onClick={() => navigate(`/orders/${design.order_id}`)}>View order</button>
          </div>
        )}
      </header>

      {error && <p className="error banner">{error}</p>}
      {design.warnings.map((w, i) => (
        <p key={i} className="warn-banner">
          ⚠ {w}
        </p>
      ))}

      <div className="editor-grid">
        <div className="col">
          <PiecePanel />
          <ComponentList />
          <ComponentParamsPanel />
        </div>
        <div className="col">
          <Schematic />
          <SizeReadout />
        </div>
        <div className="col">
          <PricePanel />
        </div>
      </div>

      {dialogOpen && (
        <AddToOrderDialog
          designId={design.id}
          onClose={() => setDialogOpen(false)}
          onDone={(orderId) => navigate(`/orders/${orderId}`)}
          onReload={reload}
        />
      )}
    </div>
  )
}
