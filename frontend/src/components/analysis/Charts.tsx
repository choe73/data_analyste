import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, LineChart, Line, Legend, PieChart, Pie,
} from 'recharts'

export function HistogramChart({ data, title }: { data: any; title: string }) {
  if (!data || !data.bins) return null
  const chartData = data.bins.map((bin: number, i: number) => ({
    bin: bin.toFixed(2),
    count: data.counts[i],
  }))
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">{title}</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="bin" tick={{ fontSize: 9 }} />
            <YAxis tick={{ fontSize: 9 }} />
            <Tooltip />
            <Bar dataKey="count" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function BoxplotChart({ data, title }: { data: any; title: string }) {
  if (!data) return null
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">{title}</CardTitle></CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          <div className="grid grid-cols-2 gap-2">
            <div>Min: <span className="font-mono">{data.min?.toFixed(2)}</span></div>
            <div>Q1: <span className="font-mono">{data.q1?.toFixed(2)}</span></div>
            <div className="font-medium">Médiane: <span className="font-mono">{data.median?.toFixed(2)}</span></div>
            <div>Q3: <span className="font-mono">{data.q3?.toFixed(2)}</span></div>
            <div>Max: <span className="font-mono">{data.max?.toFixed(2)}</span></div>
            <div>Moyenne: <span className="font-mono">{data.mean?.toFixed(2)}</span></div>
          </div>
          {data.outliers && data.outliers.length > 0 && (
            <div className="text-xs text-orange-600">Valeurs aberrantes: {data.outliers.length}</div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export function ScatterPlotChart({ data }: { data: any }) {
  if (!data || !data.x || !data.y) return null
  const chartData = data.x.map((x: number, i: number) => ({ x, y: data.y[i] }))
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Nuage de points</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" name={data.x_label || 'X'} tick={{ fontSize: 10 }} />
            <YAxis dataKey="y" name={data.y_label || 'Y'} tick={{ fontSize: 10 }} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter data={chartData} fill="#2563eb" />
          </ScatterChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function PieChart2({ data, title }: { data: any; title: string }) {
  if (!data || data.length === 0) return null
  const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed', '#0891b2']
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">{title}</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
              {data.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function CorrelationCircle({ loadings, variance }: { loadings: any; variance: any }) {
  if (!loadings || loadings.length === 0) return null
  const chartData = loadings[0].map((val: number, i: number) => ({
    name: `Var${i}`,
    x: val,
    y: loadings[1]?.[i] || 0,
  }))
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Cercle de corrélation (ACP)</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" type="number" domain={[-1, 1]} tick={{ fontSize: 10 }} />
            <YAxis dataKey="y" type="number" domain={[-1, 1]} tick={{ fontSize: 10 }} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter data={chartData} fill="#2563eb" />
          </ScatterChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function FeatureImportanceChart({ data }: { data: any }) {
  if (!data || Object.keys(data).length === 0) return null
  const chartData = Object.entries(data)
    .map(([name, value]) => ({ name, value: Number(value) }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10)
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Importance des variables</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tick={{ fontSize: 9 }} />
            <YAxis dataKey="name" type="category" tick={{ fontSize: 9 }} width={100} />
            <Tooltip />
            <Bar dataKey="value" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function ClusterVisualization({ data }: { data: any }) {
  if (!data || !data.x || !data.y) return null
  const chartData = data.x.map((x: number, i: number) => ({
    x,
    y: data.y[i],
    cluster: data.labels?.[i] || 0,
  }))
  const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed', '#0891b2', '#f59e0b', '#06b6d4']
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Visualisation des clusters</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" tick={{ fontSize: 10 }} />
            <YAxis dataKey="y" tick={{ fontSize: 10 }} />
            <Tooltip />
            <Scatter data={chartData} fill="#2563eb">
              {chartData.map((_: any, i: number) => (
                <Cell key={i} fill={COLORS[chartData[i].cluster % COLORS.length]} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function AverageProfileChart({ data }: { data: any }) {
  if (!data || data.length === 0) return null
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Profil moyen par cluster</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 9 }} />
            <YAxis tick={{ fontSize: 9 }} />
            <Tooltip />
            <Legend />
            {Object.keys(data[0] || {})
              .filter(k => k !== 'name')
              .map((key, i) => (
                <Bar key={key} dataKey={key} fill={['#2563eb', '#16a34a', '#dc2626'][i % 3]} />
              ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
