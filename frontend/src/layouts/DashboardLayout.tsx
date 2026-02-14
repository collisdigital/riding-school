import { useState, useEffect } from 'react'
import { ChessKnight, Users, Star, GraduationCap, LogOut, LayoutDashboard } from 'lucide-react'
import { useNavigate, Outlet, useLocation } from 'react-router-dom'
import axios from 'axios'

export default function DashboardLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [schoolName, setSchoolName] = useState('Loading...')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userRes = await axios.get('/api/auth/me')
        if (userRes.data.school) {
          setSchoolName(userRes.data.school.name)
        }
      } catch {
        // ignore
      }
    }
    fetchData()
  }, [])

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout')
    } catch {
      // Ignore logout errors
    }
    localStorage.removeItem('authenticated')
    navigate('/login')
  }

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { name: 'Riders', icon: Users, path: '/dashboard/riders' },
    { name: 'Grades', icon: Star, path: '/dashboard/grades' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
        <div className="p-6 flex items-center space-x-2 text-xl font-bold text-blue-600 border-b border-gray-100">
          <ChessKnight className="w-6 h-6" />
          <span>Tracker</span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <div className="bg-blue-50 text-blue-600 flex items-center space-x-3 p-3 rounded-lg font-medium">
            <GraduationCap className="w-5 h-5" />
            <span className="truncate">{schoolName}</span>
          </div>

          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <div
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`flex items-center space-x-3 p-3 rounded-lg font-medium cursor-pointer transition ${
                  isActive ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </div>
            )
          })}
        </nav>
        <div className="p-4 border-t border-gray-100">
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 p-3 text-gray-600 hover:text-red-600 transition font-medium"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
