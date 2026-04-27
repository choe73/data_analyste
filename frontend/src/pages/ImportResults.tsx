import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { ArrowLeft, BarChart3 } from 'lucide-react'

const API = (import.meta.env.VITE_API_URL as string) || ''

async function fetchImport(id: string) {
  const r = await fetch(`${API}/api/v1/imports/${id}`, { credentials: 'include' })
  if (!r.ok) throw new Error('Import not found')
  return r.json()
}

export default function ImportResults() {
  const { importId } = useParams<{ importId: string }>()
  const { data: imp, isLoading, error } = useQuery({
    queryKey: ['import', importId],
    queryFn: () => fetchImport(importId!),
    enabled: !!importId,
  })

  if (isLoading) return <div className="py-12 text-center text-muted-foreground">Chargement...</div>
  if (error || !imp) return (
    <div className="py-12 text-center">
      <p className="text-red-500 mb-4">Import introuvable</p>
      <Link to="/import"><Button variant="outline">Retour</Button></Link>
    </div>
  )

  const results = imp.analysis_results || {}
  const descriptive: Record<string, any> = results.descriptive || {}
  const correlations: Record<string, any> = results.correlations || {}
  const categorical: Record<string, any> = results.categorical || {}
  const nullSummary: Record<string, number> = results.null_summary || {}

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/import"><Button variant="ghost" size="sm"><ArrowLeft className="w-4 h-4 mr-1" />Retour</Button></Link>
        <div>
          <h1 className="text-2xl font-bold">{imp.original_filename}</h1>
          <p className="text-muted-foreground text-sm">
            {imp.row_count?.toLocaleString()} lignes · {imp.file_format?.toUpperCase()} ·{' '}
            <Badge variant="outline">{imp.analysis_status}</Badge>
          </p>
        </div>
      </div>

      {/* Colonnes détectées */}
      <Card>
        <CardHeader><CardTitle className="text-base">Colonnes détectées</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {(imp.column_names || []).map((col: string) => (
              <Badge key={col} variant="secondary">
                {col}
                <span className="ml-1 text-xs text-muted-foreground">
                  ({(imp.column_types || {})[col] || 'text'})
                </span>
              </Badge>
            ))}
          </div>
          {Object.keys(nullSummary).length > 0 && (
            <div className="mt-3 text-sm text-orange-600">
              Valeurs manquantes: {Object.entries(nullSummary).map(([k, v]) => `${k}: ${v}`).join(', ')}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistiques descriptives */}
      {Object.keys(descriptive).length > 0 && (
        <Card>
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><BarChart3 className="w-4 h-4" />Statistiques descriptives</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-muted">
                    {['Colonne', 'N', 'Moyenne', 'Écart-type', 'Min', '25%', '50%', '75%', 'Max'].map(h => (
                      <th key={h} className="px-3 py-2 text-left border font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(descriptive).map(([col, stats]: [string, any]) => (
                    <tr key={col} className="hover:bg-muted/50">
                      <td className="px-3 py-1 border font-medium">{col}</td>
                      <td className="px-3 py-1 border">{stats.count?.toFixed(0)}</td>
                      <td className="px-3 py-1 border">{stats.mean?.toFixed(3)}</td>
                      <td className="px-3 py-1 border">{stats.std?.toFixed(3)}</td>
                      <td className="px-3 py-1 border">{stats.min?.toFixed(3)}</td>
                      <td className="px-3 py-1 border">{stats['25%']?.toFixed(3)}</td>
                      <td className="px-3 py-1 border">{stats['50%']?.toFixed(3)}</td>
                      <td className="px-3 py-1 border">{stats['75%']?.toFixed(3)}</td>
                      <td className="px-3 py-1 border">{stats.max?.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Distributions catégorielles */}
      {Object.keys(categorical).length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(categorical).slice(0, 6).map(([col, dist]: [string, any]) => {
            const data = Object.entries(dist).map(([k, v]) => ({ name: k, count: v as number }))
            return (
              <Card key={col}>
                <CardHeader className="pb-2"><CardTitle className="text-sm">{col}</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={160}>
                    <BarChart data={data.slice(0, 10)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#2563eb" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Corrélations */}
      {Object.keys(correlations).length > 0 && (
        <Card>
          <CardHeader><CardTitle className="text-base">Matrice de corrélation</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="text-xs border-collapse">
                <thead>
                  <tr>
                    <th className="px-2 py-1 border bg-muted"></th>
                    {Object.keys(correlations).map(c => <th key={c} className="px-2 py-1 border bg-muted">{c}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(correlations).map(([row, vals]: [string, any]) => (
                    <tr key={row}>
                      <td className="px-2 py-1 border font-medium bg-muted">{row}</td>
                      {Object.entries(vals).map(([col, v]: [string, any]) => (
                        <td key={col} className="px-2 py-1 border text-center"
                          style={{ background: Math.abs(v) > 0.7 ? (v > 0 ? '#bbf7d0' : '#fecaca') : Math.abs(v) > 0.4 ? (v > 0 ? '#d1fae5' : '#fee2e2') : 'transparent' }}>
                          {typeof v === 'number' ? v.toFixed(2) : '—'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bouton analyser plus */}
      <Card className="border-dashed">
        <CardContent className="py-6 text-center">
          <p className="text-muted-foreground mb-3">Aller plus loin avec des analyses avancées</p>
          <Link to={`/analysis?dataset=${importId}`}>
            <Button><BarChart3 className="w-4 h-4 mr-2" />Analyser ce dataset</Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
