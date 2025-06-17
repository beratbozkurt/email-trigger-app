import { useState, useEffect } from 'react'
import { useOutletContext, useNavigate } from 'react-router-dom'
import { Mail, Zap, Settings, TrendingUp, Activity, Clock, CheckCircle } from 'lucide-react'
import { emailAPI } from '../services/api'
import toast from 'react-hot-toast'

const DashboardHome = () => {
  const { user, effectiveUserId } = useOutletContext()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalEmails: 0,
    activeTriggers: 0,
    recentEmails: [],
    connectionStatus: 'checking'
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [effectiveUserId])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load emails count
      const emailsResponse = await emailAPI.getUserEmails(effectiveUserId, 5)
      const emails = emailsResponse.data.emails || []
      
      // Load triggers count
      const triggersResponse = await emailAPI.getTriggers(effectiveUserId)
      const triggers = triggersResponse.data.triggers || []
      const activeTriggers = triggers.filter(t => t.isActive).length
      
      // Test connection by checking if we can get emails
      let connectionStatus = 'connected'
      if (!emailsResponse.data || emailsResponse.data.error) {
        connectionStatus = 'error'
      }

      setStats({
        totalEmails: emails.length,
        activeTriggers,
        recentEmails: emails.slice(0, 3),
        connectionStatus
      })
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    {
      title: 'View All Emails',
      description: 'Browse your recent emails',
      icon: Mail,
      action: () => navigate('/dashboard/emails'),
      color: 'bg-blue-500'
    },
    {
      title: 'Manage Triggers',
      description: 'Create and manage email triggers',
      icon: Zap,
      action: () => navigate('/dashboard/triggers'),
      color: 'bg-yellow-500'
    },
    {
      title: 'Account Settings',
      description: 'Manage your account and preferences',
      icon: Settings,
      action: () => navigate('/dashboard/settings'),
      color: 'bg-gray-500'
    }
  ]

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card py-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user.email.split('@')[0]}! 👋
            </h1>
            <p className="text-gray-600 mt-1">
              Your email monitoring is active. Here's your account overview:
            </p>
          </div>
          <div className="flex items-center">
            {stats.connectionStatus === 'connected' ? (
              <div className="flex items-center text-green-600">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span className="text-sm font-medium">Connected</span>
              </div>
            ) : (
              <div className="flex items-center text-red-600">
                <Activity className="w-5 h-5 mr-2" />
                <span className="text-sm font-medium">Connection Issue</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Mail className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recent Emails</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalEmails}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Zap className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Triggers</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeTriggers}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Monitoring</p>
              <p className="text-2xl font-bold text-gray-900">Active</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <button
                key={index}
                onClick={action.action}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all text-left"
              >
                <div className="flex items-center mb-3">
                  <div className={`p-2 ${action.color} rounded-lg`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="ml-3 font-medium text-gray-900">{action.title}</h3>
                </div>
                <p className="text-sm text-gray-600">{action.description}</p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Recent Emails */}
      {stats.recentEmails.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Emails</h2>
            <button
              onClick={() => navigate('/dashboard/emails')}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all →
            </button>
          </div>
          <div className="space-y-3">
            {stats.recentEmails.map((emailData, index) => {
              const email = emailData.message
              return (
                <div key={index} className="flex items-start p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <Mail className="w-4 h-4 text-primary-600" />
                    </div>
                  </div>
                  <div className="ml-3 flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {email.subject || 'No Subject'}
                    </p>
                    <p className="text-sm text-gray-600 truncate">
                      From: {email.sender}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <Clock className="w-4 h-4 text-gray-400" />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Getting Started */}
      {stats.totalEmails === 0 && (
        <div className="card text-center py-12">
          <Mail className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Your email monitoring is active!
          </h3>
          <p className="text-gray-600 mb-6">
            We're monitoring your email account for new messages. When emails arrive, they'll appear here.
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/dashboard/triggers')}
              className="btn-primary"
            >
              Create Your First Trigger
            </button>
            <button
              onClick={() => navigate('/dashboard/emails')}
              className="btn-secondary"
            >
              View Email Settings
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardHome