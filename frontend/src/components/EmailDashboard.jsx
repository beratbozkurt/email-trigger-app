import React, { useState, useEffect } from 'react'
import { Mail, Inbox, Settings, User, LogOut, Zap } from 'lucide-react'
import { emailAPI } from '../services/api'
import EmailList from './EmailList'
import TriggerManager from './TriggerManager'
import toast from 'react-hot-toast'

const EmailDashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('emails')
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(false)
  const [effectiveUserId, setEffectiveUserId] = useState(user.user_id)

  useEffect(() => {
    if (activeTab === 'emails') {
      fetchEmails()
    }
  }, [activeTab, user.user_id])

  const fetchEmails = async () => {
    setLoading(true)
    try {
      const response = await emailAPI.getUserEmails(user.user_id)
      setEmails(response.data.emails || [])
    } catch (error) {
      toast.error('Failed to fetch emails')
      console.error('Email fetch error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTestTrigger = async () => {
    try {
      await emailAPI.testTrigger(effectiveUserId)
      toast.success('Trigger test completed! Check console for details.')
    } catch (error) {
      toast.error('Failed to test triggers')
    }
  }

  const testEmailPermissions = async () => {
    try {
      toast.loading('Testing email permissions...')
      const response = await emailAPI.testEmailPermissions(effectiveUserId)
      const data = response.data
      
      toast.dismiss()
      
      if (data.error) {
        toast.error(`Permission test failed: ${data.error}`)
      } else {
        // Show detailed results
        const userTest = data.user_test
        const messageTest = data.messages_test
        
        if (userTest.success && messageTest.success) {
          toast.success('✅ Email permissions working! You can read emails.')
        } else if (userTest.success && !messageTest.success) {
          toast.error('❌ Can access profile but cannot read emails. Check permissions.')
        } else {
          toast.error('❌ Cannot access Microsoft Graph API. Token may be invalid.')
        }
        
        // Log detailed results
        console.log('Permission Test Results:', data)
      }
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to test permissions')
      console.error('Permission test error:', error)
    }
  }

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
                  onClick={() => setActiveTab('emails')}
                  className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'emails'
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Inbox className="w-5 h-5 mr-3" />
                  Emails
                </button>
                
                <button
                  onClick={() => setActiveTab('triggers')}
                  className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'triggers'
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Zap className="w-5 h-5 mr-3" />
                  Triggers
                </button>
                
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'settings'
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Settings className="w-5 h-5 mr-3" />
                  Settings
                </button>
              </div>

              <div className="mt-8 pt-6 border-t space-y-3">
                <button
                  onClick={handleTestTrigger}
                  className="w-full btn-primary text-sm"
                >
                  Test Triggers
                </button>
                
                <button
                  onClick={() => testEmailPermissions()}
                  className="w-full btn-secondary text-sm"
                >
                  🔐 Test Email Permissions
                </button>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1">
            {activeTab === 'emails' && (
              <EmailList 
                emails={emails} 
                loading={loading}
                onRefresh={fetchEmails}
              />
            )}
            
            {activeTab === 'triggers' && (
              <TriggerManager userId={effectiveUserId} />
            )}
            
            {activeTab === 'settings' && (
              <div className="card">
                <h2 className="text-lg font-medium text-gray-900">Settings</h2>
                <p className="mt-1 text-sm text-gray-500">
                  Configure your email trigger settings here.
                </p>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

export default EmailDashboard