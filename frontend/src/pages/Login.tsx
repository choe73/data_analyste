import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/store/auth'
import { Logo } from '@/components/layout/Logo'
import { Loader2 } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, register } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await register(email, password, fullName)
      }
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#007A5E]/10 to-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <Logo size={48} />
          <div>
            <h1 className="text-2xl font-bold text-[#007A5E]">DataCollect</h1>
            <p className="text-sm text-gray-500">Pro Cameroun</p>
          </div>
        </div>

        <Card className="shadow-lg border-0">
          <CardHeader className="pb-4">
            <CardTitle className="text-center text-lg">
              {mode === 'login' ? 'Connexion' : 'Creer un compte'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === 'register' && (
                <div className="space-y-1">
                  <Label htmlFor="fullName">Nom complet</Label>
                  <Input
                    id="fullName"
                    name="fullName"
                    placeholder="Jean Dupont"
                    value={fullName}
                    onChange={e => setFullName(e.target.value)}
                    required
                  />
                </div>
              )}
              <div className="space-y-1">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="vous@exemple.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="password">Mot de passe</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder={mode === 'register' ? 'Minimum 8 caracteres' : '••••••••'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  minLength={8}
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full bg-[#007A5E] hover:bg-[#005a45]" disabled={loading}>
                {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                {mode === 'login' ? 'Se connecter' : 'Creer mon compte'}
              </Button>
            </form>

            <div className="mt-4 text-center text-sm text-gray-500">
              {mode === 'login' ? (
                <>Pas encore de compte ?{' '}
                  <button onClick={() => { setMode('register'); setError('') }} className="text-[#007A5E] font-medium hover:underline">
                    S'inscrire
                  </button>
                </>
              ) : (
                <>Deja un compte ?{' '}
                  <button onClick={() => { setMode('login'); setError('') }} className="text-[#007A5E] font-medium hover:underline">
                    Se connecter
                  </button>
                </>
              )}
            </div>

            {/* Cameroon flag accent */}
            <div className="flex gap-0.5 mt-6 justify-center">
              <div className="w-8 h-1 rounded bg-[#007A5E]" />
              <div className="w-8 h-1 rounded bg-[#CE1126]" />
              <div className="w-8 h-1 rounded bg-[#FCD116]" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
