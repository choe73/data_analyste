import { Routes, Route } from 'react-router-dom'
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
import FormsList from '@/pages/FormsList'
import FormBuilder from '@/pages/FormBuilder'
import DataImportPage from '@/pages/DataImport'
import ImportResults from '@/pages/ImportResults'
import PublicForm from '@/pages/PublicForm'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
      {/* Public route - no layout */}
      <Route path="/f/:shareToken" element={<PublicForm />} />

      {/* App routes - with layout */}
      <Route path="/*" element={
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
      } />
    </Routes>
    </ErrorBoundary>
  )
}

export default App
