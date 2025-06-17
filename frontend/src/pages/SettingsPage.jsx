import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { emailAPI } from '../services/api'
import toast from 'react-hot-toast'

const SettingsPage = () => {
  const { user } = useOutletContext()
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
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Settings</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Connected Account
          </label>
          <div className="bg-gray-50 p-3 rounded-md">
            <p className="font-medium">{user.email}</p>
            <p className="text-sm text-gray-600">Provider ID: {user.provider_id}</p>
            <p className="text-sm text-gray-600">User ID: {effectiveUserId}</p>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monitoring Status
          </label>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Active - Monitoring emails every 30 seconds</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Actions
          </label>
          <div className="space-y-2">
            <button
              onClick={testEmailPermissions}
              className="w-full btn-secondary text-sm"
            >
              🔐 Test Email Permissions
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage