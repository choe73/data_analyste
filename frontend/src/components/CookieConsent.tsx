import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Switch } from '@/components/ui/switch'
import { useConsent } from '@/hooks/useConsent'

export function CookieConsent() {
  const { consent, updateConsent, loading } = useConsent()
  const [showBanner, setShowBanner] = useState(false)
  const [showCustomize, setShowCustomize] = useState(false)
  const [localConsent, setLocalConsent] = useState({
    cookie_consent: true,
    analytics_consent: false,
    marketing_consent: false,
  })

  useEffect(() => {
    const checkConsent = async () => {
      try {
        const res = await fetch('/api/v1/consent/status', { credentials: 'include' })
        if (res.ok) {
          const data = await res.json()
          if (data.cookie_consent || data.analytics_consent) {
            setShowBanner(false)
            return
          }
        }
        // Show banner if endpoint missing or no consent recorded
        const stored = localStorage.getItem('cookie_consent')
        setShowBanner(!stored)
      } catch {
        const stored = localStorage.getItem('cookie_consent')
        setShowBanner(!stored)
      }
    }
    checkConsent()
  }, [consent])

  const handleAcceptAll = async () => {
    localStorage.setItem('cookie_consent', 'all')
    await updateConsent({ cookie_consent: true, analytics_consent: true, marketing_consent: true }).catch(() => {})
    setShowBanner(false)
    setShowCustomize(false)
  }

  const handleRefuse = async () => {
    localStorage.setItem('cookie_consent', 'essential')
    await updateConsent({ cookie_consent: true, analytics_consent: false, marketing_consent: false }).catch(() => {})
    setShowBanner(false)
    setShowCustomize(false)
  }

  const handleCustomizeSave = async () => {
    localStorage.setItem('cookie_consent', 'custom')
    await updateConsent(localConsent).catch(() => {})
    setShowBanner(false)
    setShowCustomize(false)
  }

  if (!showBanner) return null

  return (
    <>
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg p-4 md:p-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
              Parametres des cookies
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Nous utilisons des cookies pour ameliorer votre experience. Conformement au RGPD
              et a la loi camerounaise sur la protection des donnees, vous pouvez personnaliser
              vos preferences.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowCustomize(true)}>
              Personnaliser
            </Button>
            <Button variant="secondary" size="sm" onClick={handleRefuse} disabled={loading}>
              Refuser
            </Button>
            <Button size="sm" onClick={handleAcceptAll} disabled={loading}>
              Accepter tout
            </Button>
          </div>
        </div>
      </div>

      <Dialog open={showCustomize} onOpenChange={setShowCustomize}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Personnaliser les cookies</DialogTitle>
            <DialogDescription>
              Choisissez les categories de cookies que vous acceptez.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Cookies essentiels</p>
                <p className="text-xs text-gray-500">Obligatoires pour le fonctionnement du site</p>
              </div>
              <Switch checked disabled />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Analytics</p>
                <p className="text-xs text-gray-500">Mesure d'audience et performance</p>
              </div>
              <Switch
                checked={localConsent.analytics_consent}
                onCheckedChange={(v) => setLocalConsent({ ...localConsent, analytics_consent: v })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Marketing</p>
                <p className="text-xs text-gray-500">Personnalisation et publicite</p>
              </div>
              <Switch
                checked={localConsent.marketing_consent}
                onCheckedChange={(v) => setLocalConsent({ ...localConsent, marketing_consent: v })}
              />
            </div>
          </div>

          <DialogFooter className="flex gap-2">
            <Button variant="outline" onClick={handleRefuse} disabled={loading}>
              Refuser tout
            </Button>
            <Button onClick={handleCustomizeSave} disabled={loading}>
              Enregistrer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
