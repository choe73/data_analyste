import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

import { BarChart3, LineChart, PieChart, Activity, Loader2, AlertCircle, Brain, TrendingUp } from 'lucide-react'
import {
  BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, LineChart as RLineChart, Line, Legend,
} from 'recharts'
import type { Dataset } from '@/types'

const API = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000'

function getToken() {
  try {
    const s = localStorage.getItem('auth-storage')
    return s ? JSON.parse(s)?.state?.token : null
  } catch { return null }
}

async function apiFetch(path: string, body?: object) {
  const token = getToken()
  const r = await fetch(`${API}${path}`, {
    method: body ? 'POST' : 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!r.ok) {
    const text = await r.text()
    try {
      const json = JSON.parse(text)
      throw new Error(json.detail || text)
    } catch {
      throw new Error(text || `HTTP ${r.status}`)
    }
  }
  return r.json()
}

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed', '#0891b2']

// Utility functions
function corrColor(v: number): string {
  const abs = Math.abs(v)
  if (abs > 0.7) return v > 0 ? '#bbf7d0' : '#fecaca'
  if (abs > 0.4) return v > 0 ? '#d1fae5' : '#fee2e2'
  return 'transparent'
}

function buildHistogram(values: number[], bins: number) {
  const clean = values.filter(v => v != null && !isNaN(v))
  if (clean.length === 0) return []
  const min = Math.min(...clean), max = Math.max(...clean)
  const step = (max - min) / bins || 1
  const counts = Array(bins).fill(0)
  clean.forEach(v => {
    const i = Math.min(Math.floor((v - min) / step), bins - 1)
    counts[i]++
  })
  return counts.map((count, i) => ({
    label: (min + i * step).toFixed(2),
    count
  }))
}

// Error Display Component
function ErrorDisplay({ error }: { error: any }) {
  const message = error?.message || String(error)
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex gap-3">
        <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-red-900">Erreur</p>
          <p className="text-sm text-red-700 mt-1">{message}</p>
        </div>
      </div>
    </div>
  )
}

// Loading Component
function LoadingSpinner({ text = 'Chargement...' }: { text?: string }) {
  return (
    <div className="flex items-center justify-center p-8">
      <Loader2 className="w-6 h-6 animate-spin mr-2" />
      <span className="text-muted-foreground">{text}</span>
    </div>
  )
}

