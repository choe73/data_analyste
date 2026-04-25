import { useState, useCallback } from 'react'

interface ConsentState {
  cookie_consent: boolean
  analytics_consent: boolean
  marketing_consent: boolean
}

export function useConsent() {
  const [consent, setConsent] = useState<ConsentState | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchConsent = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/consent/status', { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        setConsent(data)
      }
    } catch (err) {
      console.error('Failed to fetch consent', err)
    }
  }, [])

  const updateConsent = useCallback(async (payload: ConsentState) => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/consent/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })
      if (res.ok) {
        setConsent(payload)
      }
    } catch (err) {
      console.error('Failed to update consent', err)
    } finally {
      setLoading(false)
    }
  }, [])

  return { consent, loading, fetchConsent, updateConsent }
}
