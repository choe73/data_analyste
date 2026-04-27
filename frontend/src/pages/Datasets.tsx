import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Database, Search, BarChart3, Upload } from 'lucide-react'
import type { Dataset } from '@/types'

const API = (import.meta.env.VITE_API_URL as string) || ''

async function fetchDatasets(domain?: string, source?: string): Promise<Dataset[]> {
  const params = new URLSearchParams()
  if (domain && domain !== 'all') params.append('domain', domain)
  if (source && source !== 'all') params.append('source', source)
  const qs = params.toString()
  const r = await fetch(`${API}/api/v1/datasets${qs ? '?' + qs : ''}`, { credentials: 'include' })
  if (!r.ok) return []
  return r.json()
}

const DOMAIN_COLORS: Record<string, string> = {
  agriculture: 'bg-green-100 text-green-800',
  sante: 'bg-red-100 text-red-800',
  education: 'bg-blue-100 text-blue-800',
  economie: 'bg-yellow-100 text-yellow-800',
  environnement: 'bg-teal-100 text-teal-800',
  demographie: 'bg-purple-100 text-purple-800',
  general: 'bg-gray-100 text-gray-800',
}

export function Datasets() {
  const [search, setSearch] = useState('')
  const [domain, setDomain] = useState('all')
  const [source, setSource] = useState('all')

  const { data: datasets = [], isLoading } = useQuery<Dataset[]>({
    queryKey: ['datasets', domain, source],
    queryFn: () => fetchDatasets(domain, source),
  })

  const filtered = datasets.filter(d =>
    !search || d.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Datasets</h1>
          <p className="text-muted-foreground">Explorer et analyser les données disponibles</p>
        </div>
        <Link to="/import">
          <Button><Upload className="w-4 h-4 mr-2" />Importer un dataset</Button>
        </Link>
      </div>

      {/* Filtres */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Rechercher..." className="pl-9" value={search} onChange={e => setSearch(e.target.value)} />
            </div>
            <Select value={domain} onValueChange={setDomain}>
              <SelectTrigger className="w-[160px]"><SelectValue placeholder="Domaine" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les domaines</SelectItem>
                {['agriculture', 'sante', 'education', 'economie', 'environnement', 'demographie', 'general'].map(d => (
                  <SelectItem key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={source} onValueChange={setSource}>
              <SelectTrigger className="w-[160px]"><SelectValue placeholder="Source" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes les sources</SelectItem>
                <SelectItem value="import">Mes imports</SelectItem>
                <SelectItem value="collected">Données collectées</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">Chargement...</div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Database className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
            <p className="text-muted-foreground mb-3">Aucun dataset trouvé</p>
            <Link to="/import"><Button variant="outline">Importer des données</Button></Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((dataset) => {
            const colorClass = DOMAIN_COLORS[dataset.domain || 'general'] || DOMAIN_COLORS.general
            return (
              <Card key={dataset.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base leading-tight">{dataset.name}</CardTitle>
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${colorClass}`}>
                      {dataset.domain}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{dataset.source}</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                    <div>
                      <p className="text-muted-foreground text-xs">Lignes</p>
                      <p className="font-medium">{dataset.row_count?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground text-xs">Colonnes</p>
                      <p className="font-medium">{dataset.columns?.length || 0}</p>
                    </div>
                  </div>

                  {/* Aperçu des colonnes */}
                  {dataset.columns && dataset.columns.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {dataset.columns.slice(0, 4).map(col => (
                        <Badge key={col} variant="outline" className="text-xs">{col}</Badge>
                      ))}
                      {dataset.columns.length > 4 && (
                        <Badge variant="outline" className="text-xs">+{dataset.columns.length - 4}</Badge>
                      )}
                    </div>
                  )}

                  <div className="pt-3 border-t">
                    <p className="text-xs text-muted-foreground mb-2">
                      {dataset.last_updated ? new Date(dataset.last_updated).toLocaleDateString('fr-FR') : ''}
                    </p>
                    <div className="flex gap-2">
                      {dataset.source === 'import' && (
                        <Link to={`/import/${dataset.id}`} className="flex-1">
                          <Button variant="outline" size="sm" className="w-full">Résultats</Button>
                        </Link>
                      )}
                      <Link to={`/analysis?dataset=${dataset.id}`} className="flex-1">
                        <Button size="sm" className="w-full">
                          <BarChart3 className="w-3 h-3 mr-1" />Analyser
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
