import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    toast.error(message)
    return Promise.reject(error)
  }
)

export const emailAPI = {
  // Auth endpoints
  getAuthUrl: (provider) => 
    api.get(`/auth/${provider}/login`),
  
  handleCallback: (provider, code) =>
    api.get(`/auth/${provider}/callback`, { params: { code } }),
  
  // Provider endpoints
  getSupportedProviders: () =>
    api.get('/providers'),
  
  // User endpoints
  getUserEmails: (userId, limit = 10) =>
    api.get(`/users/${userId}/emails`, { params: { limit } }),
  
  // Trigger management endpoints
  getTriggers: (userId) =>
    api.get(`/users/${userId}/triggers`),
  
  createTrigger: (userId, triggerData) =>
    api.post(`/users/${userId}/triggers`, triggerData),
  
  updateTrigger: (userId, triggerId, triggerData) =>
    api.put(`/users/${userId}/triggers/${triggerId}`, triggerData),
  
  deleteTrigger: (userId, triggerId) =>
    api.delete(`/users/${userId}/triggers/${triggerId}`),
  
  // Test endpoints
  testEmailNotification: (userId) =>
    api.post(`/test-email-notification/${userId}`),
  
  startEmailMonitoring: (userId) =>
    api.get(`/start-email-monitoring/${userId}`),
  
  debugOAuthCredentials: () =>
    api.get('/debug-oauth-credentials'),
  
  testOAuth: () =>
    api.get('/auth/test-oauth'),
  
  // Health check
  healthCheck: () =>
    api.get('/health'),
}

export default api