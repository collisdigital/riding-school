import { useState, useEffect } from 'react'
import { ChessKnight, Users, Star, GraduationCap, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [riders, setRiders] = useState<{ id: string; first_name: string; last_name: string }[]>([])
  const [schoolName, setSchoolName] = useState('Loading...')
  const [newRiderFirstName, setNewRiderFirstName] = useState('')
  const [newRiderLastName, setNewRiderLastName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userRes = await axios.get('/api/auth/me')
        if (userRes.data.school) {
          setSchoolName(userRes.data.school.name)
        }

        const ridersRes = await axios.get('/api/riders/')
        setRiders(ridersRes.data)
      } catch {
        // ignore
      }
    }
    fetchData()
  }, [])

  const handleAddRider = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await axios.post('/api/riders/', {
        first_name: newRiderFirstName,
        last_name: newRiderLastName,
      })
      setRiders([...riders, res.data])
      setNewRiderFirstName('')
      setNewRiderLastName('')
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else {
        setError('Failed to add rider')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout')
    } catch {
      // Ignore logout errors
    }
    localStorage.removeItem('authenticated')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
        <div className="p-6 flex items-center space-x-2 text-xl font-bold text-blue-600 border-b border-gray-100">
          <ChessKnight className="w-6 h-6" />
          <span>Tracker</span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <div className="bg-blue-50 text-blue-600 flex items-center space-x-3 p-3 rounded-lg font-medium cursor-pointer">
            <GraduationCap className="w-5 h-5" />
            <span>{schoolName}</span>
          </div>
          <div className="text-gray-600 hover:bg-gray-50 flex items-center space-x-3 p-3 rounded-lg font-medium cursor-pointer transition">
            <Users className="w-5 h-5" />
            <span>Riders</span>
          </div>
          <div className="text-gray-600 hover:bg-gray-50 flex items-center space-x-3 p-3 rounded-lg font-medium cursor-pointer transition">
            <Star className="w-5 h-5" />
            <span>Grades</span>
          </div>
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
      <main className="flex-1 p-8">
        <header className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome to your riding school tracker.</p>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">
              Total Riders
            </div>
            <div className="text-4xl font-bold text-gray-900">{riders.length}</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">
              Active Grades
            </div>
            <div className="text-4xl font-bold text-gray-900">5</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">
              Pending Graduations
            </div>
            <div className="text-4xl font-bold text-gray-900">0</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <h2 className="text-xl font-bold mb-6">Add Rider</h2>
            <form onSubmit={handleAddRider} className="space-y-4">
              {error && (
                <div
                  className="bg-red-50 text-red-600 p-3 rounded-md text-sm"
                  role="alert"
                  aria-live="polite"
                >
                  {error}
                </div>
              )}
              <div>
                <label
                  htmlFor="rider-first-name"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Rider First Name
                </label>
                <input
                  id="rider-first-name"
                  type="text"
                  placeholder="e.g. Jane"
                  className="w-full border border-gray-300 rounded-lg p-3 focus:ring-blue-500 focus:border-blue-500"
                  value={newRiderFirstName}
                  onChange={(e) => setNewRiderFirstName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label
                  htmlFor="rider-last-name"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Rider Last Name
                </label>
                <input
                  id="rider-last-name"
                  type="text"
                  placeholder="e.g. Doe"
                  className="w-full border border-gray-300 rounded-lg p-3 focus:ring-blue-500 focus:border-blue-500"
                  value={newRiderLastName}
                  onChange={(e) => setNewRiderLastName(e.target.value)}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Adding...
                  </>
                ) : (
                  'Add Rider'
                )}
              </button>
            </form>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <h2 className="text-xl font-bold mb-6">Riders List</h2>
            {riders.length === 0 ? (
              <p className="text-gray-500 italic">No riders added yet.</p>
            ) : (
              <ul className="space-y-3">
                {riders.map((rider) => (
                  <li
                    key={rider.id}
                    className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-100"
                  >
                    <Users className="w-5 h-5 text-blue-500" />
                    <span className="font-medium text-gray-900">
                      {rider.first_name} {rider.last_name}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
