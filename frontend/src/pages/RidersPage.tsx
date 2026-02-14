import { useState, useEffect } from 'react'
import {
  Search,
  Plus,
  Edit2,
  Trash2,
  X,
  User,
  Ruler,
  Weight,
  Calendar,
  Mail,
} from 'lucide-react'
import axios from 'axios'
import { RiderResponse } from '../types'

export default function RidersPage() {
  const [riders, setRiders] = useState<RiderResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRider, setEditingRider] = useState<RiderResponse | null>(null)

  // Form State
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [dob, setDob] = useState('')

  useEffect(() => {
    fetchRiders()
  }, [])

  const fetchRiders = async () => {
    try {
      setLoading(true)
      const res = await axios.get('/api/riders/')
      setRiders(res.data)
    } catch (error) {
      console.error('Failed to fetch riders', error)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (rider?: RiderResponse) => {
    if (rider) {
      setEditingRider(rider)
      setFirstName(rider.first_name)
      setLastName(rider.last_name)
      setEmail(rider.email || '')
      setHeight(rider.height_cm?.toString() || '')
      setWeight(rider.weight_kg?.toString() || '')
      setDob(rider.date_of_birth || '')
    } else {
      setEditingRider(null)
      setFirstName('')
      setLastName('')
      setEmail('')
      setHeight('')
      setWeight('')
      setDob('')
    }
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingRider(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const payload = {
        first_name: firstName,
        last_name: lastName,
        email: email || undefined,
        height_cm: height ? parseFloat(height) : undefined,
        weight_kg: weight ? parseFloat(weight) : undefined,
        date_of_birth: dob || undefined,
      }

      if (editingRider) {
        // Update
        const res = await axios.put<RiderResponse>(`/api/riders/${editingRider.id}`, payload)
        setRiders(riders.map((r) => (r.id === editingRider.id ? res.data : r)))
      } else {
        // Create
        const res = await axios.post<RiderResponse>('/api/riders/', payload)
        setRiders([...riders, res.data])
      }
      handleCloseModal()
    } catch (error) {
      console.error('Failed to save rider', error)
      alert('Failed to save rider. Please check inputs.')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to remove this rider?')) return
    try {
      await axios.delete(`/api/riders/${id}`)
      setRiders(riders.filter((r) => r.id !== id))
    } catch (error) {
      console.error('Failed to delete rider', error)
      alert('Failed to delete rider.')
    }
  }

  const calculateAge = (dobString: string | null) => {
    if (!dobString) return '-'
    const birthDate = new Date(dobString)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const m = today.getMonth() - birthDate.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    return age
  }

  const filteredRiders = riders.filter((rider) =>
    `${rider.first_name} ${rider.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  return (
    <div className="p-8 flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Riders Administration</h1>
          <p className="text-gray-600 mt-1">Manage all riders in your school.</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition shadow-sm"
        >
          <Plus className="w-5 h-5" />
          <span>Add Rider</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search riders by name..."
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        {/* Placeholder for future filters */}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex-1">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Age
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Height
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Weight
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    Loading riders...
                  </td>
                </tr>
              ) : filteredRiders.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500 italic">
                    No riders found matching your search.
                  </td>
                </tr>
              ) : (
                filteredRiders.map((rider) => (
                  <tr key={rider.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm mr-3">
                          {rider.first_name[0]}
                          {rider.last_name[0]}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">
                            {rider.first_name} {rider.last_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {rider.email || <span className="text-gray-400 italic">No email</span>}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {calculateAge(rider.date_of_birth)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {rider.height_cm ? `${rider.height_cm} cm` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {rider.weight_kg ? `${rider.weight_kg} kg` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleOpenModal(rider)}
                          className="text-gray-400 hover:text-blue-600 p-1 rounded-md hover:bg-blue-50 transition"
                          title="Edit"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(rider.id)}
                          className="text-gray-400 hover:text-red-600 p-1 rounded-md hover:bg-red-50 transition"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <h3 className="text-lg font-bold text-gray-900">
                {editingRider ? 'Edit Rider' : 'Add New Rider'}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-full p-1 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700">First Name</label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      required
                      className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                      placeholder="Jane"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700">Last Name</label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      required
                      className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                      placeholder="Doe"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">
                  Email Address (Optional)
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <input
                    type="email"
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                    placeholder="jane@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <p className="text-xs text-gray-500">
                  Required if the rider needs to log in. Leave blank for managed profiles (e.g.,
                  children).
                </p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700">Height (cm)</label>
                  <div className="relative">
                    <Ruler className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <input
                      type="number"
                      step="0.1"
                      className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                      placeholder="165"
                      value={height}
                      onChange={(e) => setHeight(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700">Weight (kg)</label>
                  <div className="relative">
                    <Weight className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <input
                      type="number"
                      step="0.1"
                      className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                      placeholder="60"
                      value={weight}
                      onChange={(e) => setWeight(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700">Date of Birth</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <input
                      type="date"
                      className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                      value={dob}
                      onChange={(e) => setDob(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition shadow-sm"
                >
                  {editingRider ? 'Update Rider' : 'Create Rider'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
