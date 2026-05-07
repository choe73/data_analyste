import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { BarChart3, LineChart, PieChart, Activity, Loader2, AlertCircle, Brain } from 'lucide-react'
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
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed', '#0891b2']

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
  clean.forEach(v => { const i = Math.min(Math.floor((v - min) / step), bins - 1); counts[i]++ })
  return counts.map((count, i) => ({ label: (min + i * step).toFixed(1), count }))
}

function DescriptivePanel({ datasetId, columns, onResult }: { datasetId: number; columns: string[]; onResult?: (data: any) => void }) {
  const [selected, setSelected] = useState<string[]>(columns.slice(0, 6))
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/descriptive', {
      dataset_id: datasetId, columns: selected, confidence_level: 0.95,
    }),
    onSuccess: (data) => onResult?.(data),
  })
  const stats: any[] = mut.data?.statistics || []
  const corr: any = mut.data?.correlations
  const plot: any = mut.data?.plot_data
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm font-medium">Colonnes:</span>
        {columns.map(c => (
          <Badge key={c} variant={selected.includes(c) ? 'default' : 'outline'} className="cursor-pointer"
            onClick={() => setSelected(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}>{c}</Badge>
        ))}
        <Button size="sm" onClick={() => mut.mutate()} disabled={mut.isPending || selected.length === 0}>
          {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-1" />}Analyser
        </Button>
      </div>
      {mut.isError && <p className="text-red-500 text-sm flex gap-1"><AlertCircle className="w-4 h-4" />{String(mut.error)}</p>}
      {stats.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead><tr className="bg-muted">
              {['Colonne','N','Moyenne','Mediane','Ecart-type','Min','Max','IC 95%','Asymetrie'].map(h => (
                <th key={h} className="px-3 py-2 text-left font-medium border">{h}</th>
              ))}
            </tr></thead>
            <tbody>
              {stats.map((s: any) => (
                <tr key={s.column} className="hover:bg-muted/50">
                  <td className="px-3 py-1 border font-medium">{s.column}</td>
                  <td className="px-3 py-1 border">{s.count}</td>
                  <td className="px-3 py-1 border">{s.mean?.toFixed(3)}</td>
                  <td className="px-3 py-1 border">{s.median?.toFixed(3)}</td>
                  <td className="px-3 py-1 border">{s.std?.toFixed(3)}</td>
                  <td className="px-3 py-1 border">{s.min?.toFixed(3)}</td>
                  <td className="px-3 py-1 border">{s.max?.toFixed(3)}</td>
                  <td className="px-3 py-1 border text-xs">[{s.ci_lower?.toFixed(2)}, {s.ci_upper?.toFixed(2)}]</td>
                  <td className="px-3 py-1 border">{s.skewness?.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {plot?.histograms && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(plot.histograms).slice(0, 4).map(([col, vals]: [string, any]) => (
            <Card key={col}>
              <CardHeader className="pb-2"><CardTitle className="text-sm">{col}</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={buildHistogram(vals, 15)}>
                    <XAxis dataKey="label" tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} />
                    <Tooltip /><Bar dataKey="count" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
      {corr && (
        <Card>
          <CardHeader><CardTitle className="text-sm">Matrice de correlation (Pearson)</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="text-xs border-collapse">
                <thead><tr><th className="px-2 py-1 border bg-muted"></th>
                  {corr.columns.map((c: string) => <th key={c} className="px-2 py-1 border bg-muted">{c}</th>)}
                </tr></thead>
                <tbody>
                  {corr.columns.map((row: string, i: number) => (
                    <tr key={row}>
                      <td className="px-2 py-1 border font-medium bg-muted">{row}</td>
                      {corr.values[i].map((v: number, j: number) => (
                        <td key={j} className="px-2 py-1 border text-center" style={{ background: corrColor(v) }}>{v.toFixed(2)}</td>
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

function RegressionPanel({ datasetId, columns, onResult, numericColumns = [] }: { datasetId: number; columns: string[]; onResult?: (data: any) => void; numericColumns?: string[] }) {
  const [target, setTarget] = useState('')
  const [features, setFeatures] = useState<string[]>([])
  const [method, setMethod] = useState('linear')
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/regression', {
      dataset_id: datasetId, target_column: target, feature_columns: features, method, test_size: 0.2, alpha: 1.0,
    }),
    onSuccess: (data) => onResult?.(data),
  })
  const res: any = mut.data
  const targetOptions = numericColumns.length > 0 ? numericColumns : columns.filter(c => c && c.trim() !== '')
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="text-sm font-medium block mb-1">Variable cible (Y)</label>
          <Select value={target} onValueChange={setTarget}>
            <SelectTrigger><SelectValue placeholder="Choisir Y" /></SelectTrigger>
            <SelectContent>{targetOptions.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Methode</label>
          <Select value={method} onValueChange={setMethod}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {['linear','ridge','lasso','elasticnet'].map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-end">
          <Button onClick={() => mut.mutate()} disabled={!target || features.length === 0 || mut.isPending} className="w-full">
            {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-1" />}Calculer
          </Button>
        </div>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">Variables explicatives (X)</label>
        <div className="flex flex-wrap gap-2">
          {columns.filter(c => c !== target).map(c => (
            <Badge key={c} variant={features.includes(c) ? 'default' : 'outline'} className="cursor-pointer"
              onClick={() => setFeatures(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}>{c}</Badge>
          ))}
        </div>
      </div>
      {mut.isError && <p className="text-red-500 text-sm">{String(mut.error)}</p>}
      {res && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[{label:'R2',value:res.metrics?.r2_score},{label:'R2 ajuste',value:res.metrics?.adjusted_r2},{label:'RMSE',value:res.metrics?.rmse},{label:'MAE',value:res.metrics?.mae}].map(({label,value}) => (
              <Card key={label}><CardContent className="p-3 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className={`text-xl font-bold ${value != null && value > 0.7 ? 'text-green-600' : 'text-orange-500'}`}>{value?.toFixed(4) ?? '---'}</p>
              </CardContent></Card>
            ))}
          </div>
          <Card>
            <CardHeader><CardTitle className="text-sm">Coefficients</CardTitle></CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <thead><tr className="bg-muted"><th className="px-3 py-1 text-left border">Variable</th><th className="px-3 py-1 border">Coefficient</th><th className="px-3 py-1 border">VIF</th></tr></thead>
                <tbody>
                  <tr><td className="px-3 py-1 border font-medium">Constante</td><td className="px-3 py-1 border">{res.intercept?.toFixed(6)}</td><td className="px-3 py-1 border">---</td></tr>
                  {res.coefficients?.map((c: any) => (
                    <tr key={c.name} className={c.vif > 10 ? 'bg-orange-50' : ''}>
                      <td className="px-3 py-1 border">{c.name}</td>
                      <td className="px-3 py-1 border">{c.value?.toFixed(6)}</td>
                      <td className="px-3 py-1 border">{c.vif ? (c.vif > 10 ? <span className="text-orange-600 font-medium">{c.vif.toFixed(1)} !</span> : c.vif.toFixed(1)) : '---'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {res.diagnostics?.durbin_watson && <p className="text-xs text-muted-foreground mt-2">Durbin-Watson: {res.diagnostics.durbin_watson}</p>}
            </CardContent>
          </Card>
          {res.plot_data?.scatter && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Valeurs reelles vs predites</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="x" name="Predit" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="y" name="Reel" tick={{ fontSize: 11 }} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter data={res.plot_data.scatter.x.map((x: number, i: number) => ({ x, y: res.plot_data.scatter.y[i] }))} fill="#2563eb" />
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

function PCAPanel({ datasetId, columns, onResult, numericColumns = [] }: { datasetId: number; columns: string[]; onResult?: (data: any) => void; numericColumns?: string[] }) {
  const [selected, setSelected] = useState<string[]>((numericColumns.length > 0 ? numericColumns : columns).slice(0, 5))
  const [method, setMethod] = useState('kaiser')
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/pca', { dataset_id: datasetId, columns: selected, standardize: true, method }),
    onSuccess: (data) => onResult?.(data),
  })
  const res: any = mut.data
  const selectableColumns = numericColumns.length > 0 ? numericColumns : columns
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm font-medium">Variables:</span>
        {selectableColumns.map(c => (
          <Badge key={c} variant={selected.includes(c) ? 'default' : 'outline'} className="cursor-pointer"
            onClick={() => setSelected(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}>{c}</Badge>
        ))}
      </div>
      <div className="flex gap-3 items-center">
        <Select value={method} onValueChange={setMethod}>
          <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="kaiser">Critere de Kaiser</SelectItem>
            <SelectItem value="variance_80">80% de variance</SelectItem>
            <SelectItem value="all">Toutes les composantes</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={() => mut.mutate()} disabled={selected.length < 2 || mut.isPending}>
          {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-1" />}Calculer ACP
        </Button>
      </div>
      {mut.isError && <p className="text-red-500 text-sm">{String(mut.error)}</p>}
      {res && (
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle className="text-sm">Variance expliquee</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={res.components?.map((c: any) => ({ name: `CP${c.component_number}`, variance: c.variance_explained_pct, cumul: c.cumulative_variance_pct }))}>
                  <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} />
                  <Tooltip /><Legend />
                  <Bar dataKey="variance" name="Variance %" fill="#2563eb" />
                  <Line type="monotone" dataKey="cumul" name="Cumule %" stroke="#dc2626" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm">Loadings</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead><tr className="bg-muted">
                    <th className="px-3 py-1 border text-left">Variable</th>
                    {res.components?.map((c: any) => <th key={c.component_number} className="px-3 py-1 border">CP{c.component_number} ({c.variance_explained_pct}%)</th>)}
                  </tr></thead>
                  <tbody>
                    {selected.map(v => (
                      <tr key={v} className="hover:bg-muted/50">
                        <td className="px-3 py-1 border font-medium">{v}</td>
                        {res.components?.map((c: any) => {
                          const val = c.loadings?.[v] ?? 0
                          return <td key={c.component_number} className="px-3 py-1 border text-center" style={{ background: corrColor(val) }}>{val.toFixed(3)}</td>
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
          {res.biplot_data?.scores?.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Projection individus (CP1 vs CP2)</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={280}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="x" tick={{ fontSize: 11 }} /><YAxis dataKey="y" tick={{ fontSize: 11 }} /><Tooltip />
                    <Scatter data={res.biplot_data.scores.slice(0, 200).map((s: number[]) => ({ x: s[0], y: s[1] ?? 0 }))} fill="#2563eb" opacity={0.6} />
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

function ClassificationPanel({ datasetId, columns, onResult, categoricalColumns = [] }: { datasetId: number; columns: string[]; onResult?: (data: any) => void; categoricalColumns?: string[] }) {
  const [target, setTarget] = useState('')
  const [features, setFeatures] = useState<string[]>([])
  const [algo, setAlgo] = useState('random_forest')
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/classification', {
      dataset_id: datasetId, target_column: target, feature_columns: features, algorithm: algo, test_size: 0.2, cv_folds: 5,
    }),
    onSuccess: (data) => onResult?.(data),
  })
  const res: any = mut.data
  const targetOptions = categoricalColumns.length > 0 ? categoricalColumns : columns.filter(c => c && c.trim() !== '')
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="text-sm font-medium block mb-1">Variable cible</label>
          <Select value={target} onValueChange={setTarget}>
            <SelectTrigger><SelectValue placeholder="Choisir la cible" /></SelectTrigger>
            <SelectContent>{targetOptions.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Algorithme</label>
          <Select value={algo} onValueChange={setAlgo}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {['logistic','random_forest','gradient_boosting','svm','knn','naive_bayes'].map(a => <SelectItem key={a} value={a}>{a}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-end">
          <Button onClick={() => mut.mutate()} disabled={!target || features.length === 0 || mut.isPending} className="w-full">
            {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-1" />}Entrainer
          </Button>
        </div>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">Features (X)</label>
        <div className="flex flex-wrap gap-2">
          {columns.filter(c => c !== target).map(c => (
            <Badge key={c} variant={features.includes(c) ? 'default' : 'outline'} className="cursor-pointer"
              onClick={() => setFeatures(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}>{c}</Badge>
          ))}
        </div>
      </div>
      {mut.isError && <p className="text-red-500 text-sm">{String(mut.error)}</p>}
      {res && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[{label:'Accuracy',value:res.overall_metrics?.accuracy},{label:'Precision',value:res.overall_metrics?.precision},{label:'Recall',value:res.overall_metrics?.recall},{label:'F1-Score',value:res.overall_metrics?.f1_score}].map(({label,value}) => (
              <Card key={label}><CardContent className="p-3 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className={`text-xl font-bold ${value > 0.8 ? 'text-green-600' : value > 0.6 ? 'text-orange-500' : 'text-red-500'}`}>{value != null ? (value * 100).toFixed(1) + '%' : '---'}</p>
              </CardContent></Card>
            ))}
          </div>
          {res.confusion_matrix?.matrix && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Matrice de confusion</CardTitle></CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="text-sm border-collapse">
                    <thead><tr><th className="px-2 py-1 border bg-muted">Reel \ Predit</th>
                      {res.confusion_matrix.labels.map((l: string) => <th key={l} className="px-2 py-1 border bg-muted">{l}</th>)}
                    </tr></thead>
                    <tbody>
                      {res.confusion_matrix.matrix.map((row: number[], i: number) => (
                        <tr key={i}>
                          <td className="px-2 py-1 border font-medium bg-muted">{res.confusion_matrix.labels[i]}</td>
                          {row.map((v: number, j: number) => (
                            <td key={j} className="px-2 py-1 border text-center font-medium"
                              style={{ background: i === j ? '#dcfce7' : v > 0 ? '#fee2e2' : 'white' }}>{v}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
          {res.feature_importances && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Importance des variables</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={Object.entries(res.feature_importances).sort((a: any, b: any) => b[1] - a[1]).map(([k, v]: any) => ({ name: k, value: v }))}>
                    <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} /><Tooltip />
                    <Bar dataKey="value" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

function ClusteringPanel({ datasetId, columns, onResult, numericColumns = [] }: { datasetId: number; columns: string[]; onResult?: (data: any) => void; numericColumns?: string[] }) {
  const [selected, setSelected] = useState<string[]>((numericColumns.length > 0 ? numericColumns : columns).slice(0, 4))
  const [algo, setAlgo] = useState('kmeans')
  const [method, setMethod] = useState('auto')
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/clustering', { dataset_id: datasetId, columns: selected, algorithm: algo, method }),
    onSuccess: (data) => onResult?.(data),
  })
  const res: any = mut.data
  const selectableColumns = numericColumns.length > 0 ? numericColumns : columns
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm font-medium">Variables:</span>
        {selectableColumns.map(c => (
          <Badge key={c} variant={selected.includes(c) ? 'default' : 'outline'} className="cursor-pointer"
            onClick={() => setSelected(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}>{c}</Badge>
        ))}
      </div>
      <div className="flex gap-3 flex-wrap items-center">
        <Select value={algo} onValueChange={setAlgo}>
          <SelectTrigger className="w-44"><SelectValue /></SelectTrigger>
          <SelectContent>{['kmeans','dbscan','hierarchical','gmm'].map(a => <SelectItem key={a} value={a}>{a}</SelectItem>)}</SelectContent>
        </Select>
        <Select value={method} onValueChange={setMethod}>
          <SelectTrigger className="w-44"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="auto">Auto (silhouette)</SelectItem>
            <SelectItem value="elbow">Methode du coude</SelectItem>
            <SelectItem value="silhouette">Score silhouette</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={() => mut.mutate()} disabled={selected.length < 2 || mut.isPending}>
          {mut.isPending && <Loader2 className="w-4 h-4 animate-spin mr-1" />}Clusteriser
        </Button>
      </div>
      {mut.isError && <p className="text-red-500 text-sm">{String(mut.error)}</p>}
      {res && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[{label:'Clusters',value:res.n_clusters,fmt:(v:number)=>String(v)},{label:'Silhouette',value:res.metrics?.silhouette_score,fmt:(v:number)=>v?.toFixed(3)},{label:'Calinski-H.',value:res.metrics?.calinski_harabasz_score,fmt:(v:number)=>v?.toFixed(1)},{label:'Davies-B.',value:res.metrics?.davies_bouldin_score,fmt:(v:number)=>v?.toFixed(3)}].map(({label,value,fmt}) => (
              <Card key={label}><CardContent className="p-3 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-xl font-bold text-blue-600">{value != null ? fmt(value) : '---'}</p>
              </CardContent></Card>
            ))}
          </div>
          {res.cluster_visualization && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Visualisation des clusters</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={280}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="x" tick={{ fontSize: 11 }} /><YAxis dataKey="y" tick={{ fontSize: 11 }} /><Tooltip />
                    <Scatter data={res.cluster_visualization.x.map((x: number, i: number) => ({ x, y: res.cluster_visualization.y[i], cluster: res.cluster_visualization.labels[i] }))} fill="#2563eb">
                      {res.cluster_visualization.x.map((_: any, i: number) => <Cell key={i} fill={COLORS[res.cluster_visualization.labels[i] % COLORS.length]} />)}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
          {res.elbow_plot_data && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Methode du coude</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={180}>
                  <RLineChart data={res.elbow_plot_data.k.map((k: number, i: number) => ({ k, inertia: res.elbow_plot_data.inertia[i] }))}>
                    <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="k" tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} /><Tooltip />
                    <Line type="monotone" dataKey="inertia" stroke="#2563eb" dot />
                  </RLineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

function GeminiPanel({ analysisType, analysisData }: { analysisType: string; analysisData: any }) {
  const [question, setQuestion] = useState('')
  const [domain, setDomain] = useState('')
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/interpret', {
      analysis_type: analysisType, analysis_data: analysisData,
      user_question: question || undefined, domain_hint: domain || undefined,
    }),
  })
  const res: any = mut.data
  if (!analysisData) return null
  return (
    <Card className="border-purple-200 bg-purple-50/30">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Brain className="w-4 h-4 text-purple-600" />
          Interpretation IA {res?.persona ? `-- ${res.persona}` : '-- Expert Gemini'}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex gap-2 flex-wrap">
          <Select value={domain} onValueChange={setDomain}>
            <SelectTrigger className="w-44 h-8 text-xs"><SelectValue placeholder="Domaine (auto)" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="auto">Auto-detection</SelectItem>
              {['sante','agriculture','finance','entrepreneuriat','education','environnement'].map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
            </SelectContent>
          </Select>
          <input className="flex-1 border rounded px-3 py-1.5 text-sm min-w-[200px]"
            placeholder="Question specifique (optionnel)..." value={question} onChange={e => setQuestion(e.target.value)} />
          <Button size="sm" variant="outline" onClick={() => mut.mutate()} disabled={mut.isPending}>
            {mut.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Interpreter'}
          </Button>
        </div>
        {res && (
          <div className="space-y-2 text-sm">
            {res.domain && <p className="text-xs text-purple-600 font-medium">Domaine: {res.domain} | Expert: {res.persona}</p>}
            <p className="text-gray-700">{res.interpretation}</p>
            {res.key_findings?.length > 0 && (
              <div><p className="font-medium text-purple-700">Points cles:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {res.key_findings.map((f: string, i: number) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            )}
            {res.recommendations?.length > 0 && (
              <div><p className="font-medium text-purple-700">Recommandations:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {res.recommendations.map((r: string, i: number) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}
            {res.warnings?.length > 0 && <div className="bg-orange-50 border border-orange-200 rounded p-2"><p className="text-xs text-orange-700">{res.warnings.join(' ')}</p></div>}
            {res.quota_remaining != null && <p className="text-xs text-muted-foreground">Quota restant: {res.quota_remaining}/heure</p>}
          </div>
        )}
        {mut.isError && <p className="text-red-500 text-xs">{String(mut.error)}</p>}
      </CardContent>
    </Card>
  )
}

export function Analysis() {
  const [datasetId, setDatasetId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState('descriptive')
  const [lastResult, setLastResult] = useState<any>(null)
  const [preview, setPreview] = useState<any>(null)

  const { data: datasets = [] } = useQuery<Dataset[]>({
    queryKey: ['datasets'],
    queryFn: () => apiFetch('/api/v1/datasets'),
  })
  
  // Fetch preview when dataset changes
  useEffect(() => {
    if (datasetId) {
      apiFetch(`/api/v1/analysis/preview/${datasetId}`)
        .then(data => setPreview(data))
        .catch(() => setPreview(null))
    } else {
      setPreview(null)
    }
  }, [datasetId])
  
  // Use columns from preview if available, otherwise from dataset
  const selectedDataset: any = datasets.find((d: any) => String(d.id) === String(datasetId))
  const colTypes: Record<string, string> = selectedDataset?.column_types || {}
  const allColumns: string[] = selectedDataset?.columns || []
  
  // Get numeric and categorical columns from preview
  const numericColumns = preview?.columns?.numeric || []
  const categoricalColumns = preview?.columns?.categorical || []
  
  // Use numeric columns from preview if available, otherwise filter from dataset
  const columns: string[] = numericColumns.length > 0 
    ? numericColumns 
    : (allColumns.length > 0 && Object.keys(colTypes).length > 0
        ? allColumns.filter((c: string) => ['number', 'numeric', 'float', 'int', 'integer'].includes(colTypes[c]))
        : allColumns)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analyse de donnees</h1>
        <p className="text-muted-foreground">Statistiques descriptives, regression, ACP, classification, clustering</p>
      </div>
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <span className="text-sm font-medium whitespace-nowrap">Dataset:</span>
            <Select value={datasetId ? String(datasetId) : ''} onValueChange={v => setDatasetId(Number(v))}>
              <SelectTrigger className="w-full sm:w-[380px]">
                <SelectValue placeholder="Selectionner un dataset ou import" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((d: Dataset) => (
                  <SelectItem key={d.id} value={String(d.id)}>{d.name} -- {d.row_count.toLocaleString()} lignes</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedDataset && (
              <div className="flex gap-2 text-xs text-muted-foreground">
                <Badge variant="outline">{selectedDataset.row_count?.toLocaleString()} lignes</Badge>
                <Badge variant="outline">{allColumns.length} colonnes</Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      {!datasetId && (
        <Card className="border-dashed">
          <CardContent className="p-8 text-center text-muted-foreground">
            Selectionnez un dataset. Importez vos donnees via la page "Import".
          </CardContent>
        </Card>
      )}
      {datasetId && allColumns.length === 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="p-4 text-orange-700 text-sm">
            Aucune colonne détectée. Vérifiez l'import ou sélectionnez un autre dataset.
          </CardContent>
        </Card>
      )}
      {datasetId && allColumns.length > 0 && (
        <div className="space-y-4">
          {preview?.incompatible_analyses && Object.keys(preview.incompatible_analyses).length > 0 && (
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="p-4">
                <p className="text-sm font-medium text-orange-900 mb-2">Analyses non disponibles pour ce dataset:</p>
                <ul className="text-sm text-orange-800 space-y-1">
                  {Object.entries(preview.incompatible_analyses).map(([analysis, reason]: [string, any]) => (
                    <li key={analysis}>• <span className="font-medium">{analysis}:</span> {reason}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
          {preview && (
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-blue-600 font-medium">Lignes</p>
                    <p className="text-lg font-bold text-blue-900">{preview.row_count?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-blue-600 font-medium">Colonnes numeriques</p>
                    <p className="text-lg font-bold text-blue-900">{preview.columns?.numeric?.length || 0}</p>
                  </div>
                  <div>
                    <p className="text-blue-600 font-medium">Colonnes categoriques</p>
                    <p className="text-lg font-bold text-blue-900">{preview.columns?.categorical?.length || 0}</p>
                  </div>
                  <div>
                    <p className="text-blue-600 font-medium">Analyses compatibles</p>
                    <p className="text-lg font-bold text-blue-900">{preview.compatible_analyses?.length || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
      {datasetId && allColumns.length > 0 && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5">
            <TabsTrigger value="descriptive"><BarChart3 className="w-4 h-4 mr-1" />Descriptif</TabsTrigger>
            <TabsTrigger value="regression"><LineChart className="w-4 h-4 mr-1" />Regression</TabsTrigger>
            <TabsTrigger value="pca"><PieChart className="w-4 h-4 mr-1" />ACP</TabsTrigger>
            <TabsTrigger value="classification"><Activity className="w-4 h-4 mr-1" />Classification</TabsTrigger>
            <TabsTrigger value="clustering"><BarChart3 className="w-4 h-4 mr-1" />Clustering</TabsTrigger>
          </TabsList>
          <TabsContent value="descriptive">
            <Card><CardHeader><CardTitle>Statistiques descriptives</CardTitle></CardHeader>
              <CardContent className="space-y-4"><DescriptivePanel datasetId={datasetId} columns={columns} onResult={setLastResult} />
                <GeminiPanel analysisType="descriptive" analysisData={lastResult} /></CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="regression">
            <Card><CardHeader><CardTitle>Regression lineaire</CardTitle></CardHeader>
              <CardContent className="space-y-4"><RegressionPanel datasetId={datasetId} columns={columns} onResult={setLastResult} numericColumns={numericColumns} />
                <GeminiPanel analysisType="regression" analysisData={lastResult} /></CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="pca">
            <Card><CardHeader><CardTitle>Analyse en Composantes Principales (ACP)</CardTitle></CardHeader>
              <CardContent className="space-y-4"><PCAPanel datasetId={datasetId} columns={columns} onResult={setLastResult} numericColumns={numericColumns} />
                <GeminiPanel analysisType="pca" analysisData={lastResult} /></CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="classification">
            <Card><CardHeader><CardTitle>Classification supervisee</CardTitle></CardHeader>
              <CardContent className="space-y-4"><ClassificationPanel datasetId={datasetId} columns={columns} onResult={setLastResult} categoricalColumns={categoricalColumns} />
                <GeminiPanel analysisType="classification" analysisData={lastResult} /></CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="clustering">
            <Card><CardHeader><CardTitle>Clustering non supervise</CardTitle></CardHeader>
              <CardContent className="space-y-4"><ClusteringPanel datasetId={datasetId} columns={columns} onResult={setLastResult} numericColumns={numericColumns} />
                <GeminiPanel analysisType="clustering" analysisData={lastResult} /></CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
