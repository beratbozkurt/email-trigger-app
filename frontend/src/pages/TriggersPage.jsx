import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import TriggerManager from '../components/TriggerManager'

const TriggersPage = () => {
  const { user } = useOutletContext()
  // Get effective user ID (might be 4 instead of 1)
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
    <TriggerManager userId={effectiveUserId} />
  )
}

export default TriggersPage