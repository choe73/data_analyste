import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'

interface FormFieldData {
  field_type: string
  label: string
  placeholder?: string
  required: boolean
  options?: string[]
  order: number
}

const FIELD_TYPES = [
  { value: 'text', label: 'Texte court' },
  { value: 'textarea', label: 'Texte long' },
  { value: 'number', label: 'Numérique' },
  { value: 'select', label: 'Liste déroulante' },
  { value: 'multiselect', label: 'Sélection multiple' },
  { value: 'date', label: 'Date' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Téléphone' },
  { value: 'rating', label: 'Note (1-5)' },
  { value: 'file', label: 'Fichier' },
]

const DOMAINS = [
  'agriculture', 'sante', 'education', 'commerce', 'environnement',
  'infrastructure', 'demographie', 'economie', 'social', 'autre',
]

export default function FormBuilderPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [domain, setDomain] = useState('')
  const [fields, setFields] = useState<FormFieldData[]>([])
  const [saving, setSaving] = useState(false)

  const addField = () => {
    setFields([...fields, {
      field_type: 'text',
      label: '',
      required: false,
      order: fields.length,
    }])
  }

  const updateField = (index: number, updates: Partial<FormFieldData>) => {
    const newFields = [...fields]
    newFields[index] = { ...newFields[index], ...updates }
    setFields(newFields)
  }

  const removeField = (index: number) => {
    setFields(fields.filter((_, i) => i !== index).map((f, i) => ({ ...f, order: i })))
  }

  const handleSave = async () => {
    if (!title || !domain) {
      toast({ title: 'Erreur', description: 'Titre et domaine requis', variant: 'destructive' })
      return
    }
    if (fields.length === 0) {
      toast({ title: 'Erreur', description: 'Ajoutez au moins un champ', variant: 'destructive' })
      return
    }

    setSaving(true)
    try {
      const res = await fetch('/api/v1/forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title,
          description,
          domain,
          fields: fields.map(f => ({
            ...f,
            options: f.field_type === 'select' || f.field_type === 'multiselect'
              ? f.options?.map(o => ({ value: o, label: o }))
              : undefined,
          })),
        }),
      })
      if (res.ok) {
        const data = await res.json()
        toast({ title: 'Formulaire créé !' })
        navigate(`/forms/${data.id}`)
      } else {
        const err = await res.json()
        toast({ title: 'Erreur', description: err.detail || 'Création échouée', variant: 'destructive' })
      }
    } catch {
      toast({ title: 'Erreur réseau', variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Créer un formulaire</h1>
          <p className="text-muted-foreground">Construisez votre formulaire de collecte de données</p>
        </div>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Création...' : 'Créer le formulaire'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Informations générales</CardTitle>
          <CardDescription>Titre, description et domaine de votre formulaire</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Titre *</Label>
              <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Ex: Enquête prix marchés" />
            </div>
            <div className="space-y-2">
              <Label>Domaine *</Label>
              <Select value={domain} onValueChange={setDomain}>
                <SelectTrigger><SelectValue placeholder="Choisir un domaine" /></SelectTrigger>
                <SelectContent>
                  {DOMAINS.map(d => (
                    <SelectItem key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Décrivez l'objectif de ce formulaire..." />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Champs du formulaire</CardTitle>
            <CardDescription>{fields.length} champ(s) défini(s)</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={addField}>+ Ajouter un champ</Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {fields.length === 0 && (
            <p className="text-center text-muted-foreground py-8">
              Cliquez sur "Ajouter un champ" pour commencer
            </p>
          )}
          {fields.map((field, index) => (
            <div key={index} className="border rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <Badge variant="secondary">Champ {index + 1}</Badge>
                <Button variant="ghost" size="sm" onClick={() => removeField(index)}>Supprimer</Button>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">Type</Label>
                  <Select value={field.field_type} onValueChange={v => updateField(index, { field_type: v })}>
                    <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {FIELD_TYPES.map(t => (
                        <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Libellé</Label>
                  <Input className="h-9" value={field.label} onChange={e => updateField(index, { label: e.target.value })} placeholder="Nom du champ" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Placeholder</Label>
                  <Input className="h-9" value={field.placeholder || ''} onChange={e => updateField(index, { placeholder: e.target.value })} placeholder="Indice..." />
                </div>
              </div>
              {(field.field_type === 'select' || field.field_type === 'multiselect') && (
                <div className="space-y-1">
                  <Label className="text-xs">Options (séparées par des virgules)</Label>
                  <Input
                    value={field.options?.join(', ') || ''}
                    onChange={e => updateField(index, {
                      options: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
                    })}
                    placeholder="Option 1, Option 2, Option 3"
                  />
                </div>
              )}
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={field.required}
                  onChange={e => updateField(index, { required: e.target.checked })}
                />
                Obligatoire
              </label>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
