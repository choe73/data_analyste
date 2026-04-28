import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, CheckCircle, Loader } from 'lucide-react'

export function CollectorDebug() {
  const [activeTest, setActiveTest] = useState<string | null>(null)
  const [results, setResults] = useState<Record<string, any>>({})
  const [logs, setLogs] = useState<Record<string, string[]>>({})
  const [loading, setLoading] = useState(false)

  const testCollector = async (source: string) => {
    setActiveTest(source)
    setLoading(true)
    setLogs(prev => ({ ...prev, [source]: ['Starting test...'] }))

    try {
      // Start debug collection
      const startRes = await fetch(`/api/v1/collect/collect-debug/${source}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      })
      const startData = await startRes.json()
      const taskId = startData.task_id

      // Poll for logs
      let completed = false
      let attempts = 0
      const maxAttempts = 60

      while (!completed && attempts < maxAttempts) {
        await new Promise(r => setTimeout(r, 1000))
        
        const logsRes = await fetch(`/api/v1/collect/collect-debug-logs/${taskId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        const logsData = await logsRes.json()

        setLogs(prev => ({ ...prev, [source]: logsData.logs }))
        setResults(prev => ({ ...prev, [source]: logsData }))

        if (logsData.status === 'completed' || logsData.status === 'failed') {
          completed = true
        }

        attempts++
      }

      setLoading(false)
    } catch (error) {
      setLogs(prev => ({
        ...prev,
        [source]: [...(prev[source] || []), `ERROR: ${error}`]
      }))
      setLoading(false)
    }
  }

  const testDiagnostics = async () => {
    setActiveTest('diagnostics')
    setLoading(true)

    try {
      const res = await fetch('/api/v1/diagnostics/test/all', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      })
      const data = await res.json()
      setResults(prev => ({ ...prev, diagnostics: data }))
      setLoading(false)
    } catch (error) {
      setResults(prev => ({ ...prev, diagnostics: { error: String(error) } }))
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Diagnostic Collecteurs</h1>
        <p className="text-muted-foreground">
          Testez les collecteurs de données et diagnostiquez les problèmes
        </p>
      </div>

      {/* Quick Tests */}
      <Card>
        <CardHeader>
          <CardTitle>Tests Rapides</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => testCollector('world_bank')}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && activeTest === 'world_bank' && (
                <Loader className="w-4 h-4 animate-spin" />
              )}
              Test World Bank
            </button>
            <button
              onClick={() => testCollector('nasa_power')}
              disabled={loading}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && activeTest === 'nasa_power' && (
                <Loader className="w-4 h-4 animate-spin" />
              )}
              Test NASA POWER
            </button>
            <button
              onClick={() => testCollector('fao')}
              disabled={loading}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-md disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && activeTest === 'fao' && (
                <Loader className="w-4 h-4 animate-spin" />
              )}
              Test FAO
            </button>
            <button
              onClick={testDiagnostics}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && activeTest === 'diagnostics' && (
                <Loader className="w-4 h-4 animate-spin" />
              )}
              Test Tous
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {Object.keys(results).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Résultats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(results).map(([source, result]) => (
              <div key={source} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold capitalize">{source}</h3>
                  {result.status === 'completed' ? (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Complété
                    </div>
                  ) : result.status === 'failed' ? (
                    <div className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      Erreur
                    </div>
                  ) : (
                    <div className="border border-gray-300 text-gray-700 px-3 py-1 rounded-full text-sm">
                      En cours...
                    </div>
                  )}
                </div>

                {logs[source] && logs[source].length > 0 && (
                  <div className="bg-gray-900 text-gray-100 p-3 rounded font-mono text-sm max-h-64 overflow-y-auto mb-3">
                    {logs[source].map((log, i) => (
                      <div key={i} className="text-xs">
                        {log.includes('ERROR') ? (
                          <span className="text-red-400">{log}</span>
                        ) : log.includes('✓') || log.includes('complete') ? (
                          <span className="text-green-400">{log}</span>
                        ) : (
                          <span>{log}</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {result.errors && result.errors.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded p-3">
                    {result.errors.map((err: string, i: number) => (
                      <p key={i} className="text-sm text-red-700">{err}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
