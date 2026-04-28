import { useQuery, useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { getSources, triggerCollection, triggerAllCollections, getCollectionStatus } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Download, Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import type { DataSource } from '@/types'

export function DataCollection() {
  const { toast } = useToast()
  const [taskHistory, setTaskHistory] = useState<Record<string, any>>({})

  const { data: sources, isLoading } = useQuery<DataSource[]>({
    queryKey: ['sources'],
    queryFn: getSources,
  })

  const collectMutation = useMutation({
    mutationFn: (sourceId: string) => triggerCollection(sourceId, false),
    onSuccess: (data, sourceId) => {
      toast({ title: 'Collecte démarrée', description: `Tâche ID: ${data.task_id}` })
      setTaskHistory(prev => ({ ...prev, [data.task_id]: { status: 'pending', source: sourceId, result: null } }))
      // Poll status every 5s
      const interval = setInterval(async () => {
        try {
          const status = await getCollectionStatus(data.task_id)
          setTaskHistory(prev => ({ ...prev, [data.task_id]: status }))
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(interval)
          }
        } catch { clearInterval(interval) }
      }, 5000)
    },
    onError: () => toast({ title: 'Erreur', description: 'Impossible de démarrer la collecte', variant: 'destructive' }),
  })

  const collectAllMutation = useMutation({
    mutationFn: () => triggerAllCollections(false),
    onSuccess: (data) => {
      toast({ title: 'Collecte globale démarrée', description: 'Toutes les sources sont en cours de collecte' })
      if (data.tasks) {
        data.tasks.forEach((t: any) => {
          setTaskHistory(prev => ({ ...prev, [t.task_id]: { status: 'pending', source: t.source, result: null } }))
        })
      }
    },
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'unavailable':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'collecting':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Collecte de données</h1>
          <p className="text-muted-foreground">
            Gérer les sources de données et les collectes automatiques
          </p>
        </div>
        <Button 
          className="bg-cm-green hover:bg-cm-green/90"
          onClick={() => collectAllMutation.mutate()}
          disabled={collectAllMutation.isPending}
        >
          <Download className="w-4 h-4 mr-2" />
          {collectAllMutation.isPending ? 'Collecte en cours...' : 'Collecter toutes les sources'}
        </Button>
      </div>

      {/* Sources Grid */}
      {isLoading ? (
        <div className="text-center py-8">Chargement...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources?.sources.map((source) => (
            <Card key={source.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(source.status)}
                    <div>
                      <CardTitle className="text-lg">{source.name}</CardTitle>
                      <p className="text-xs text-muted-foreground">{source.url}</p>
                    </div>
                  </div>
                  <Badge variant={source.status === 'available' ? 'default' : 'secondary'}>
                    {source.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Dernière mise à jour:
                    </p>
                    <p className="text-sm">
                      {source.last_update 
                        ? new Date(source.last_update).toLocaleString('fr-FR')
                        : 'Jamais'}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => collectMutation.mutate(source.id)}
                    disabled={collectMutation.isPending || source.status !== 'available'}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Collecter
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Collection History - real tasks */}
      <Card>
        <CardHeader>
          <CardTitle>Tâches récentes</CardTitle>
        </CardHeader>
        <CardContent>
          {Object.keys(taskHistory).length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              Aucune collecte lancée dans cette session.
            </p>
          ) : (
            <div className="space-y-3">
              {Object.entries(taskHistory).map(([taskId, task]: [string, any]) => (
                <div key={taskId} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div className="flex items-center gap-3">
                    {task.status === 'completed' && <CheckCircle className="w-5 h-5 text-green-500" />}
                    {task.status === 'failed' && <XCircle className="w-5 h-5 text-red-500" />}
                    {task.status === 'running' && <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />}
                    {task.status === 'pending' && <Clock className="w-5 h-5 text-yellow-500" />}
                    <div>
                      <p className="text-sm font-medium">{task.source}</p>
                      <p className="text-xs text-muted-foreground font-mono">{taskId.slice(0, 8)}...</p>
                    </div>
                  </div>
                  <Badge variant={task.status === 'completed' ? 'default' : 'secondary'}>
                    {task.status === 'completed' && task.result?.records_collected != null
                      ? `${task.result.records_collected} enregistrements`
                      : task.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
