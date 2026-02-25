import { useEffect, useState } from 'react'
import Login from './components/Login'
import RequestList from './components/RequestList'
import { api } from './api/client'
import { User } from './types'

function App() {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    api.get('/auth/me')
      .then(res => setUser(res.data))
      .catch(() => setUser(null))
  }, [])

  const handleLogin = (user: User) => setUser(user)
  const handleLogout = () => {
    api.post('/auth/logout').then(() => setUser(null))
  }

  if (!user) return <Login onLogin={handleLogin} />

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Заявки в ремонтную службу</h1>
        <div>
          Вы вошли как <strong>{user.name}</strong> ({user.role})
          <button onClick={handleLogout} style={{ marginLeft: '1rem' }}>Выйти</button>
        </div>
      </div>
      <RequestList user={user} />
    </div>
  )
}

export default App