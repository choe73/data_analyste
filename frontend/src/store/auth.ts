import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const API = (import.meta.env.VITE_API_URL as string) || ''

interface User { id: number; email: string; full_name?: string; role: string }

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const form = new URLSearchParams()
        form.append('username', email)
        form.append('password', password)
        const r = await fetch(`${API}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form.toString(),
        })
        if (!r.ok) {
          const err = await r.json().catch(() => ({}))
          throw new Error(err.detail || 'Identifiants incorrects')
        }
        const data = await r.json()
        const token = data.access_token
        const me = await fetch(`${API}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        const user = await me.json()
        set({ token, user, isAuthenticated: true })
      },

      register: async (email, password, full_name) => {
        const r = await fetch(`${API}/api/v1/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name }),
        })
        if (!r.ok) {
          const err = await r.json().catch(() => ({}))
          throw new Error(err.detail || 'Erreur lors de la creation du compte')
        }
        const { login } = useAuth.getState()
        await login(email, password)
      },

      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
      partialize: (s) => ({ token: s.token, user: s.user, isAuthenticated: s.isAuthenticated }),
    }
  )
)

/** Fetch with automatic Bearer token injection */
export async function authFetch(path: string, opts: RequestInit = {}): Promise<Response> {
  const token = useAuth.getState().token
  const headers: Record<string, string> = { ...(opts.headers as Record<string, string> || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!(opts.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }
  const API_URL = (import.meta.env.VITE_API_URL as string) || ''
  return fetch(`${API_URL}${path}`, { ...opts, headers })
}
