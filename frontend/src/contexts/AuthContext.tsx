import { createContext, useContext, useState, type ReactNode } from 'react'
import { login as apiLogin, register as apiRegister } from '../api/auth'

interface AuthState {
  token: string | null
  username: string | null
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function loadInitialState(): AuthState {
  const token = localStorage.getItem('access_token')
  const username = localStorage.getItem('username')
  return { token, username }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(loadInitialState)

  async function login(username: string, password: string) {
    const data = await apiLogin(username, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('username', data.username)
    setState({ token: data.access_token, username: data.username })
  }

  async function register(username: string, email: string, password: string) {
    const data = await apiRegister(username, email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('username', data.username)
    setState({ token: data.access_token, username: data.username })
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
    setState({ token: null, username: null })
  }

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
