import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { MainLayout } from '@/components/layout/MainLayout'
import { Dashboard } from '@/pages/Dashboard'
import { Datasets } from '@/pages/Datasets'
import { Analysis } from '@/pages/Analysis'
import { DataCollection } from '@/pages/DataCollection'
import { Models } from '@/pages/Models'
import { Settings } from '@/pages/Settings'
import { CookieConsent } from '@/components/CookieConsent'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useAuth } from '@/store/auth'
import FormsList from '@/pages/FormsList'
import FormBuilder from '@/pages/FormBuilder'
import DataImportPage from '@/pages/DataImport'
import ImportResults from '@/pages/ImportResults'
import PublicForm from '@/pages/PublicForm'
import LoginPage from '@/pages/Login'
import { LandingPage } from '@/pages/LandingPage'
import Pricing from '@/pages/Pricing'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <MainLayout>
        {children}
      </MainLayout>
      <CookieConsent />
      <Toaster />
    </ProtectedRoute>
  )
}

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <ErrorBoundary>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route path="/f/:shareToken" element={<PublicForm />} />

        {/* Protected routes - flat structure so direct URLs work */}
        <Route path="/dashboard" element={<AppShell><Dashboard /></AppShell>} />
        <Route path="/collection" element={<AppShell><DataCollection /></AppShell>} />
        <Route path="/datasets" element={<AppShell><Datasets /></AppShell>} />
        <Route path="/import" element={<AppShell><DataImportPage /></AppShell>} />
        <Route path="/import/:importId" element={<AppShell><ImportResults /></AppShell>} />
        <Route path="/forms" element={<AppShell><FormsList /></AppShell>} />
        <Route path="/forms/new" element={<AppShell><FormBuilder /></AppShell>} />
        <Route path="/analysis" element={<AppShell><Analysis /></AppShell>} />
        <Route path="/models" element={<AppShell><Models /></AppShell>} />
        <Route path="/pricing" element={<AppShell><Pricing /></AppShell>} />
        <Route path="/settings" element={<AppShell><Settings /></AppShell>} />

        {/* Legacy /dashboard/* redirects */}
        <Route path="/dashboard/pricing" element={<Navigate to="/pricing" replace />} />
        <Route path="/dashboard/analysis" element={<Navigate to="/analysis" replace />} />
        <Route path="/dashboard/collection" element={<Navigate to="/collection" replace />} />
        <Route path="/dashboard/datasets" element={<Navigate to="/datasets" replace />} />
        <Route path="/dashboard/import" element={<Navigate to="/import" replace />} />
        <Route path="/dashboard/forms" element={<Navigate to="/forms" replace />} />
        <Route path="/dashboard/models" element={<Navigate to="/models" replace />} />
        <Route path="/dashboard/settings" element={<Navigate to="/settings" replace />} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/"} replace />} />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
