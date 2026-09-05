import { useEffect, useState } from 'react'
import './App.css'
import { navigate } from './nav'
import { Customers } from './features/customers/Customers'
import { NewDesign } from './features/design/NewDesign'
import { DesignEditor } from './features/design-editor/DesignEditor'
import { Landing } from './features/landing/Landing'
import { Orders } from './features/orders/Orders'

// Minimal hash routing — no router library (see frontend/CLAUDE.md).
type Route =
  | { name: 'landing' }
  | { name: 'new-design' }
  | { name: 'design'; id: number }
  | { name: 'customers' }
  | { name: 'orders' }

function parseHash(): Route {
  const h = window.location.hash.replace(/^#/, '')
  const design = h.match(/^\/designs\/(\d+)/)
  if (design) return { name: 'design', id: Number(design[1]) }
  if (h === '/design/new') return { name: 'new-design' }
  if (h === '/customers') return { name: 'customers' }
  if (h === '/orders') return { name: 'orders' }
  return { name: 'landing' }
}

export default function App() {
  const [route, setRoute] = useState<Route>(parseHash)

  useEffect(() => {
    const onHash = () => setRoute(parseHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const openDesign = (id: number) => navigate(`/designs/${id}`)

  return (
    <div className="app">
      <header className="app-bar">
        <button className="brand" onClick={() => navigate('/')}>
          ▦ Frame Shop
        </button>
        <span className="tag">prototype</span>
      </header>
      <main>
        {route.name === 'landing' && <Landing />}
        {route.name === 'new-design' && <NewDesign onOpen={openDesign} />}
        {route.name === 'design' && (
          <DesignEditor
            key={route.id}
            designId={route.id}
            onExit={() => navigate('/design/new')}
          />
        )}
        {route.name === 'customers' && <Customers />}
        {route.name === 'orders' && <Orders onOpenDesign={openDesign} />}
      </main>
    </div>
  )
}
