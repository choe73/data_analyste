import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { authFetch } from '@/store/auth'
import { Upload, AlertCircle, CheckCircle, Database } from 'lucide-react'

interface ColumnInfo {
  name: string
  type: string
  non_null_count: number
  null_count: number
  unique_count: number
}

interface DataImportItem {
  id: number
  name: string
  row_count: number
  column_count: number
  columns?: ColumnInfo[]
  created_at: string
}

export default function DataImportPage() {
  const [imports, setImports] = useState<DataImportItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] = useState<DataImportItem | null>(null)
  const { toast } = useToast()

  const fetchImports = () => {
    authFetch('/api/v1/imports')
      .then(res => res.ok ? res.json() : [])
      .then(data => setImports(Array.isArray(data) ? data : []))
      .catch(() => setImports([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchImports() }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['csv', 'xlsx', 'xls'].includes(ext || '')) {
      toast({ 
        title: 'Format non supporté', 
        description: 'Utilisez CSV ou Excel', 
        variant: 'destructive' 
      })
      return
    }
    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    
    setUploading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)
    
    try {
      const res = await authFetch('/api/v1/imports/upload', { 
        method: 'POST', 
        body: formData 
      })
      
      if (res.ok) {
        const data = await res.json()
        setUploadResult(data)
        toast({ 
          title: 'Fichier importé !', 
          description: `${data.row_count} lignes détectées` 
        })
        fetchImports()
        setSelectedFile(null)
      } else {
        const err = await res.json().catch(() => ({}))
        toast({ 
          title: 'Erreur', 
          description: err.detail || 'Import échoué', 
          variant: 'destructive' 
        })
      }
    } catch (error) {
      toast({ title: 'Erreur réseau', variant: 'destructive' })
    } finally {
      setUploading(false)
    }
  }

  const handleAnalyze = async (importId: number) => {
    try {
      const res = await authFetch(`/api/v1/imports/${importId}/analyze`, { method: 'POST' })
      if (res.ok) { 
        toast({ title: 'Analyse lancée !' })
        fetchImports() 
      }
      else toast({ title: 'Erreur', variant: 'destructive' })
    } catch { 
      toast({ title: 'Erreur réseau', variant: 'destructive' }) 
    }
  }

  const getTypeColor = (type: string) => {
    switch(type) {
      case 'numeric': return 'bg-blue-100 text-blue-800'
      case 'categorical': return 'bg-purple-100 text-purple-800'
      case 'text': return 'bg-green-100 text-green-800'
      case 'datetime': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Import de Données</h1>
        <p className="text-gray-600 mt-2">
          Importez vos fichiers CSV ou Excel pour une analyse automatique
        </p>
      </div>

      {/* Upload Area */}
      <Card className="p-8">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">
            Glissez-déposez votre fichier ou cliquez pour sélectionner
          </p>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm hover:bg-accent hover:text-accent-foreground cursor-pointer transition-colors"
          >
            Sélectionner un fichier
          </label>
        </div>

        {selectedFile && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm font-medium text-blue-900">
              Fichier sélectionné: {selectedFile.name}
            </p>
          </div>
        )}

        {selectedFile && !uploadResult && (
          <Button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full mt-4 bg-green-600"
          >
            {uploading ? 'Téléchargement...' : 'Télécharger et analyser'}
          </Button>
        )}
      </Card>

      {/* Upload Results */}
      {uploadResult && (
        <Card className="p-6 border-green-200 bg-green-50">
          <div className="flex items-start mb-4">
            <CheckCircle className="w-6 h-6 text-green-600 mr-3 flex-shrink-0" />
            <div>
              <h2 className="text-xl font-bold">{uploadResult.name}</h2>
              <p className="text-gray-600">
                {uploadResult.row_count} lignes × {uploadResult.column_count} colonnes
              </p>
            </div>
          </div>

          {/* Columns Info */}
          {uploadResult.columns && uploadResult.columns.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold mb-4">Colonnes détectées</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {uploadResult.columns.map((col) => (
                  <div key={col.name} className="p-4 border rounded-lg bg-white">
                    <div className="flex items-start justify-between mb-2">
                      <p className="font-medium">{col.name}</p>
                      <Badge className={getTypeColor(col.type)}>
                        {col.type}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>Non-null: {col.non_null_count}</p>
                      <p>Unique: {col.unique_count}</p>
                      {col.null_count > 0 && (
                        <p className="text-orange-600">Null: {col.null_count}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Button
            onClick={() => {
              setUploadResult(null)
              setSelectedFile(null)
            }}
            className="w-full mt-6"
            variant="outline"
          >
            Importer un autre fichier
          </Button>
        </Card>
      )}

      {/* Imports List */}
      {loading ? (
        <p className="text-gray-600">Chargement...</p>
      ) : imports.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Aucune donnée importée</p>
            <p className="text-sm text-gray-500">
              Importez un fichier CSV ou Excel pour commencer
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {imports.map(imp => (
            <Card key={imp.id}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{imp.name}</CardTitle>
                </div>
                <CardDescription>
                  {imp.row_count.toLocaleString()} lignes × {imp.column_count} colonnes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    onClick={() => handleAnalyze(imp.id)}
                    className="bg-green-600"
                  >
                    Analyser
                  </Button>
                  <Link to={`/import/${imp.id}`}>
                    <Button size="sm" variant="outline">
                      Voir les détails
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
