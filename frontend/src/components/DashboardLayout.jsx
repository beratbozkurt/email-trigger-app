import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Mail, Inbox, Settings, User, LogOut, Zap, Home } from 'lucide-react'
import { emailAPI } from '../services/api'
import toast from 'react-hot-toast'
import Breadcrumb from './Breadcrumb'

const DashboardLayout = ({ user, onLogout }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [effectiveUserId, setEffectiveUserId] = useState(user.user_id)

  useEffect(() => {
    // Check if user data was updated in localStorage
    const savedUser = localStorage.getItem('emailTriggerUser')
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        if (userData.user_id !== user.user_id) {
          setEffectiveUserId(userData.user_id)
        }
      } catch (error) {
        console.error('Error parsing saved user data:', error)
      }
    }
  }, [user.user_id])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Mail className="w-8 h-8 text-primary-600 mr-3" />
              <h1 className="text-xl font-semibold text-gray-900">
                Email Trigger App
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-gray-600">
                <User className="w-4 h-4 mr-2" />
                {user.email}
              </div>
              <button
                onClick={onLogout}
                className="btn-secondary flex items-center"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <nav className="w-64 flex-shrink-0">
            <div className="card">
              <div className="space-y-1">
                <button
                  onClick={() => navigate('/dashboard/emails')}
                  className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    location.pathname.includes('/emails')
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Inbox className="w-5 h-5 mr-3" />
                  Emails
                </button>
                
                <button
                  onClick={() => navigate('/dashboard/triggers')}
                  className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    location.pathname.includes('/triggers')
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Zap className="w-5 h-5 mr-3" />
                  Triggers
                </button>
                
                <button
                  onClick={() => navigate('/dashboard/settings')}
                  className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    location.pathname.includes('/settings')
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Settings className="w-5 h-5 mr-3" />
                  Settings
                </button>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1">
            <Breadcrumb />
            <Outlet context={{ user, effectiveUserId }} />
          </main>
        </div>
      </div>
    </div>
  )
}

export default DashboardLayout