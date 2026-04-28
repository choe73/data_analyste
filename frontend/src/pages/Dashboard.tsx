import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Activity, Database, FileText, Upload, CheckCircle, AlertCircle,
  BarChart3, Brain, TrendingUp, Zap, ArrowRight, Sparkles,
  Globe2, FlaskConical, Layers
} from 'lucide-react'
import { authFetch } from '@/store/auth'

const API = (import.meta.env.VITE_API_URL as string) || ''

async function apiFetch(path: string) {
  try {
    const r = await authFetch(path)
    if (!r.ok) return []
    const data = await r.json()
    return Array.isArray(data) ? data : (data ?? [])
  } catch { return [] }
}

export function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      try {
        const r = await fetch(`${API}/health`)
        return r.ok ? r.json() : null
      } catch { return null }
    },
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
    {
      title: 'Datasets disponibles',
      description: 'Sources de données structurées prêtes pour l\'analyse',
      value: (datasets as any[]).length,
      icon: Database,
      gradient: 'from-blue-500 to-cyan-400',
      bgLight: 'bg-blue-50',
      textColor: 'text-blue-600',
      link: '/datasets',
    },
    {
      title: 'Imports analysés',
      description: 'Fichiers importés et traités par le moteur d\'analyse',
      value: completedImports,
      icon: Upload,
      gradient: 'from-emerald-500 to-green-400',
      bgLight: 'bg-emerald-50',
      textColor: 'text-emerald-600',
      link: '/import',
    },
    {
      title: 'Formulaires publiés',
      description: 'Enquêtes et formulaires de collecte actifs',
      value: publishedForms,
      icon: FileText,
      gradient: 'from-violet-500 to-purple-400',
      bgLight: 'bg-violet-50',
      textColor: 'text-violet-600',
      link: '/forms',
    },
    {
      title: 'Réponses collectées',
      description: 'Données collectées via formulaires et API',
      value: totalResponses,
      icon: Activity,
      gradient: 'from-amber-500 to-orange-400',
      bgLight: 'bg-amber-50',
      textColor: 'text-amber-600',
      link: '/forms',
    },
  ]

  const dbStatus = health?.status === 'healthy'
  const redisStatus = health?.redis === 'healthy'

  const quickActions = [
    {
      title: 'Importer des données',
      description: 'CSV, Excel ou API — analyse automatique par l\'IA',
      icon: Upload,
      link: '/import',
      gradient: 'from-blue-600 to-cyan-500',
    },
    {
      title: 'Créer un formulaire',
      description: 'Construisez des enquêtes adaptées au contexte camerounais',
      icon: FileText,
      link: '/forms/new',
      gradient: 'from-violet-600 to-purple-500',
    },
    {
      title: 'Lancer une analyse',
      description: 'Statistiques, régression, ACP, clustering — interprétées par Gemini',
      icon: Brain,
      link: '/analysis',
      gradient: 'from-emerald-600 to-green-500',
    },
    {
      title: 'Explorer les datasets',
      description: 'Données régionales : agriculture, santé, éducation, finance',
      icon: Globe2,
      link: '/datasets',
      gradient: 'from-amber-600 to-orange-500',
    },
  ]

  const capabilities = [
    {
      icon: BarChart3,
      title: 'Analyses descriptives',
      desc: 'Moyennes, corrélations, distributions',
    },
    {
      icon: TrendingUp,
      title: 'Régression & Prédiction',
      desc: 'Modèles linéaires, polynomiaux, séries temporelles',
    },
    {
      icon: Layers,
      title: 'ACP & Clustering',
      desc: 'Réduction de dimensionnalité, segmentation automatique',
    },
    {
      icon: FlaskConical,
      title: 'Classification supervisée',
      desc: 'Arbres de décision, SVM, forêts aléatoires',
    },
    {
      icon: Sparkles,
      title: 'Interprétation IA',
      desc: 'Gemini traduit vos résultats en recommandations actionnables',
    },
    {
      icon: Zap,
      title: 'Collecte automatisée',
      desc: 'API World Bank, NASA, FAO — données en temps réel',
    },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Hero header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#007A5E] via-[#006B50] to-[#005a45] p-8 text-white">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyem0wLTRWMjhIMjR2Mmgxem0tMi0ydi0ySDE0djJoMjB6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-30" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5 text-green-300" />
            <span className="text-sm font-medium text-green-200">Assistant analytique augmenté par l'IA</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            DataCollect Pro Cameroun
          </h1>
          <p className="text-green-100 max-w-2xl text-base leading-relaxed">
            De la donnée brute à l'action — collectez, analysez et obtenez des recommandations
            contextuelles pour les 10 régions du Cameroun. Régression, ACP, clustering et classification,
            interprétés par l'IA Gemini.
          </p>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon
          return (
            <Link key={stat.title} to={stat.link} className="group">
              <Card className="relative overflow-hidden hover:shadow-lg transition-all duration-300 border-0 shadow-sm group-hover:-translate-y-0.5">
                <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-[0.04] group-hover:opacity-[0.08] transition-opacity`} />
                <CardHeader className="flex flex-row items-center justify-between pb-2 relative">
                  <div className="space-y-0.5">
                    <CardTitle className="text-sm font-semibold text-gray-700">{stat.title}</CardTitle>
                    <CardDescription className="text-xs text-gray-400 hidden sm:block">{stat.description}</CardDescription>
                  </div>
                  <div className={`p-2.5 rounded-xl ${stat.bgLight}`}>
                    <Icon className={`w-5 h-5 ${stat.textColor}`} />
                  </div>
                </CardHeader>
                <CardContent className="relative">
                  <div className="text-3xl font-bold tracking-tight text-gray-900">{stat.value}</div>
                  <div className="flex items-center gap-1 mt-1 text-xs text-gray-400 group-hover:text-[#007A5E] transition-colors">
                    <ArrowRight className="w-3 h-3" />
                    <span>Voir les détails</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <Link key={action.title} to={action.link}>
                <Card className="group hover:shadow-lg transition-all duration-300 border-0 shadow-sm overflow-hidden cursor-pointer hover:-translate-y-0.5">
                  <div className="h-1 bg-gradient-to-r {action.gradient}" style={{ background: `linear-gradient(to right, var(--tw-gradient-stops))` }} />
                  <CardContent className="p-5">
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg bg-gradient-to-br ${action.gradient} text-white shrink-0`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="font-semibold text-sm text-gray-900 mb-1">{action.title}</h3>
                        <p className="text-xs text-gray-500 leading-relaxed">{action.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent imports */}
        <Card className="shadow-sm border-0">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-base font-semibold">Imports récents</CardTitle>
              <CardDescription className="text-xs text-gray-400">Derniers fichiers importés et analysés</CardDescription>
            </div>
            <Link to="/import"><Button variant="ghost" size="sm" className="text-[#007A5E]">Voir tout <ArrowRight className="w-3 h-3 ml-1" /></Button></Link>
          </CardHeader>
          <CardContent>
            {(imports as any[]).length === 0 ? (
              <div className="text-center py-8 bg-gray-50/50 rounded-xl">
                <Upload className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-1">Aucun import pour le moment</p>
                <p className="text-xs text-gray-400 mb-4">Importez un fichier CSV ou Excel pour démarrer</p>
                <Link to="/import"><Button size="sm" className="bg-[#007A5E] hover:bg-[#005a45]">Importer des données</Button></Link>
              </div>
            ) : (
              <div className="space-y-3">
                {(imports as any[]).slice(0, 5).map((imp: any) => (
                  <div key={imp.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{imp.original_filename}</p>
                      <p className="text-xs text-gray-400">{imp.row_count?.toLocaleString()} lignes · {imp.file_format?.toUpperCase()}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge
                        variant={imp.analysis_status === 'completed' ? 'default' : 'secondary'}
                        className={`text-xs ${imp.analysis_status === 'completed' ? 'bg-emerald-100 text-emerald-700 hover:bg-emerald-100' : ''}`}
                      >
                        {imp.analysis_status === 'completed' ? 'Analysé' : imp.analysis_status === 'uploaded' ? 'Uploadé' : imp.analysis_status}
                      </Badge>
                      {imp.analysis_status === 'completed' && (
                        <Link to={`/import/${imp.id}`}><Button variant="ghost" size="sm" className="h-7 text-xs text-[#007A5E]">Voir</Button></Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Active forms */}
        <Card className="shadow-sm border-0">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-base font-semibold">Formulaires actifs</CardTitle>
              <CardDescription className="text-xs text-gray-400">Enquêtes et sondages en cours de collecte</CardDescription>
            </div>
            <Link to="/forms"><Button variant="ghost" size="sm" className="text-[#007A5E]">Voir tout <ArrowRight className="w-3 h-3 ml-1" /></Button></Link>
          </CardHeader>
          <CardContent>
            {(forms as any[]).length === 0 ? (
              <div className="text-center py-8 bg-gray-50/50 rounded-xl">
                <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-1">Aucun formulaire créé</p>
                <p className="text-xs text-gray-400 mb-4">Créez un formulaire pour collecter des données sur le terrain</p>
                <Link to="/forms/new"><Button size="sm" className="bg-[#007A5E] hover:bg-[#005a45]">Créer un formulaire</Button></Link>
              </div>
            ) : (
              <div className="space-y-3">
                {(forms as any[]).slice(0, 5).map((form: any) => (
                  <div key={form.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{form.title}</p>
                      <p className="text-xs text-gray-400">{form.domain} · {form.response_count || 0} réponse(s)</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge
                        variant={form.is_published ? 'default' : 'secondary'}
                        className={`text-xs ${form.is_published ? 'bg-violet-100 text-violet-700 hover:bg-violet-100' : ''}`}
                      >
                        {form.is_published ? 'Publié' : 'Brouillon'}
                      </Badge>
                      {form.is_published && form.share_token && (
                        <Button
                          variant="ghost" size="sm" className="h-7 text-xs text-[#007A5E]"
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

      {/* Capabilities */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Capacités d'analyse</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {capabilities.map((cap) => {
            const Icon = cap.icon
            return (
              <div key={cap.title} className="flex items-start gap-3 p-4 rounded-xl bg-white shadow-sm border-0 hover:shadow-md transition-shadow">
                <div className="p-2 rounded-lg bg-[#007A5E]/10 shrink-0">
                  <Icon className="w-5 h-5 text-[#007A5E]" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">{cap.title}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">{cap.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* System health */}
      <Card className="shadow-sm border-0">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold">État du système</CardTitle>
          <CardDescription className="text-xs text-gray-400">Monitoring en temps réel des services</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: 'API Backend', ok: !!health, detail: 'FastAPI + Uvicorn' },
              { label: 'Base de données', ok: dbStatus, detail: 'PostgreSQL / Supabase' },
              { label: 'Cache Redis', ok: redisStatus, detail: 'Mise en cache des requêtes' },
            ].map(({ label, ok, detail }) => (
              <div key={label} className={`flex items-center gap-3 p-3 rounded-xl ${ok ? 'bg-emerald-50/50' : 'bg-red-50/50'}`}>
                <div className={`p-1.5 rounded-full ${ok ? 'bg-emerald-100' : 'bg-red-100'}`}>
                  {ok ? <CheckCircle className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-red-500" />}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{label}</p>
                  <p className="text-xs text-gray-400">{detail}</p>
                </div>
                <Badge variant="outline" className={`ml-auto text-xs ${ok ? 'border-emerald-200 text-emerald-700' : 'border-red-200 text-red-600'}`}>
                  {ok ? 'OK' : 'Down'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
