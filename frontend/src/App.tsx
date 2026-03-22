import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import Layout from '@/components/layout/Layout'
import LoginPage from '@/pages/LoginPage'
import SurveyPage from '@/pages/SurveyPage'
import DashboardRedirect from '@/pages/DashboardRedirect'
import AdminPage from '@/pages/AdminPage'
import CompaniesPage from '@/pages/CompaniesPage'
import CompanyFormPage from '@/pages/CompanyFormPage'
import CompanyDetailPage from '@/pages/CompanyDetailPage'
import UsersPage from '@/pages/UsersPage'
import CampaignsPage from '@/pages/CampaignsPage'
import CampaignFormPage from '@/pages/CampaignFormPage'
import CampaignDetailPage from '@/pages/CampaignDetailPage'
import CSVUploadPage from '@/pages/CSVUploadPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import ProfilePage from '@/pages/ProfilePage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route path="/survey" element={<SurveyPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardRedirect />} />
          <Route path="admin" element={<AdminPage />} />
          <Route path="admin/companies" element={<CompaniesPage />} />
          <Route path="admin/companies/new" element={<CompanyFormPage />} />
          <Route path="admin/companies/:id" element={<CompanyDetailPage />} />
          <Route path="admin/users" element={<UsersPage adminView />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="campaigns/new" element={<CampaignFormPage />} />
          <Route path="campaigns/:id" element={<CampaignDetailPage />} />
          <Route path="campaigns/:id/upload" element={<CSVUploadPage />} />
          <Route path="campaigns/:id/analytics" element={<AnalyticsPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
