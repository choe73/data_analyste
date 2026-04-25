import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface FormFieldData {
  id: number
  field_type: string
  label: string
  placeholder?: string
  required: boolean
  options?: { value: string; label: string }[]
  order: number
}

interface PublicFormData {
  title: string
  description?: string
  domain: string
  fields: FormFieldData[]
}

export default function PublicFormPage() {
  const { shareToken } = useParams<{ shareToken: string }>()
  const [form, setForm] = useState<PublicFormData | null>(null)
  const [responses, setResponses] = useState<Record<string, unknown>>({})
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/v1/public/forms/${shareToken}`)
      .then(res => {
        if (!res.ok) throw new Error('Not found')
        return res.json()
      })
      .then(data => setForm(data))
      .catch(() => setError('Ce formulaire n\'existe pas ou n\'est plus disponible'))
      .finally(() => setLoading(false))
  }, [shareToken])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await fetch(`/api/v1/public/forms/${shareToken}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses }),
      })
      if (res.ok) {
        setSubmitted(true)
      } else {
        const err = await res.json()
        setError(err.detail || 'Erreur lors de la soumission')
      }
    } catch {
      setError('Erreur réseau')
    }
  }

  if (loading) return <div className="flex items-center justify-center min-h-screen"><p>Chargement...</p></div>
  if (error && !form) return <div className="flex items-center justify-center min-h-screen"><p className="text-red-500">{error}</p></div>
  if (submitted) return (
    <div className="flex items-center justify-center min-h-screen">
      <Card className="max-w-md">
        <CardContent className="py-8 text-center">
          <p className="text-xl font-semibold text-green-600 mb-2">Merci !</p>
          <p className="text-muted-foreground">Votre réponse a été enregistrée avec succès.</p>
        </CardContent>
      </Card>
    </div>
  )

  if (!form) return null

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">{form.title}</CardTitle>
          {form.description && <CardDescription>{form.description}</CardDescription>}
          <Badge variant="secondary" className="w-fit">{form.domain}</Badge>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            {form.fields.sort((a, b) => a.order - b.order).map(field => (
              <div key={field.id} className="space-y-2">
                <Label>
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </Label>
                {field.field_type === 'text' && (
                  <Input
                    placeholder={field.placeholder}
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value })}
                    required={field.required}
                  />
                )}
                {field.field_type === 'textarea' && (
                  <Textarea
                    placeholder={field.placeholder}
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value })}
                    required={field.required}
                  />
                )}
                {field.field_type === 'number' && (
                  <Input
                    type="number"
                    placeholder={field.placeholder}
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value ? Number(e.target.value) : null })}
                    required={field.required}
                  />
                )}
                {field.field_type === 'email' && (
                  <Input
                    type="email"
                    placeholder={field.placeholder}
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value })}
                    required={field.required}
                  />
                )}
                {field.field_type === 'phone' && (
                  <Input
                    type="tel"
                    placeholder={field.placeholder || '+237 XXX XXX XXX'}
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value })}
                    required={field.required}
                  />
                )}
                {field.field_type === 'date' && (
                  <Input
                    type="date"
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value })}
                    required={field.required}
                  />
                )}
                {field.field_type === 'rating' && (
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setResponses({ ...responses, [field.id]: star })}
                        className={`text-2xl ${responses[field.id] >= star ? 'text-yellow-500' : 'text-gray-300'}`}
                      >
                        &#9733;
                      </button>
                    ))}
                  </div>
                )}
                {(field.field_type === 'select' || field.field_type === 'multiselect') && (
                  <select
                    className="w-full border rounded-md p-2 bg-background"
                    value={(responses[field.id] as string) || ''}
                    onChange={e => setResponses({ ...responses, [field.id]: e.target.value })}
                    required={field.required}
                    multiple={field.field_type === 'multiselect'}
                  >
                    <option value="">-- Choisir --</option>
                    {field.options?.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                )}
                {field.field_type === 'file' && (
                  <Input
                    type="file"
                    onChange={e => {
                      const f = e.target.files?.[0]
                      if (f) setResponses({ ...responses, [field.id]: f.name })
                    }}
                    required={field.required}
                  />
                )}
              </div>
            ))}
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <Button type="submit" className="w-full">Soumettre</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
