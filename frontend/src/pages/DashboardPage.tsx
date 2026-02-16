import { useState, useEffect } from 'react'
import { Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import type { RiderResponse } from '../types'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [riders, setRiders] = useState<RiderResponse[]>([])
  const [newRiderFirstName, setNewRiderFirstName] = useState('')
  const [newRiderLastName, setNewRiderLastName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
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

  return (
    <div className="p-8">
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
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
              <label htmlFor="rider-first-name" className="block text-sm font-medium text-gray-700 mb-1">
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
              <label htmlFor="rider-last-name" className="block text-sm font-medium text-gray-700 mb-1">
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

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
        <p className="text-gray-600">More charts and analytics coming soon.</p>
      </div>
    </div>
  )
}
