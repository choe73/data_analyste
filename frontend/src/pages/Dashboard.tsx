import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Activity, Database, FileText, Upload, CheckCircle, AlertCircle, Clock } from 'lucide-react'

const API = (import.meta.env.VITE_API_URL as string) || ''

async function apiFetch(path: string) {
  try {
    const r = await fetch(`${API}${path}`, { credentials: 'include' })
    if (!r.ok) return []
    const data = await r.json()
    return Array.isArray(data) ? data : (data ?? [])
  } catch {
    return []
  }
}

export function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiFetch('/health').catch(() => null),
    refetchInterval: 30000,
  })

  const { data: datasets = [] } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => apiFetch('/api/v1/datasets').catch(() => []),
  })

  const { data: imports = [] } = useQuery({
    queryKey: ['imports'],
    queryFn: () => apiFetch('/api/v1/imports').catch(() => []),
  })

  const { data: forms = [] } = useQuery({
    queryKey: ['forms'],
    queryFn: () => apiFetch('/api/v1/forms').catch(() => []),
  })

  const totalResponses = (forms as any[]).reduce((sum: number, f: any) => sum + (f.response_count || 0), 0)
  const completedImports = (imports as any[]).filter((i: any) => i.analysis_status === 'completed').length
  const publishedForms = (forms as any[]).filter((f: any) => f.is_published).length

  const stats = [
    { title: 'Datasets disponibles', value: (datasets as any[]).length, icon: Database, color: 'bg-blue-500', link: '/datasets' },
    { title: 'Imports analysés', value: completedImports, icon: Upload, color: 'bg-green-500', link: '/import' },
    { title: 'Formulaires publiés', value: publishedForms, icon: FileText, color: 'bg-purple-500', link: '/forms' },
    { title: 'Réponses collectées', value: totalResponses, icon: Activity, color: 'bg-orange-500', link: '/forms' },
  ]

  const dbStatus = health?.status === 'healthy'
  const redisStatus = health?.redis === 'healthy'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground">Vue d'ensemble de la plateforme DataCollect Pro Cameroun</p>
      </div>

      {/* Stats réelles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Link key={stat.title} to={stat.link}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                  <div className={`p-2 rounded-full ${stat.color}`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Santé système */}
      <Card>
        <CardHeader><CardTitle>État du système</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[
              { label: 'API Backend', ok: !!health },
              { label: 'Base de données', ok: dbStatus },
              { label: 'Cache Redis', ok: redisStatus },
            ].map(({ label, ok }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-sm">{label}</span>
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {ok ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                  {ok ? 'Opérationnel' : 'Indisponible'}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Imports récents */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Imports récents</CardTitle>
            <Link to="/import"><Button variant="ghost" size="sm">Voir tout</Button></Link>
          </CardHeader>
          <CardContent>
            {(imports as any[]).length === 0 ? (
              <div className="text-center py-4">
                <p className="text-muted-foreground text-sm mb-2">Aucun import</p>
                <Link to="/import"><Button size="sm" variant="outline">Importer des données</Button></Link>
              </div>
            ) : (
              <div className="space-y-3">
                {(imports as any[]).slice(0, 5).map((imp: any) => (
                  <div key={imp.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium truncate max-w-[200px]">{imp.original_filename}</p>
                      <p className="text-xs text-muted-foreground">{imp.row_count?.toLocaleString()} lignes</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={imp.analysis_status === 'completed' ? 'default' : 'secondary'} className="text-xs">
                        {imp.analysis_status === 'completed' ? 'Analysé' : imp.analysis_status === 'uploaded' ? 'Uploadé' : imp.analysis_status}
                      </Badge>
                      {imp.analysis_status === 'completed' && (
                        <Link to={`/import/${imp.id}`}><Button variant="ghost" size="sm" className="h-6 text-xs">Voir</Button></Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Formulaires récents */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Formulaires actifs</CardTitle>
            <Link to="/forms"><Button variant="ghost" size="sm">Voir tout</Button></Link>
          </CardHeader>
          <CardContent>
            {(forms as any[]).length === 0 ? (
              <div className="text-center py-4">
                <p className="text-muted-foreground text-sm mb-2">Aucun formulaire</p>
                <Link to="/forms/new"><Button size="sm" variant="outline">Créer un formulaire</Button></Link>
              </div>
            ) : (
              <div className="space-y-3">
                {(forms as any[]).slice(0, 5).map((form: any) => (
                  <div key={form.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium truncate max-w-[200px]">{form.title}</p>
                      <p className="text-xs text-muted-foreground">{form.domain} · {form.response_count || 0} réponse(s)</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={form.is_published ? 'default' : 'secondary'} className="text-xs">
                        {form.is_published ? 'Publié' : 'Brouillon'}
                      </Badge>
                      {form.is_published && form.share_token && (
                        <Button
                          variant="ghost" size="sm" className="h-6 text-xs"
                          onClick={() => navigator.clipboard.writeText(`${window.location.origin}/f/${form.share_token}`)}
                        >
                          Copier lien
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Actions rapides */}
      <Card>
        <CardHeader><CardTitle>Actions rapides</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link to="/import"><Button variant="outline"><Upload className="w-4 h-4 mr-2" />Importer des données</Button></Link>
            <Link to="/forms/new"><Button variant="outline"><FileText className="w-4 h-4 mr-2" />Créer un formulaire</Button></Link>
            <Link to="/analysis"><Button variant="outline"><Activity className="w-4 h-4 mr-2" />Lancer une analyse</Button></Link>
            <Link to="/datasets"><Button variant="outline"><Database className="w-4 h-4 mr-2" />Explorer les datasets</Button></Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
