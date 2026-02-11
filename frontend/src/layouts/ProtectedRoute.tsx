import { Navigate } from 'react-router-dom'

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem('authenticated') === 'true'
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}
