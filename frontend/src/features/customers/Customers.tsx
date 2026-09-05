import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../api/client'
import { navigate } from '../../nav'

export function Customers() {
  const qc = useQueryClient()
  const customers = useQuery({ queryKey: ['customers'], queryFn: api.listCustomers })

  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')

  const create = useMutation({
    mutationFn: () =>
      api.createCustomer({
        name: name.trim(),
        phone: phone.trim() || undefined,
        email: email.trim() || undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['customers'] })
      setName('')
      setPhone('')
      setEmail('')
    },
  })

  return (
    <div className="stack">
      <button className="link" onClick={() => navigate('/')}>
        ← home
      </button>
      <h2>Customers</h2>

      <div className="home">
        <section className="panel">
          <h3>Add a customer</h3>
          <label className="field">
            <span>Name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <div className="field-row">
            <label className="field">
              <span>Phone</span>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </label>
            <label className="field">
              <span>Email</span>
              <input value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
          </div>
          <button
            className="primary"
            disabled={name.trim() === '' || create.isPending}
            onClick={() => create.mutate()}
          >
            {create.isPending ? 'Saving…' : 'Add customer'}
          </button>
          {create.isError && <p className="error">{String((create.error as Error).message)}</p>}
        </section>

        <section className="panel">
          <h3>All customers</h3>
          {customers.isLoading && <p className="muted">Loading…</p>}
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th className="num">Orders</th>
              </tr>
            </thead>
            <tbody>
              {(customers.data ?? []).map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.phone ?? '—'}</td>
                  <td>{c.email ?? '—'}</td>
                  <td className="num">{c.order_count}</td>
                </tr>
              ))}
              {customers.data?.length === 0 && (
                <tr>
                  <td colSpan={4} className="muted">
                    No customers yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}
