import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Beef } from 'lucide-react'
import axios from 'axios'

export default function CreateSchoolPage() {
  const navigate = useNavigate()
  const [schoolName, setSchoolName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      await axios.post(
        '/api/schools/',
        { name: schoolName },
        { headers: { Authorization: `Bearer ${token}` } },
      )

      // Update token (since school_id is now in it)
      // For simplicity in this demo, we'll just re-login or use the same token
      // In a real app, the backend might return a new token or we'd refresh it.

      navigate('/dashboard')
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else {
        setError('Failed to create school')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
            <Beef className="h-10 w-10" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Name Your School</h2>
          <p className="mt-2 text-sm text-gray-600">
            One last step to set up your tracking platform.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-gray-700">School Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Willow Creek Equestrian"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500"
              value={schoolName}
              onChange={(e) => setSchoolName(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Creating school...' : 'Create School & Start Tracking'}
          </button>
        </form>
      </div>
    </div>
  )
}
