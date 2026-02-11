import { ReactNode } from 'react'
import { Beef } from 'lucide-react'

interface AuthLayoutProps {
  children: ReactNode
  title: string
  subtitle: string
}

export default function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
      <div className="hidden lg:flex flex-col justify-between p-12 bg-blue-600 text-white">
        <div>
          <div className="flex items-center space-x-2 text-2xl font-bold">
            <Beef className="w-8 h-8" />
            <span>Riding School Tracker</span>
          </div>
        </div>
        <div>
          <blockquote className="text-3xl font-medium leading-tight">
            "This platform has completely transformed how we manage our riders' progress. It's
            simple, professional, and effective."
          </blockquote>
          <div className="mt-6 flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full bg-blue-400" />
            <div>
              <div className="font-bold">Sarah Jenkins</div>
              <div className="text-blue-200">Owner, Willow Creek Equestrian</div>
            </div>
          </div>
        </div>
        <div className="text-sm text-blue-200">
          © 2026 Riding School Progress Tracker. All rights reserved.
        </div>
      </div>
      <div className="flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-extrabold text-gray-900">{title}</h2>
            <p className="mt-2 text-sm text-gray-600">{subtitle}</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  )
}