// Descriptive Analysis Panel
function DescriptivePanel({ datasetId, columns, onResult }: {
  datasetId: number
  columns: string[]
  onResult?: (data: any) => void
}) {
  const [selected, setSelected] = useState<string[]>(columns.slice(0, 6))
  
  useEffect(() => {
    if (columns.length > 0 && selected.length === 0) {
      setSelected(columns.slice(0, 6))
    }
  }, [columns])

  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/descriptive', {
      dataset_id: datasetId,
      columns: selected,
      confidence_level: 0.95,
    }),
    onSuccess: (data) => onResult?.(data),
  })

  const stats: any[] = mut.data?.statistics || []
  const corr: any = mut.data?.correlations
  const plot: any = mut.data?.plot_data

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm font-medium">Colonnes:</span>
        {columns.map(c => (
          <Badge
            key={c}
            variant={selected.includes(c) ? 'default' : 'outline'}
            className="cursor-pointer hover:bg-primary/80"
            onClick={() => setSelected(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}
          >
            {c}
          </Badge>
        ))}
        <Button
          size="sm"
          onClick={() => mut.mutate()}
          disabled={mut.isPending || selected.length === 0}
        >
          {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-1" />}
          Analyser
        </Button>
      </div>

      {mut.isError && <ErrorDisplay error={mut.error} />}

      {stats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Statistiques descriptives</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-muted">
                    {['Colonne', 'N', 'Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max', 'IC 95%'].map(h => (
                      <th key={h} className="px-3 py-2 text-left font-medium border">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {stats.map((s: any) => (
                    <tr key={s.column} className="hover:bg-muted/50">
                      <td className="px-3 py-2 border font-medium">{s.column}</td>
                      <td className="px-3 py-2 border">{s.count}</td>
                      <td className="px-3 py-2 border">{s.mean?.toFixed(2)}</td>
                      <td className="px-3 py-2 border">{s.median?.toFixed(2)}</td>
                      <td className="px-3 py-2 border">{s.std?.toFixed(2)}</td>
                      <td className="px-3 py-2 border">{s.min?.toFixed(2)}</td>
                      <td className="px-3 py-2 border">{s.max?.toFixed(2)}</td>
                      <td className="px-3 py-2 border text-xs">
                        [{s.ci_lower?.toFixed(2)}, {s.ci_upper?.toFixed(2)}]
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {plot?.histograms && Object.keys(plot.histograms).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Distribution des variables</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(plot.histograms).slice(0, 4).map(([col, vals]: [string, any]) => (
                <div key={col}>
                  <p className="text-sm font-medium mb-2">{col}</p>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={buildHistogram(vals, 20)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="label" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {corr && corr.columns && corr.columns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Matrice de corrélation (Pearson)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="text-xs border-collapse">
                <thead>
                  <tr>
                    <th className="px-2 py-1 border bg-muted"></th>
                    {corr.columns.map((c: string) => (
                      <th key={c} className="px-2 py-1 border bg-muted">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {corr.columns.map((row: string, i: number) => (
                    <tr key={row}>
                      <td className="px-2 py-1 border font-medium bg-muted">{row}</td>
                      {corr.values[i].map((v: number, j: number) => (
                        <td
                          key={j}
                          className="px-2 py-1 border text-center font-medium"
                          style={{ background: corrColor(v) }}
                        >
                          {v.toFixed(2)}
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
    </div>
  )
}

// Regression Panel
function RegressionPanel({ datasetId, columns, numericColumns, onResult }: {
  datasetId: number
  columns: string[]
  numericColumns: string[]
  onResult?: (data: any) => void
}) {
  const [target, setTarget] = useState('')
  const [features, setFeatures] = useState<string[]>([])
  const [method, setMethod] = useState('linear')

  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/regression', {
      dataset_id: datasetId,
      target_column: target,
      feature_columns: features,
      method,
      test_size: 0.2,
      alpha: 1.0,
    }),
    onSuccess: (data) => onResult?.(data),
  })

  const res: any = mut.data
  const availableColumns = numericColumns.length > 0 ? numericColumns : columns

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="text-sm font-medium block mb-2">Variable cible (Y)</label>
          <Select value={target} onValueChange={setTarget}>
            <SelectTrigger>
              <SelectValue placeholder="Choisir Y" />
            </SelectTrigger>
            <SelectContent>
              {availableColumns.map(c => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-sm font-medium block mb-2">Méthode</label>
          <Select value={method} onValueChange={setMethod}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {['linear', 'ridge', 'lasso', 'elasticnet'].map(m => (
                <SelectItem key={m} value={m}>{m}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-end">
          <Button
            onClick={() => mut.mutate()}
            disabled={!target || features.length === 0 || mut.isPending}
            className="w-full"
          >
            {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
            Calculer
          </Button>
        </div>
      </div>

      <div>
        <label className="text-sm font-medium block mb-2">Variables explicatives (X)</label>
        <div className="flex flex-wrap gap-2">
          {availableColumns.filter(c => c !== target).map(c => (
            <Badge
              key={c}
              variant={features.includes(c) ? 'default' : 'outline'}
              className="cursor-pointer hover:bg-primary/80"
              onClick={() => setFeatures(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}
            >
              {c}
            </Badge>
          ))}
        </div>
      </div>

      {mut.isError && <ErrorDisplay error={mut.error} />}

      {res && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'R²', value: res.metrics?.r2_score },
              { label: 'R² ajusté', value: res.metrics?.adjusted_r2 },
              { label: 'RMSE', value: res.metrics?.rmse },
              { label: 'MAE', value: res.metrics?.mae }
            ].map(({ label, value }) => (
              <Card key={label}>
                <CardContent className="p-4 text-center">
                  <p className="text-xs text-muted-foreground mb-1">{label}</p>
                  <p className={`text-2xl font-bold ${
                    value != null && value > 0.7 ? 'text-green-600' :
                    value != null && value > 0.4 ? 'text-orange-500' : 'text-red-500'
                  }`}>
                    {value != null ? value.toFixed(4) : '---'}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {res.coefficients && res.coefficients.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Coefficients</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-muted">
                        <th className="px-3 py-2 text-left border">Variable</th>
                        <th className="px-3 py-2 border">Coefficient</th>
                        <th className="px-3 py-2 border">VIF</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="px-3 py-2 border font-medium">Constante</td>
                        <td className="px-3 py-2 border">{res.intercept?.toFixed(6)}</td>
                        <td className="px-3 py-2 border">---</td>
                      </tr>
                      {res.coefficients.map((c: any) => (
                        <tr key={c.name} className={c.vif > 10 ? 'bg-orange-50' : ''}>
                          <td className="px-3 py-2 border">{c.name}</td>
                          <td className="px-3 py-2 border">{c.value?.toFixed(6)}</td>
                          <td className="px-3 py-2 border">
                            {c.vif ? (
                              c.vif > 10 ? (
                                <span className="text-orange-600 font-medium">{c.vif.toFixed(1)} ⚠</span>
                              ) : (
                                c.vif.toFixed(1)
                              )
                            ) : '---'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {res.plot_data?.scatter && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Valeurs réelles vs prédites</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="x" name="Prédit" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="y" name="Réel" tick={{ fontSize: 11 }} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter
                      data={res.plot_data.scatter.x.map((x: number, i: number) => ({
                        x,
                        y: res.plot_data.scatter.y[i]
                      }))}
                      fill="#2563eb"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

// Gemini Interpretation Panel
function GeminiPanel({ analysisType, analysisData }: {
  analysisType: string
  analysisData: any
}) {
  const [question, setQuestion] = useState('')
  const [domain, setDomain] = useState('')

  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/interpret', {
      analysis_type: analysisType,
      analysis_data: analysisData,
      user_question: question || undefined,
      domain_hint: domain || undefined,
    }),
  })

  const res: any = mut.data

  if (!analysisData) return null

  return (
    <Card className="border-purple-200 bg-purple-50/30">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-600" />
          Interprétation IA
          {res?.persona && <span className="text-sm font-normal text-muted-foreground">— {res.persona}</span>}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2 flex-wrap">
          <Select value={domain} onValueChange={setDomain}>
            <SelectTrigger className="w-48 h-9 text-sm">
              <SelectValue placeholder="Domaine (auto)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Auto-détection</SelectItem>
              {['sante', 'agriculture', 'finance', 'entrepreneuriat', 'education', 'environnement'].map(d => (
                <SelectItem key={d} value={d}>{d}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <input
            className="flex-1 border rounded px-3 py-2 text-sm min-w-[200px]"
            placeholder="Question spécifique (optionnel)..."
            value={question}
            onChange={e => setQuestion(e.target.value)}
          />
          <Button
            size="sm"
            variant="outline"
            onClick={() => mut.mutate()}
            disabled={mut.isPending}
          >
            {mut.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Interpréter'}
          </Button>
        </div>

        {mut.isError && <ErrorDisplay error={mut.error} />}

        {res && (
          <div className="space-y-3 text-sm">
            {res.domain && (
              <p className="text-xs text-purple-600 font-medium">
                Domaine: {res.domain}
              </p>
            )}
            <p className="text-gray-700 leading-relaxed">{res.interpretation}</p>
            {res.key_findings && res.key_findings.length > 0 && (
              <div>
                <p className="font-medium text-purple-700 mb-1">Points clés:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {res.key_findings.map((f: string, i: number) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
            )}
            {res.recommendations && res.recommendations.length > 0 && (
              <div>
                <p className="font-medium text-purple-700 mb-1">Recommandations:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {res.recommendations.map((r: string, i: number) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
            {res.warnings && res.warnings.length > 0 && (
              <div className="bg-orange-50 border border-orange-200 rounded p-2">
                <p className="text-xs text-orange-700">{res.warnings.join(' ')}</p>
              </div>
            )}
            {res.quota_remaining != null && (
              <p className="text-xs text-muted-foreground">
                Quota restant: {res.quota_remaining}/heure
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Main Analysis Component
export function Analysis() {
  const [datasetId, setDatasetId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState('descriptive')
  const [lastResult, setLastResult] = useState<any>(null)
  const [preview, setPreview] = useState<any>(null)

  const { data: datasets = [], isLoading: datasetsLoading } = useQuery<Dataset[]>({
    queryKey: ['datasets'],
    queryFn: () => apiFetch('/api/v1/datasets'),
  })

  // Fetch preview when dataset changes
  useEffect(() => {
    if (datasetId) {
      setPreview(null)
      setLastResult(null)
      apiFetch(`/api/v1/analysis/preview/${datasetId}`)
        .then(data => setPreview(data))
        .catch(err => {
          console.error('Preview error:', err)
          setPreview(null)
        })
    } else {
      setPreview(null)
      setLastResult(null)
    }
  }, [datasetId])

  // Extract columns from preview
  const numericColumns = preview?.columns?.numeric || []
  const categoricalColumns = preview?.columns?.categorical || []
  const allColumns = [...numericColumns, ...categoricalColumns]

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <TrendingUp className="w-8 h-8" />
          Analyse de données
        </h1>
        <p className="text-muted-foreground mt-1">
          Statistiques descriptives, régression, ACP, classification, clustering
        </p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <span className="text-sm font-medium whitespace-nowrap">Dataset:</span>
            <Select
              value={datasetId ? String(datasetId) : ''}
              onValueChange={v => setDatasetId(Number(v))}
            >
              <SelectTrigger className="w-full sm:w-[400px]">
                <SelectValue placeholder="Sélectionner un dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((d: Dataset) => (
                  <SelectItem key={d.id} value={String(d.id)}>
                    {d.name} — {d.row_count.toLocaleString()} lignes
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {preview && (
              <div className="flex gap-2 text-xs">
                <Badge variant="outline">{preview.row_count?.toLocaleString()} lignes</Badge>
                <Badge variant="outline">{numericColumns.length} num</Badge>
                <Badge variant="outline">{categoricalColumns.length} cat</Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {datasetsLoading && <LoadingSpinner text="Chargement des datasets..." />}

      {!datasetId && !datasetsLoading && (
        <Card className="border-dashed">
          <CardContent className="p-12 text-center text-muted-foreground">
            <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Sélectionnez un dataset pour commencer l'analyse</p>
          </CardContent>
        </Card>
      )}

      {datasetId && !preview && (
        <LoadingSpinner text="Chargement de l'aperçu..." />
      )}

      {datasetId && preview && allColumns.length === 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-900">Aucune colonne détectée</p>
              <p className="text-sm text-red-700 mt-1">Vérifiez l'import ou sélectionnez un autre dataset.</p>
            </div>
          </div>
        </div>
      )}

      {datasetId && preview && allColumns.length > 0 && (
        <div className="space-y-6">
          {preview.incompatible_analyses && Object.keys(preview.incompatible_analyses).length > 0 && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-orange-900 mb-2">Analyses non disponibles:</p>
                  <ul className="text-sm text-orange-800 space-y-1">
                    {Object.entries(preview.incompatible_analyses).map(([analysis, reason]: [string, any]) => (
                      <li key={analysis}>
                        • <span className="font-medium">{analysis}:</span> {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {preview.row_count > 0 && (
            <Card className="border-blue-200 bg-blue-50/30">
              <CardContent className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div>
                    <p className="text-sm text-blue-600 font-medium mb-1">Lignes</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {preview.row_count.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-blue-600 font-medium mb-1">Colonnes numériques</p>
                    <p className="text-2xl font-bold text-blue-900">{numericColumns.length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-blue-600 font-medium mb-1">Colonnes catégorielles</p>
                    <p className="text-2xl font-bold text-blue-900">{categoricalColumns.length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-blue-600 font-medium mb-1">Analyses compatibles</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {preview.compatible_analyses?.length || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-2 lg:grid-cols-3">
              <TabsTrigger value="descriptive">
                <BarChart3 className="w-4 h-4 mr-2" />
                Descriptif
              </TabsTrigger>
              <TabsTrigger value="regression">
                <LineChart className="w-4 h-4 mr-2" />
                Régression
              </TabsTrigger>
              <TabsTrigger value="pca">
                <PieChart className="w-4 h-4 mr-2" />
                ACP
              </TabsTrigger>
            </TabsList>

            <TabsContent value="descriptive" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Statistiques descriptives</CardTitle>
                </CardHeader>
                <CardContent>
                  <DescriptivePanel
                    datasetId={datasetId}
                    columns={allColumns}
                    onResult={setLastResult}
                  />
                </CardContent>
              </Card>
              <GeminiPanel analysisType="descriptive" analysisData={lastResult} />
            </TabsContent>

            <TabsContent value="regression" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Régression linéaire</CardTitle>
                </CardHeader>
                <CardContent>
                  <RegressionPanel
                    datasetId={datasetId}
                    columns={allColumns}
                    numericColumns={numericColumns}
                    onResult={setLastResult}
                  />
                </CardContent>
              </Card>
              <GeminiPanel analysisType="regression" analysisData={lastResult} />
            </TabsContent>

            <TabsContent value="pca" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Analyse en Composantes Principales (ACP)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center p-8 text-muted-foreground">
                    <PieChart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>ACP disponible prochainement</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  )
}
