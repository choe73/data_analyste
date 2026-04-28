import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Check, X } from 'lucide-react'
import { authFetch } from '@/store/auth'

interface Plan {
  id: number
  name: string
  price_xaf: number | null
  features: Record<string, any>
}

export default function Pricing() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    authFetch('/api/v1/plans')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => setPlans(Array.isArray(data) ? data : []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto mb-4" />
        <p className="text-gray-600">Chargement des abonnements...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-12 text-center text-red-600">
        <p>Erreur lors du chargement des plans : {error}</p>
        <Button className="mt-4" onClick={() => window.location.reload()}>Réessayer</Button>
      </div>
    )
  }

  return (
    <div className="py-12 px-4 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Tarification DataCollect Pro</h1>
        <p className="text-gray-500">Choisissez le plan adapté à vos besoins d'analyse</p>
      </div>

      <div className="grid md:grid-cols-4 gap-6">
        {plans.map((plan) => {
          const isPopular = plan.name === 'standard'
          return (
            <Card
              key={plan.id}
              className={`p-6 flex flex-col ${isPopular ? 'ring-2 ring-[#007A5E] shadow-lg' : ''}`}
            >
              {isPopular && (
                <span className="bg-[#007A5E] text-white text-xs font-semibold px-3 py-1 rounded-full mb-3 w-fit">
                  Populaire
                </span>
              )}
              <h3 className="text-xl font-bold mb-1 capitalize">{plan.name}</h3>
              <div className="mb-5 text-3xl font-bold text-[#007A5E]">
                {plan.price_xaf != null ? `${plan.price_xaf.toLocaleString()} FCFA` : 'Sur devis'}
                {plan.price_xaf != null && <span className="text-sm font-normal text-gray-500">/mois</span>}
              </div>

              <ul className="space-y-2 mb-6 flex-grow text-sm">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600 shrink-0" />
                  {plan.features?.max_analyses ?? '∞'} analyses/mois
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600 shrink-0" />
                  {plan.features?.max_datasets ?? '∞'} datasets
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600 shrink-0" />
                  {plan.features?.max_forms ?? '∞'} formulaires
                </li>
                <li className="flex items-center gap-2">
                  {plan.features?.gemini
                    ? <Check className="w-4 h-4 text-green-600 shrink-0" />
                    : <X className="w-4 h-4 text-gray-400 shrink-0" />}
                  <span className={plan.features?.gemini ? '' : 'text-gray-400'}>IA Gemini</span>
                </li>
                <li className="flex items-center gap-2">
                  {plan.features?.export
                    ? <Check className="w-4 h-4 text-green-600 shrink-0" />
                    : <X className="w-4 h-4 text-gray-400 shrink-0" />}
                  <span className={plan.features?.export ? '' : 'text-gray-400'}>Export CSV/Excel</span>
                </li>
              </ul>

              <Button
                className={`w-full ${isPopular ? 'bg-[#007A5E] hover:bg-[#005a45]' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'}`}
              >
                {plan.name === 'enterprise' ? 'Nous contacter' : plan.price_xaf === 0 ? 'Plan actuel' : "S'abonner"}
              </Button>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
