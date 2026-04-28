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

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <ErrorBoundary>
      <Routes>
        {/* Public routes - no layout */}
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/f/:shareToken" element={<PublicForm />} />

        {/* Protected app routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/datasets" element={<Datasets />} />
                  <Route path="/analysis" element={<Analysis />} />
                  <Route path="/collection" element={<DataCollection />} />
                  <Route path="/models" element={<Models />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/forms" element={<FormsList />} />
                  <Route path="/forms/new" element={<FormBuilder />} />
                  <Route path="/import" element={<DataImportPage />} />
                  <Route path="/import/:importId" element={<ImportResults />} />
                </Routes>
              </MainLayout>
              <CookieConsent />
              <Toaster />
            </>
          </ProtectedRoute>
        } />

        {/* Catch-all for protected routes */}
        <Route path="/*" element={
          <ProtectedRoute>
            <>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/datasets" element={<Datasets />} />
                  <Route path="/analysis" element={<Analysis />} />
                  <Route path="/collection" element={<DataCollection />} />
                  <Route path="/models" element={<Models />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/forms" element={<FormsList />} />
                  <Route path="/forms/new" element={<FormBuilder />} />
                  <Route path="/import" element={<DataImportPage />} />
                  <Route path="/import/:importId" element={<ImportResults />} />
                </Routes>
              </MainLayout>
              <CookieConsent />
              <Toaster />
            </>
          </ProtectedRoute>
        } />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
