import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import toast from 'react-hot-toast'
import LoginPage from './pages/LoginPage'
import DashboardHome from './pages/DashboardHome'
import EmailsPage from './pages/EmailsPage'
import TriggersPage from './pages/TriggersPage'
import SettingsPage from './pages/SettingsPage'
import DashboardLayout from './components/DashboardLayout'

function AppContent() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isProcessingOAuth, setIsProcessingOAuth] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const initializeAuth = async () => {
      console.log('🔍 App useEffect running')
      
      // Check for OAuth callback first
      const urlParams = new URLSearchParams(window.location.search)
      const oauthSuccess = urlParams.get('oauth_success')
      const oauthError = urlParams.get('oauth_error')
      
      console.log('🔗 URL params - success:', oauthSuccess, 'error:', oauthError)
      
      if (oauthError) {
        toast.error('OAuth authentication failed. Please try again.')
        window.history.replaceState({}, document.title, window.location.pathname)
        navigate('/login')
        setLoading(false)
        return
      } 
      
      if (oauthSuccess) {
        console.log('🚀 OAuth success detected - processing...')
        setIsProcessingOAuth(true)
        
        // Check for user data in URL parameters first (fallback)
        const urlUserData = urlParams.get('user_data')
        
        // Check if user data was stored by the callback page
        const callbackUserData = localStorage.getItem('emailTriggerUser')
        console.log('📞 OAuth success - callback data:', callbackUserData)
        console.log('🔗 OAuth success - URL data:', urlUserData)
        
        let userData = null
        
        // Try to get user data from localStorage first, then URL params
        if (callbackUserData) {
          try {
            userData = JSON.parse(callbackUserData)
            console.log('✅ Got user data from localStorage:', userData)
          } catch (e) {
            console.error('❌ Failed to parse localStorage OAuth data:', e)
          }
        }
        
        // Fallback to URL parameters if localStorage failed
        if (!userData && urlUserData) {
          try {
            userData = JSON.parse(decodeURIComponent(urlUserData))
            console.log('✅ Got user data from URL params:', userData)
          } catch (e) {
            console.error('❌ Failed to parse URL OAuth data:', e)
          }
        }
        
        if (userData) {
          // Clean up URL first
          window.history.replaceState({}, document.title, window.location.pathname)
          
          // Set user state first
          setUser(userData)
          
          // Store in localStorage if it wasn't already there
          if (!callbackUserData) {
            localStorage.setItem('emailTriggerUser', JSON.stringify(userData))
          }
          
          toast.success(`Welcome back, ${userData.email}! 🎉`)
          
          // Navigate to dashboard using React Router after state is set
          console.log('🏠 Navigating to dashboard...')
          setTimeout(() => {
            setLoading(false)
            setIsProcessingOAuth(false)
            navigate('/dashboard', { replace: true })
          }, 200)
          return
        } else {
          console.log('❌ No user data found in localStorage or URL params')
          toast.error('Authentication data not found')
          setIsProcessingOAuth(false)
          navigate('/login')
          setLoading(false)
          return
        }
      }
      
      // Handle existing user from localStorage
      const savedUser = localStorage.getItem('emailTriggerUser')
      console.log('📱 Saved user from localStorage:', savedUser)
      
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          console.log('✅ Setting user from localStorage:', userData)
          setUser(userData)
        } catch (error) {
          console.error('Error parsing saved user:', error)
          localStorage.removeItem('emailTriggerUser')
        }
      }
      
      setLoading(false)
    }

    initializeAuth()
  }, [navigate])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('emailTriggerUser', JSON.stringify(userData))
    toast.success(`Welcome to your dashboard! 🎉`)
    // Navigate to dashboard after login
    navigate('/dashboard')
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('emailTriggerUser')
    toast.info('Logged out successfully')
    // Navigate to login page after logout
    navigate('/login')
  }

  if (loading || isProcessingOAuth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {isProcessingOAuth ? 'Processing authentication...' : 'Loading...'}
          </p>
        </div>
      </div>
    )
  }

  console.log('🎯 Rendering routes - user:', user, 'path:', window.location.pathname)
  
  return (
    <Routes>
      <Route path="/login" element={
        user ? (
          <Navigate to="/dashboard" replace />
        ) : (
          <LoginPage onLogin={handleLogin} />
        )
      } />
      
      <Route path="/dashboard" element={
        user ? (
          <DashboardLayout user={user} onLogout={handleLogout} />
        ) : (
          <Navigate to="/login" replace />
        )
      }>
        <Route index element={<DashboardHome />} />
        <Route path="emails" element={<EmailsPage />} />
        <Route path="triggers" element={<TriggersPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      
      <Route path="/" element={
        <Navigate to={user ? "/dashboard" : "/login"} replace />
      } />
      
      <Route path="*" element={
        <Navigate to={user ? "/dashboard" : "/login"} replace />
      } />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        <AppContent />
      </div>
    </Router>
  )
}

export default App