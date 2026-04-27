import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Download, BarChart3, Link2, Trash2, Globe, EyeOff } from 'lucide-react'
import { authFetch } from '@/store/auth'

const API = (import.meta.env.VITE_API_URL as string) || ''

async function apiFetch(path: string, opts?: RequestInit) {
  const r = await authFetch(path, opts)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

interface FormItem {
  id: number
  title: string
  domain: string
  is_published: boolean
  response_count: number
  share_token: string | null
  created_at: string
  fields: { id: number; label: string; field_type: string }[]
}

function FormAnalyticsPanel({ formId }: { formId: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['form-analytics', formId],
    queryFn: () => apiFetch(`/api/v1/forms/${formId}/analytics`),
  })

  if (isLoading) return <p className="text-xs text-muted-foreground">Chargement analytics...</p>
  if (!data) return null

  const fieldStats: Record<string, any> = data.field_stats || {}

  return (
    <div className="mt-3 space-y-3 border-t pt-3">
      <p className="text-sm font-medium">{data.total_responses} réponse(s) au total</p>
      {Object.entries(fieldStats).slice(0, 3).map(([field, stats]: [string, any]) => {
        if (stats.distribution) {
          const chartData = Object.entries(stats.distribution).map(([k, v]) => ({ name: k, count: v as number }))
          return (
            <div key={field}>
              <p className="text-xs font-medium text-muted-foreground mb-1">{field}</p>
              <ResponsiveContainer width="100%" height={100}>
                <BarChart data={chartData.slice(0, 8)}>
                  <XAxis dataKey="name" tick={{ fontSize: 9 }} />
                  <YAxis tick={{ fontSize: 9 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )
        }
        if (stats.mean !== undefined) {
          return (
            <div key={field} className="text-xs">
              <span className="font-medium">{field}:</span> moy={stats.mean?.toFixed(2)}, min={stats.min?.toFixed(2)}, max={stats.max?.toFixed(2)}
            </div>
          )
        }
        return null
      })}
    </div>
  )
}

export default function FormsListPage() {
  const { toast } = useToast()
  const qc = useQueryClient()
  const [expandedAnalytics, setExpandedAnalytics] = useState<number | null>(null)

  const { data: forms = [], isLoading } = useQuery<FormItem[]>({
    queryKey: ['forms'],
    queryFn: () => apiFetch('/api/v1/forms'),
  })

  const publishMut = useMutation({
    mutationFn: ({ id, publish }: { id: number; publish: boolean }) =>
      apiFetch(`/api/v1/forms/${id}/${publish ? 'publish' : 'unpublish'}`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['forms'] }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => apiFetch(`/api/v1/forms/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['forms'] })
      toast({ title: 'Formulaire supprimé' })
    },
  })

  const handleExport = (formId: number, format: 'csv' | 'json') => {
    window.open(`${API}/api/v1/forms/${formId}/responses/export?format=${format}`, '_blank')
  }

  const copyLink = (token: string) => {
    navigator.clipboard.writeText(`${window.location.origin}/f/${token}`)
    toast({ title: 'Lien copié !' })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Mes Formulaires</h1>
          <p className="text-muted-foreground">Gérez vos formulaires de collecte de données</p>
        </div>
        <Link to="/forms/new"><Button>+ Nouveau formulaire</Button></Link>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Chargement...</p>
      ) : forms.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">Vous n'avez pas encore créé de formulaire</p>
            <Link to="/forms/new"><Button>Créer votre premier formulaire</Button></Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {forms.map(form => (
            <Card key={form.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{form.title}</CardTitle>
                  <Badge variant={form.is_published ? 'default' : 'secondary'}>
                    {form.is_published ? 'Publié' : 'Brouillon'}
                  </Badge>
                </div>
                <CardDescription>{form.domain} · {form.fields?.length || 0} champ(s)</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{form.response_count} réponse(s)</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(form.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline" size="sm"
                    onClick={() => publishMut.mutate({ id: form.id, publish: !form.is_published })}
                    disabled={publishMut.isPending}
                  >
                    {form.is_published ? <><EyeOff className="w-3 h-3 mr-1" />Dépublier</> : <><Globe className="w-3 h-3 mr-1" />Publier</>}
                  </Button>

                  {form.is_published && form.share_token && (
                    <Button variant="outline" size="sm" onClick={() => copyLink(form.share_token!)}>
                      <Link2 className="w-3 h-3 mr-1" />Lien
                    </Button>
                  )}

                  {form.response_count > 0 && (
                    <>
                      <Button variant="outline" size="sm" onClick={() => setExpandedAnalytics(expandedAnalytics === form.id ? null : form.id)}>
                        <BarChart3 className="w-3 h-3 mr-1" />Stats
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleExport(form.id, 'csv')}>
                        <Download className="w-3 h-3 mr-1" />CSV
                      </Button>
                    </>
                  )}

                  <Button
                    variant="ghost" size="sm"
                    onClick={() => { if (confirm('Supprimer ce formulaire ?')) deleteMut.mutate(form.id) }}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>

                {/* Analytics inline */}
                {expandedAnalytics === form.id && <FormAnalyticsPanel formId={form.id} />}

                {/* Lien public */}
                {form.is_published && form.share_token && (
                  <div className="text-xs text-muted-foreground bg-muted rounded p-2 truncate">
                    {window.location.origin}/f/{form.share_token}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
