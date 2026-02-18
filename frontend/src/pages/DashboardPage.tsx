import { useState, useEffect } from 'react'
import axios from 'axios'
import type { RiderResponse, Grade } from '../types'
import { useNavigate } from 'react-router-dom'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [riders, setRiders] = useState<RiderResponse[]>([])
  const [grades, setGrades] = useState<Grade[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ridersRes, gradesRes] = await Promise.all([
          axios.get('/api/riders/'),
          axios.get('/api/grades/'),
        ])
        setRiders(ridersRes.data)
        setGrades(gradesRes.data)
      } catch {
        // ignore
      }
    }
    fetchData()
  }, [])

  return (
    <div className="p-8">
      <header className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your riding school tracker.</p>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div
          onClick={() => navigate('/dashboard/riders')}
          className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:border-blue-200 transition-colors"
        >
          <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">
            Total Riders
          </div>
          <div className="text-4xl font-bold text-gray-900">{riders.length}</div>
        </div>
        <div
          onClick={() => navigate('/dashboard/grades')}
          className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:border-blue-200 transition-colors"
        >
          <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">
            Active Grades
          </div>
          <div className="text-4xl font-bold text-gray-900">{grades.length}</div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 opacity-70">
          <div className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wider">
            Pending Graduations
          </div>
          <div className="text-4xl font-bold text-gray-900">0</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
        <p className="text-gray-600">More charts and analytics coming soon.</p>
      </div>
    </div>
  )
}
