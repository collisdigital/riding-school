import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CreateSchoolPage from './pages/CreateSchoolPage'
import DashboardPage from './pages/DashboardPage'
import RidersPage from './pages/RidersPage'
import { ProtectedRoute } from './layouts/ProtectedRoute'
import DashboardLayout from './layouts/DashboardLayout'
import axios from 'axios'

// Configure axios to always send cookies
axios.defaults.withCredentials = true

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/onboarding/create-school"
          element={
            <ProtectedRoute>
              <CreateSchoolPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="riders" element={<RidersPage />} />
          {/* Add more routes here like 'grades' */}
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
