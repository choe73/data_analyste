import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Brain, Database } from 'lucide-react'
import { authFetch } from '@/store/auth'

interface MLModel {
  id: number
  model_name: string
  model_type: string
  algorithm: string
  metrics: Record<string, any> | null
  is_active: boolean
  created_at: string | null
}

export function Models() {
  const [models, setModels] = useState<MLModel[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    authFetch('/api/v1/models')
      .then(res => res.ok ? res.json() : [])
      .then(data => setModels(Array.isArray(data) ? data : []))
      .catch(() => setModels([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-3" />
        <p className="text-gray-500">Chargement de vos modèles...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Modèles d'Intelligence Artificielle</h1>
        <p className="text-gray-500 mt-1">
          Modèles entraînés sur vos données — {models.length} modèle{models.length !== 1 ? 's' : ''} en base
        </p>
      </div>

      {models.length === 0 ? (
        <Card className="border-2 border-dashed border-gray-200 bg-gray-50">
          <CardContent className="p-12 text-center">
            <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p className="font-medium text-gray-700 mb-2">Aucun modèle entraîné</p>
            <p className="text-sm text-gray-500">
              Allez dans "Analyses & Gemini IA", importez un dataset, puis lancez une
              Régression ou une Classification pour créer votre premier modèle.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {models.map((model) => (
            <Card key={model.id}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <Brain className="w-5 h-5 text-[#007A5E]" />
                  {model.model_name}
                  {model.is_active && (
                    <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      Actif
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 text-sm text-gray-600 mb-3">
                  <span>Type : <strong>{model.model_type}</strong></span>
                  <span>Algorithme : <strong>{model.algorithm}</strong></span>
                  {model.created_at && (
                    <span>Créé le : <strong>{new Date(model.created_at).toLocaleDateString('fr-FR')}</strong></span>
                  )}
                </div>
                {model.metrics && Object.keys(model.metrics).length > 0 && (
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-xs font-semibold text-gray-500 mb-2">Métriques de performance</p>
                    <div className="flex flex-wrap gap-3">
                      {Object.entries(model.metrics).map(([key, val]) => (
                        <div key={key} className="text-xs">
                          <span className="text-gray-500">{key}: </span>
                          <span className="font-mono font-medium">
                            {typeof val === 'number' ? val.toFixed(4) : String(val)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
