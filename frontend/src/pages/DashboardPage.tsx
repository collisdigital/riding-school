import { useState, useEffect } from 'react'
import { Beef, Users, Star, GraduationCap, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [riders, setRiders] = useState<{id: string, first_name: string}[]>([])
  const [schoolName, setSchoolName] = useState('Loading...')
  const [newRiderName, setNewRiderName] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token')
        // We need an endpoint for the current user's school or similar
        // For now, let's assume we can get it from the user info or another call.
        // I will add a simple /api/auth/me to get the user and school info.
        const userRes = await axios.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (userRes.data.school) {
          setSchoolName(userRes.data.school.name)
        }

        const ridersRes = await axios.get('/api/riders/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setRiders(ridersRes.data)
      } catch (err) {}
    }
    fetchData()
  }, [])

  const handleAddRider = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const token = localStorage.getItem('token')
      const res = await axios.post('/api/riders/', 
        { first_name: newRiderName, last_name: 'Rider' },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setRiders([...riders, res.data])
      setNewRiderName('')
    } catch (err) {}
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
        <div className="p-6 flex items-center space-x-2 text-xl font-bold text-blue-600 border-b border-gray-100">
          <Beef className="w-6 h-6" />
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
            <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">Total Riders</div>
            <div className="text-4xl font-bold text-gray-900">{riders.length}</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">Active Grades</div>
            <div className="text-4xl font-bold text-gray-900">5</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">Pending Graduations</div>
            <div className="text-4xl font-bold text-gray-900">0</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <h2 className="text-xl font-bold mb-6">Add Rider</h2>
            <form onSubmit={handleAddRider} className="space-y-4">
              <input 
                type="text" 
                placeholder="Rider First Name"
                className="w-full border border-gray-300 rounded-lg p-3"
                value={newRiderName}
                onChange={(e) => setNewRiderName(e.target.value)}
                required
              />
              <button type="submit" className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg">
                Add Rider
              </button>
            </form>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <h2 className="text-xl font-bold mb-6">Riders List</h2>
            {riders.length === 0 ? (
              <p className="text-gray-500 italic">No riders added yet.</p>
            ) : (
              <ul className="space-y-3">
                {riders.map(rider => (
                  <li key={rider.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <Users className="w-5 h-5 text-blue-500" />
                    <span className="font-medium text-gray-900">{rider.first_name}</span>
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
