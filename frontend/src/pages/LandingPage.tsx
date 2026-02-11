import { Link } from 'react-router-dom'
import { ChessKnight, ChevronRight, CheckCircle2 } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2 text-2xl font-bold text-blue-600">
          <ChessKnight className="w-8 h-8" />
          <span>Riding School Tracker</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link to="/login" className="text-gray-600 hover:text-blue-600 font-medium">
            Login
          </Link>
          <Link
            to="/register"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Register Your School
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 text-center lg:text-left lg:flex lg:items-center">
          <div className="lg:w-1/2 space-y-8">
            <h1 className="text-5xl lg:text-6xl font-extrabold text-gray-900 leading-tight">
              Track Rider Progress with <span className="text-blue-600">Precision.</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl">
              The all-in-one platform for riding schools to manage grades, track skills, and
              celebrate rider achievements. Professional, simple, and built for equestrians.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 justify-center lg:justify-start">
              <Link
                to="/register"
                className="flex items-center justify-center bg-blue-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-blue-700 transition"
              >
                Get Started Now <ChevronRight className="ml-2 w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="flex items-center justify-center border-2 border-gray-200 text-gray-600 px-8 py-4 rounded-xl font-bold text-lg hover:border-blue-600 hover:text-blue-600 transition"
              >
                View Live Demo
              </Link>
            </div>
            <div className="flex items-center space-x-6 justify-center lg:justify-start text-sm text-gray-500">
              <div className="flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-2 text-green-500" /> No credit card required
              </div>
              <div className="flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-2 text-green-500" /> 14-day free trial
              </div>
            </div>
          </div>
          <div className="hidden lg:block lg:w-1/2 ml-12">
            <div className="bg-gray-100 rounded-3xl p-8 aspect-video flex items-center justify-center border-4 border-white shadow-2xl">
              <ChessKnight className="w-32 h-32 text-blue-200" />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
