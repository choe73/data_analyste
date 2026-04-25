import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'

interface DataImportItem {
  id: number
  original_filename: string
  file_format: string
  row_count: number
  analysis_status: string
  created_at: string
}

export default function DataImportPage() {
  const [imports, setImports] = useState<DataImportItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const { toast } = useToast()

  const fetchImports = () => {
    fetch('/api/v1/imports', { credentials: 'include' })
      .then(res => res.ok ? res.json() : [])
      .then(data => setImports(data))
      .catch(() => setImports([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchImports() }, [])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['csv', 'xlsx', 'xls', 'json', 'geojson'].includes(ext || '')) {
      toast({ title: 'Format non supporté', description: 'Utilisez CSV, Excel, JSON ou GeoJSON', variant: 'destructive' })
      return
    }

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/v1/imports/upload', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      })
      if (res.ok) {
        const data = await res.json()
        toast({ title: 'Fichier importé !', description: `${data.row_count} lignes détectées` })
        fetchImports()
      } else {
        const err = await res.json()
        toast({ title: 'Erreur', description: err.detail || 'Import échoué', variant: 'destructive' })
      }
    } catch {
      toast({ title: 'Erreur réseau', variant: 'destructive' })
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleAnalyze = async (importId: number) => {
    try {
      const res = await fetch(`/api/v1/imports/${importId}/analyze`, {
        method: 'POST',
        credentials: 'include',
      })
      if (res.ok) {
        toast({ title: 'Analyse lancée !' })
        fetchImports()
      } else {
        toast({ title: 'Erreur', variant: 'destructive' })
      }
    } catch {
      toast({ title: 'Erreur réseau', variant: 'destructive' })
    }
  }

  const statusLabel: Record<string, { text: string; variant: 'default' | 'secondary' | 'destructive' }> = {
    uploaded: { text: 'Uploadé', variant: 'secondary' },
    confirmed: { text: 'Confirmé', variant: 'default' },
    pending: { text: 'En attente', variant: 'secondary' },
    completed: { text: 'Analysé', variant: 'default' },
    failed: { text: 'Échoué', variant: 'destructive' },
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Import de Données</h1>
          <p className="text-muted-foreground">Importez vos données et obtenez une analyse automatique</p>
        </div>
        <label>
          <Button asChild disabled={uploading}>
            <span>{uploading ? 'Upload en cours...' : '+ Importer un fichier'}</span>
          </Button>
          <input type="file" className="hidden" accept=".csv,.xlsx,.xls,.json,.geojson" onChange={handleUpload} />
        </label>
      </div>

      {loading ? (
        <p className="text-muted-foreground">Chargement...</p>
      ) : imports.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-2">Aucune donnée importée</p>
            <p className="text-sm text-muted-foreground">Importez un fichier CSV, Excel ou JSON pour commencer</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {imports.map(imp => {
            const st = statusLabel[imp.analysis_status] || statusLabel.pending
            return (
              <Card key={imp.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{imp.original_filename}</CardTitle>
                    <Badge variant={st.variant}>{st.text}</Badge>
                  </div>
                  <CardDescription>
                    {imp.file_format.toUpperCase()} · {imp.row_count.toLocaleString()} lignes
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    {imp.analysis_status === 'uploaded' && (
                      <Button size="sm" onClick={() => handleAnalyze(imp.id)}>
                        Lancer l'analyse
                      </Button>
                    )}
                    {imp.analysis_status === 'completed' && (
                      <Link to={`/import/${imp.id}`}>
                        <Button size="sm" variant="outline">Voir les résultats</Button>
                      </Link>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={async () => {
                        await fetch(`/api/v1/imports/${imp.id}`, { method: 'DELETE', credentials: 'include' })
                        fetchImports()
                      }}
                    >
                      Supprimer
                    </Button>
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
