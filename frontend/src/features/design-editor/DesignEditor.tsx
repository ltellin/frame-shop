import { DesignEditorProvider, useDesignEditor } from '../../state/designEditor'
import { Schematic } from '../schematic/Schematic'
import { ComponentList } from './ComponentList'
import { ComponentParamsPanel } from './ComponentParamsPanel'
import { PricePanel } from './PricePanel'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  held: 'On hold',
  quoted: 'Quoted',
  accepted: 'Accepted',
  discarded: 'Discarded',
}

export function DesignEditor({ designId, onExit }: { designId: number; onExit: () => void }) {
  return (
    <DesignEditorProvider designId={designId}>
      <EditorBody onExit={onExit} />
    </DesignEditorProvider>
  )
}

function EditorBody({ onExit }: { onExit: () => void }) {
  const { design, loading, error, saving, setStatus } = useDesignEditor()

  if (loading) return <p className="pad">Loading design…</p>
  if (!design) return <p className="pad error">{error ?? 'Design not found.'}</p>

  return (
    <div className="editor">
      <header className="editor-head">
        <div>
          <button className="link" onClick={onExit}>
            ← all designs
          </button>
          <h2>
            {design.name} <span className="muted">#{design.id}</span>
          </h2>
          <p className="muted">
            Order #{design.order_id} · “{design.artwork.title}” · v{design.version}
            {saving && ' · saving…'}
          </p>
        </div>
        <div className="status-controls">
          <span className={`status-pill status-${design.status}`}>
            {STATUS_LABELS[design.status] ?? design.status}
          </span>
          {design.status !== 'accepted' && design.status !== 'discarded' && (
            <>
              {design.status !== 'draft' && (
                <button onClick={() => setStatus('draft')}>Move to draft</button>
              )}
              {design.status !== 'held' && <button onClick={() => setStatus('held')}>Hold</button>}
              {design.status !== 'quoted' && (
                <button onClick={() => setStatus('quoted')}>Save as quote</button>
              )}
              <button className="danger" onClick={() => setStatus('discarded')}>
                Discard
              </button>
            </>
          )}
        </div>
      </header>

      {error && <p className="error banner">{error}</p>}

      <div className="editor-grid">
        <div className="col">
          <ComponentList />
          <ComponentParamsPanel />
        </div>
        <div className="col">
          <Schematic />
        </div>
        <div className="col">
          <PricePanel />
        </div>
      </div>
    </div>
  )
}
