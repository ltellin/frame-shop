import { useEffect, useState } from 'react'
import './App.css'
import { DesignEditor } from './features/design-editor/DesignEditor'
import { Home } from './features/home/Home'

// Minimal hash routing: #/ = home, #/designs/:id = editor.
function readHash(): number | null {
  const m = window.location.hash.match(/^#\/designs\/(\d+)/)
  return m ? Number(m[1]) : null
}

export default function App() {
  const [designId, setDesignId] = useState<number | null>(readHash)

  useEffect(() => {
    const onHash = () => setDesignId(readHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const open = (id: number) => {
    window.location.hash = `#/designs/${id}`
    setDesignId(id)
  }
  const exit = () => {
    window.location.hash = '#/'
    setDesignId(null)
  }

  return (
    <div className="app">
      <header className="app-bar">
        <span className="brand">▦ Frame Shop</span>
        <span className="tag">prototype · design editor</span>
      </header>
      <main>
        {designId == null ? (
          <Home onOpen={open} />
        ) : (
          <DesignEditor key={designId} designId={designId} onExit={exit} />
        )}
      </main>
    </div>
  )
}
