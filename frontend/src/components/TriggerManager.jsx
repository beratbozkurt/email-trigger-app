import React, { useState, useEffect } from 'react'
import { Plus, Trash2, Edit, Zap, Save, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { emailAPI } from '../services/api'

const TriggerManager = ({ userId }) => {
  const [triggers, setTriggers] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingTrigger, setEditingTrigger] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)

  useEffect(() => {
    fetchTriggers()
  }, [userId])

  const fetchTriggers = async () => {
    try {
      setLoading(true)
      const response = await emailAPI.getTriggers(userId)
      setTriggers(response.data.triggers || [])
    } catch (error) {
      toast.error('Failed to fetch triggers')
      console.error('Fetch triggers error:', error)
    } finally {
      setLoading(false)
    }
  }

  const triggerTypes = [
    { value: 'sender_contains', label: 'Sender contains' },
    { value: 'subject_contains', label: 'Subject contains' },
    { value: 'body_contains', label: 'Body contains' },
    { value: 'sender_exact', label: 'Exact sender' },
    { value: 'subject_regex', label: 'Subject regex' },
    { value: 'attachment_exists', label: 'Has attachments' },
    { value: 'time_range', label: 'Time range' }
  ]

  const actionTypes = [
    { value: 'log_message', label: 'Log message' },
    { value: 'mark_as_read', label: 'Mark as read' },
    { value: 'forward_email', label: 'Forward email' },
    { value: 'send_notification', label: 'Send notification' },
    { value: 'webhook_call', label: 'Call webhook' },
    { value: 'custom_script', label: 'Run script' }
  ]

  const handleCreateTrigger = async (triggerData) => {
    try {
      const response = await emailAPI.createTrigger(userId, triggerData)
      await fetchTriggers() // Refresh the list
      setShowCreateForm(false)
      toast.success('Trigger created successfully!')
    } catch (error) {
      toast.error('Failed to create trigger')
      console.error('Create trigger error:', error)
    }
  }

  const handleUpdateTrigger = async (updatedTrigger) => {
    try {
      await emailAPI.updateTrigger(userId, updatedTrigger.id, updatedTrigger)
      await fetchTriggers() // Refresh the list
      setEditingTrigger(null)
      toast.success('Trigger updated successfully!')
    } catch (error) {
      toast.error('Failed to update trigger')
      console.error('Update trigger error:', error)
    }
  }

  const handleDeleteTrigger = async (triggerId) => {
    try {
      await emailAPI.deleteTrigger(userId, triggerId)
      await fetchTriggers() // Refresh the list
      toast.success('Trigger deleted successfully!')
    } catch (error) {
      toast.error('Failed to delete trigger')
      console.error('Delete trigger error:', error)
    }
  }

  const toggleTrigger = async (triggerId) => {
    const trigger = triggers.find(t => t.id === triggerId)
    if (trigger) {
      await handleUpdateTrigger({
        ...trigger,
        isActive: !trigger.isActive
      })
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Email Triggers</h2>
        </div>
        <div className="card py-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading triggers...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Email Triggers</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Trigger
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <TriggerForm
          onSave={handleCreateTrigger}
          onCancel={() => setShowCreateForm(false)}
          triggerTypes={triggerTypes}
          actionTypes={actionTypes}
        />
      )}

      {/* Triggers List */}
      <div className="space-y-4">
        {triggers.map((trigger) => (
          <div key={trigger.id} className="card">
            {editingTrigger === trigger.id ? (
              <TriggerForm
                trigger={trigger}
                onSave={handleUpdateTrigger}
                onCancel={() => setEditingTrigger(null)}
                triggerTypes={triggerTypes}
                actionTypes={actionTypes}
              />
            ) : (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <Zap className={`w-5 h-5 mr-2 ${trigger.isActive ? 'text-green-500' : 'text-gray-400'}`} />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {trigger.name}
                    </h3>
                    <span className={`ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      trigger.isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {trigger.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{trigger.description}</p>
                  
                  <div className="flex flex-wrap gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Trigger:</span>
                      <span className="ml-1 text-gray-600">
                        {triggerTypes.find(t => t.value === trigger.triggerType)?.label}
                        {trigger.condition && ` "${trigger.condition}"`}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Action:</span>
                      <span className="ml-1 text-gray-600">
                        {actionTypes.find(a => a.value === trigger.action)?.label}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleTrigger(trigger.id)}
                    className={`px-3 py-1 rounded text-sm font-medium ${
                      trigger.isActive
                        ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                        : 'bg-green-100 text-green-800 hover:bg-green-200'
                    }`}
                  >
                    {trigger.isActive ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    onClick={() => setEditingTrigger(trigger.id)}
                    className="p-2 text-gray-400 hover:text-gray-600"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteTrigger(trigger.id)}
                    className="p-2 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {triggers.length === 0 && (
        <div className="card text-center py-12">
          <Zap className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No triggers configured</h3>
          <p className="text-gray-500 mb-4">
            Create your first trigger to automatically process incoming emails.
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            Create First Trigger
          </button>
        </div>
      )}
    </div>
  )
}

const TriggerForm = ({ trigger, onSave, onCancel, triggerTypes, actionTypes }) => {
  const [formData, setFormData] = useState({
    name: trigger?.name || '',
    description: trigger?.description || '',
    triggerType: trigger?.triggerType || 'sender_contains',
    condition: trigger?.condition || '',
    action: trigger?.action || 'log_message'
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.name.trim()) {
      toast.error('Please enter a trigger name')
      return
    }
    onSave({ ...trigger, ...formData })
  }

  const needsCondition = !['attachment_exists'].includes(formData.triggerType)

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Trigger Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="e.g., Boss Emails"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Trigger Type
          </label>
          <select
            value={formData.triggerType}
            onChange={(e) => setFormData({...formData, triggerType: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {triggerTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>
      </div>

      {needsCondition && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Condition
          </label>
          <input
            type="text"
            value={formData.condition}
            onChange={(e) => setFormData({...formData, condition: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder={
              formData.triggerType === 'time_range' ? 'e.g., 09:00-17:00' :
              formData.triggerType.includes('regex') ? 'e.g., urgent|emergency' :
              'e.g., boss@company.com'
            }
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Action
        </label>
        <select
          value={formData.action}
          onChange={(e) => setFormData({...formData, action: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {actionTypes.map(action => (
            <option key={action.value} value={action.value}>{action.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Describe what this trigger does..."
        />
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary flex items-center"
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary flex items-center"
        >
          <Save className="w-4 h-4 mr-2" />
          {trigger ? 'Update' : 'Create'} Trigger
        </button>
      </div>
    </form>
  )
}

export default TriggerManager