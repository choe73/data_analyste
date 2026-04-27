import { useState } from 'react'
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

async function apiFetch(path: string, body?: object) {
  const r = await fetch(`${API}${path}`, {
    method: body ? 'POST' : 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed', '#0891b2']

// ─── Descriptive Panel ───────────────────────────────────────────────────────
function DescriptivePanel({ datasetId, columns }: { datasetId: number; columns: string[] }) {
  const [selected, setSelected] = useState<string[]>(columns.slice(0, 6))
  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/descriptive', {
      dataset_id: datasetId, columns: selected, confidence_level: 0.95,
    }),
  })

  const stats: any[] = mut.data?.statistics || []
  const corr: any = mut.data?.correlations
  const plot: any = mut.data?.plot_data

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm font-medium">Colonnes:</span>
        {columns.map(c => (
          <Badge
            key={c}
            variant={selected.includes(c) ? 'default' : 'outline'}
            className="cursor-pointer"
            onClick={() => setSelected(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}
          >{c}</Badge>
        ))}
        <Button size="sm" onClick={() => mut.mutate()} disabled={mut.isPending || selected.length === 0}>
          {mut.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
          Analyser
        </Button>
      </div>

      {mut.isError && <p className="text-red-500 text-sm flex gap-1"><AlertCircle className="w-4 h-4" />{String(mut.error)}</p>}

      {stats.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-muted">
                {['Colonne','N','Moyenne','Médiane','Écart-type','Min','Max','IC 95%','Asymétrie'].map(h => (
                  <th key={h} className="px-3 py-2 text-left font-medium border">{h}</th>
                ))}
              </tr>
            </thead>
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
          {Object.entries(plot.histograms).slice(0, 4).map(([col, vals]: [string, any]) => {
            const bins = buildHistogram(vals, 15)
            return (
              <Card key={col}>
                <CardHeader className="pb-2"><CardTitle className="text-sm">{col}</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={160}>
                    <BarChart data={bins}>
                      <XAxis dataKey="label" tick={{ fontSize: 10 }} />
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

      {corr && (
        <Card>
          <CardHeader><CardTitle className="text-sm">Matrice de corrélation (Pearson)</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="text-xs border-collapse">
                <thead>
                  <tr>
                    <th className="px-2 py-1 border bg-muted"></th>
                    {corr.columns.map((c: string) => <th key={c} className="px-2 py-1 border bg-muted">{c}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {corr.columns.map((row: string, i: number) => (
                    <tr key={row}>
                      <td className="px-2 py-1 border font-medium bg-muted">{row}</td>
                      {corr.values[i].map((v: number, j: number) => (
                        <td key={j} className="px-2 py-1 border text-center" style={{ background: corrColor(v) }}>
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

// ─── Regression Panel ────────────────────────────────────────────────────────
function RegressionPanel({ datasetId, columns }: { datasetId: number; columns: string[] }) {
  const [target, setTarget] = useState('')
  const [features, setFeatures] = useState<string[]>([])
  const [method, setMethod] = useState('linear')

  const mut = useMutation({
    mutationFn: () => apiFetch('/api/v1/analysis/regression', {
      dataset_id: datasetId, target_column: target, feature_columns: features,
      method, test_size: 0.2, alpha: 1.0,
    }),
  })
  const res: any = mut.data

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="text-sm font-medium block mb-1">Variable cible (Y)</label>
          <Select value={target} onValueChange={setTarget}>
            <SelectTrigger><SelectValue placeholder="Choisir Y" /></SelectTrigger>
            <SelectContent>{columns.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Méthode</label>
          <Select value={method} onValueChange={setMethod}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {['linear','ridge','lasso','elasticnet'].map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-end">
          <Button onClick={() => mut.mutate()} disabled={!target || features.length === 0 || mut.isPending} className="w-full">
            {mut.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null} Calculer
          </Button>
        </div>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">Variables explicatives (X) — cliquer pour sélectionner</label>
        <div className="flex flex-wrap gap-2">
          {columns.filter(c => c !== target).map(c => (
            <Badge key={c} variant={features.includes(c) ? 'default' : 'outline'} className="cursor-pointer"
              onClick={() => setFeatures(p => p.includes(c) ? p.filter(x => x !== c) : [...p, c])}>
              {c}
            </Badge>
          ))}
        </div>
      </div>

      {mut.isError && <p className="text-red-500 text-sm">{String(mut.error)}</p>}

      {res && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'R²', value: res.metrics?.r2_score, good: v => v > 0.7 },
              { label: 'R² ajusté', value: res.metrics?.adjusted_r2, good: v => v > 0.7 },
              { label: 'RMSE', value: res.metrics?.rmse, good: () => true },
              { label: 'MAE', value: res.metrics?.mae, good: () => true },
            ].map(({ label, value, good }) => (
              <Card key={label}>
                <CardContent className="p-3 text-center">
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className={`text-xl font-bold ${value != null && good(value) ? 'text-green-600' : 'text-orange-500'}`}>
                    {value?.toFixed(4) ?? '—'}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader><CardTitle className="text-sm">Coefficients</CardTitle></CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <thead><tr className="bg-muted"><th className="px-3 py-1 text-left border">Variable</th><th className="px-3 py-1 border">Coefficient</th><th className="px-3 py-1 border">VIF</th></tr></thead>
                <tbody>
                  <tr><td className="px-3 py-1 border font-medium">Constante</td><td className="px-3 py-1 border">{res.intercept?.toFixed(6)}</td><td className="px-3 py-1 border">—</td></tr>
                  {res.coefficients?.map((c: any) => (
                    <tr key={c.name} className={c.vif > 10 ? 'bg-orange-50' : ''}>
                      <td className="px-3 py-1 border">{c.name}</td>
                      <td className="px-3 py-1 border">{c.value?.toFixed(6)}</td>
                      <td className="px-3 py-1 border">{c.vif ? (c.vif > 10 ? <span className="text-orange-600 font-medium">{c.vif.toFixed(1)} ⚠</span> : c.vif.toFixed(1)) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {res.diagnostics?.durbin_watson && (
                <p className="text-xs text-muted-foreground mt-2">Durbin-Watson: {res.diagnostics.durbin_watson} (2 = pas d'autocorrélation)</p>
              )}
            </CardContent>
          </Card>

          {res.plot_data?.scatter && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Valeurs réelles vs prédites</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="x" name="Prédit" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="y" name="Réel" tick={{ fontSize: 11 }} />
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
