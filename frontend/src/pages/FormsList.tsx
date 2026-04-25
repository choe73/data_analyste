import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface FormItem {
  id: number
  title: string
  domain: string
  is_published: boolean
  response_count: number
  share_token: string | null
  created_at: string
}

export default function FormsListPage() {
  const [forms, setForms] = useState<FormItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/forms', { credentials: 'include' })
      .then(res => res.ok ? res.json() : [])
      .then(data => setForms(data))
      .catch(() => setForms([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Mes Formulaires</h1>
          <p className="text-muted-foreground">Gérez vos formulaires de collecte de données</p>
        </div>
        <Link to="/forms/new">
          <Button>+ Nouveau formulaire</Button>
        </Link>
      </div>

      {loading ? (
        <p className="text-muted-foreground">Chargement...</p>
      ) : forms.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">Vous n'avez pas encore créé de formulaire</p>
            <Link to="/forms/new">
              <Button>Créer votre premier formulaire</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {forms.map(form => (
            <Card key={form.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{form.title}</CardTitle>
                  <Badge variant={form.is_published ? 'default' : 'secondary'}>
                    {form.is_published ? 'Publié' : 'Brouillon'}
                  </Badge>
                </div>
                <CardDescription>{form.domain}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {form.response_count} réponse(s)
                  </span>
                  <div className="flex gap-2">
                    <Link to={`/forms/${form.id}`}>
                      <Button variant="outline" size="sm">Voir</Button>
                    </Link>
                    {form.is_published && form.share_token && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          navigator.clipboard.writeText(
                            `${window.location.origin}/f/${form.share_token}`
                          )
                        }}
                      >
                        Copier lien
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
