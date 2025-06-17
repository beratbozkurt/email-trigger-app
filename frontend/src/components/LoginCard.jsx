import React, { useState } from 'react'
import { Mail, Chrome, Calendar } from 'lucide-react'
import { emailAPI } from '../services/api'
import toast from 'react-hot-toast'

const LoginCard = ({ onLogin }) => {
  const [loading, setLoading] = useState(null)

  const handleProviderLogin = async (provider) => {
    setLoading(provider)
    try {
      const response = await emailAPI.getAuthUrl(provider)
      const authUrl = response.data.authorization_url
      
      // Redirect to OAuth URL instead of popup
      toast.loading('Redirecting to OAuth provider...')
      window.location.href = authUrl
      
    } catch (error) {
      setLoading(null)
      toast.error(`Failed to start ${provider} login`)
    }
  }

  const handleCallback = async (provider, code) => {
    try {
      const response = await emailAPI.handleCallback(provider, code)
      toast.success(`Successfully connected to ${provider}!`)
      onLogin(response.data)
    } catch (error) {
      toast.error(`Failed to complete ${provider} login`)
    }
  }

  return (
    <div className="card max-w-md mx-auto">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
          <Mail className="w-8 h-8 text-primary-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Email Trigger App
        </h1>
        <p className="text-gray-600">
          Connect your email accounts to get started
        </p>
      </div>

      <div className="space-y-4">
        <button
          onClick={() => handleProviderLogin('gmail')}
          disabled={loading === 'gmail'}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <Chrome className="w-5 h-5 mr-3 text-red-500" />
          {loading === 'gmail' ? 'Connecting...' : 'Connect Gmail'}
        </button>

        <button
          onClick={() => handleProviderLogin('outlook')}
          disabled={loading === 'outlook'}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <Calendar className="w-5 h-5 mr-3 text-blue-500" />
          {loading === 'outlook' ? 'Connecting...' : 'Connect Outlook'}
        </button>
      </div>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or for testing</span>
          </div>
        </div>
        
        <button
          onClick={() => window.location.href = 'http://localhost:8000/auth/test-oauth'}
          className="mt-4 w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm bg-gray-50 text-gray-700 hover:bg-gray-100 transition-colors text-sm"
        >
          🧪 Test Login (Demo Mode)
        </button>
      </div>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          Your email data is secure and never stored on our servers
        </p>
      </div>
    </div>
  )
}

export default LoginCard