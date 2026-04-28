import { Card, CardContent } from '@/components/ui/card'
import { Zap } from 'lucide-react'

export function Models() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Modèles ML</h1>
          <p className="text-muted-foreground">
            Gérer les modèles entraînés et leurs prédictions
          </p>
        </div>
      </div>

      {/* Coming Soon */}
      <Card className="border-2 border-dashed border-cm-green/30 bg-cm-green/5">
        <CardContent className="p-12 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-full bg-cm-green/10 flex items-center justify-center">
              <Zap className="w-8 h-8 text-cm-green" />
            </div>
          </div>
          <h2 className="text-2xl font-bold mb-2">Bientôt disponible</h2>
          <p className="text-muted-foreground mb-4">
            La fonctionnalité d'entraînement et de gestion des modèles ML sera disponible prochainement.
          </p>
          <p className="text-sm text-gray-500">
            Nous travaillons actuellement sur l'intégration complète des algorithmes d'apprentissage automatique.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
