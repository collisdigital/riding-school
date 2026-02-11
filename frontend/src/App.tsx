import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState<string>('Loading...')

  useEffect(() => {
    fetch('/api/')
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage('Error connecting to backend'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg text-center max-w-md w-full">
        <h1 className="text-3xl font-bold text-blue-600 mb-4">
          Riding School Tracker
        </h1>
        <p className="text-gray-600 text-lg mb-6">
          {message}
        </p>
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Welcome to the future of progress tracking for riders.
          </p>
          <div className="flex justify-center space-x-2">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
              Vite + React
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
              FastAPI
            </span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
              Tailwind v4
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
