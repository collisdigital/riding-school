import { useState, useEffect } from 'react'
import axios from 'axios'
import type { RiderResponse } from '../types'

export default function DashboardPage() {
  const [riders, setRiders] = useState<RiderResponse[]>([])

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

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
        <p className="text-gray-600">More charts and analytics coming soon.</p>
      </div>
    </div>
  )
}
