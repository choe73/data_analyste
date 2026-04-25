import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'

interface FeedbackWidgetProps {
  analysisId?: number
  analysisType?: string
}

export function FeedbackWidget({ analysisId, analysisType }: FeedbackWidgetProps) {
  const [rating, setRating] = useState<number | null>(null)
  const [comment, setComment] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async () => {
    if (rating === null) return
    setLoading(true)
    try {
      const res = await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          analysis_id: analysisId,
          analysis_type: analysisType,
          rating,
          comment: comment || undefined,
          helpful: rating >= 4,
        }),
      })
      if (res.ok) {
        setSubmitted(true)
        toast({ title: 'Merci pour votre retour !' })
      }
    } catch (err) {
      toast({ title: 'Erreur', description: 'Impossible d envoyer le feedback', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="text-sm text-green-600 dark:text-green-400 py-2">
        Merci pour votre retour !
      </div>
    )
  }

  return (
    <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800 mt-4">
      <p className="text-sm font-medium mb-2">Ce resultat vous a-t-il ete utile ?</p>
      <div className="flex gap-2 mb-3">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className={`text-xl transition-colors ${
              rating !== null && star <= rating
                ? 'text-yellow-500'
                : 'text-gray-300 dark:text-gray-600 hover:text-yellow-400'
            }`}
            aria-label={`${star} etoiles`}
          >
            &#9733;
          </button>
        ))}
      </div>
      {rating !== null && (
        <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
          <Textarea
            placeholder="Commentaire optionnel..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="text-sm min-h-[60px]"
          />
          <Button size="sm" onClick={handleSubmit} disabled={loading}>
            Envoyer
          </Button>
        </div>
      )}
    </div>
  )
}
