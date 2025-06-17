import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { emailAPI } from '../services/api'
import EmailList from '../components/EmailList'
import toast from 'react-hot-toast'

const EmailsPage = () => {
  const { user } = useOutletContext()
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Initial fetch
    fetchEmails()

    // Set up automatic refresh every 30 seconds
    const refreshInterval = setInterval(fetchEmails, 30000)

    // Cleanup interval on component unmount
    return () => clearInterval(refreshInterval)
  }, [user.user_id])

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

  return (
    <EmailList 
      emails={emails} 
      loading={loading}
    />
  )
}

export default EmailsPage