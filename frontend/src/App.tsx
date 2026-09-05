import { useEffect, useState } from 'react'
import './App.css'
import { navigate } from './nav'
import { Customers } from './features/customers/Customers'
import { NewDesignGate } from './features/design/NewDesignGate'
import { DesignEditor } from './features/design-editor/DesignEditor'
import { Landing } from './features/landing/Landing'
import { OrderDetail } from './features/orders/OrderDetail'
import { Orders } from './features/orders/Orders'

// Minimal hash routing — no router library (see frontend/CLAUDE.md).
type Route =
  | { name: 'landing' }
  | { name: 'new-design'; order?: number }
  | { name: 'design'; id: number; order?: number }
  | { name: 'customers' }
  | { name: 'orders' }
  | { name: 'order'; id: number }

function parseHash(): Route {
  const raw = window.location.hash.replace(/^#/, '')
  const [path, queryStr] = raw.split('?')
  const query = new URLSearchParams(queryStr)
  const order = query.has('order') ? Number(query.get('order')) : undefined

  const design = path.match(/^\/designs\/(\d+)/)
  if (design) return { name: 'design', id: Number(design[1]), order }
  const orderPage = path.match(/^\/orders\/(\d+)/)
  if (orderPage) return { name: 'order', id: Number(orderPage[1]) }
  if (path === '/design/new') return { name: 'new-design', order }
  if (path === '/customers') return { name: 'customers' }
  if (path === '/orders') return { name: 'orders' }
  return { name: 'landing' }
}

export default function App() {
  const [route, setRoute] = useState<Route>(parseHash)

  useEffect(() => {
    const onHash = () => setRoute(parseHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

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
        {route.name === 'new-design' && <NewDesignGate attachOrderId={route.order} />}
        {route.name === 'design' && (
          <DesignEditor key={route.id} designId={route.id} attachOrderId={route.order} />
        )}
        {route.name === 'customers' && <Customers />}
        {route.name === 'orders' && <Orders />}
        {route.name === 'order' && <OrderDetail key={route.id} orderId={route.id} />}
      </main>
    </div>
  )
}
