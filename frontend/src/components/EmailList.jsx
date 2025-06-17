import React, { useState, useEffect } from 'react'
import { Mail, Clock, User, Paperclip, Download } from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'

const EmailList = ({ emails, loading }) => {
  const [lastRefresh, setLastRefresh] = useState(new Date())

  useEffect(() => {
    if (!loading) {
      setLastRefresh(new Date())
    }
  }, [loading])

  const formatDate = (date) => {
    return format(new Date(date), 'MMM d, yyyy h:mm a')
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleAttachmentClick = async (attachment) => {
    try {
      const response = await fetch(`/api/attachments/${attachment.id || attachment.external_id}`)
      if (!response.ok) throw new Error('Failed to download attachment')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = attachment.filename || response.headers.get('Content-Disposition')?.split('filename="')[1]?.replace('"', '') || 'attachment'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading attachment:', error)
      alert('Failed to download attachment')
    }
  }

  const truncateText = (text, length = 100) => {
    if (!text) return ''
    // If text contains HTML, try to extract plain text
    if (text.includes('<') && text.includes('>')) {
      try {
        // Create a temporary element to parse HTML
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = text
        text = tempDiv.textContent || tempDiv.innerText || ''
      } catch (e) {
        // If HTML parsing fails, just remove basic tags
        text = text.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
      }
    }
    return text.length > length ? text.substring(0, length) + '...' : text
  }

  const getProviderIcon = (providerType) => {
    switch (providerType) {
      case 'gmail':
        return '📧'
      case 'outlook':
        return '📮'
      default:
        return '✉️'
    }
  }

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="w-6 h-6 animate-spin rounded-full border-b-2 border-primary-600 mr-2"></div>
          <span className="text-gray-600">Loading emails...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Recent Emails</h2>
        <p className="text-sm text-gray-500 mt-1">
          Auto-refreshing every 30 seconds • Last updated {formatDate(lastRefresh)}
        </p>
      </div>

      {/* Email List */}
      <div className="card p-0">
        {emails.length === 0 ? (
          <div className="text-center py-12">
            <Mail className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No emails found</h3>
            <p className="text-gray-500">
              Connect your email account and wait for new emails to appear here.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {emails.map((emailData, index) => {
              const email = emailData.message
              const provider = emailData.provider_type
              
              return (
                <div key={`${provider}-${email.id || index}`} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {/* Header */}
                      <div className="flex items-center mb-2">
                        <span className="text-lg mr-2">{getProviderIcon(provider)}</span>
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                          {provider}
                        </span>
                        {!email.is_read && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            New
                          </span>
                        )}
                      </div>
                      
                      {/* Subject */}
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {email.subject || 'No Subject'}
                      </h3>
                      
                      {/* Sender */}
                      <div className="flex items-center text-sm text-gray-600 mb-2">
                        <User className="w-4 h-4 mr-1" />
                        <span>{email.sender}</span>
                      </div>
                      
                      {/* Body Preview */}
                      <p className="text-gray-700 text-sm leading-relaxed mb-3">
                        {truncateText(email.body)}
                      </p>
                      
                      {/* Footer */}
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
                            {formatDate(email.received_at)}
                          </div>
                          
                          {email.attachments && email.attachments.length > 0 && (
                            <div className="flex items-center space-x-2">
                              <Paperclip className="w-3 h-3" />
                              <span>{email.attachments.length} attachment{email.attachments.length > 1 ? 's' : ''}</span>
                              <div className="flex flex-wrap gap-1">
                                {email.attachments.map((attachment, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => handleAttachmentClick(attachment)}
                                    className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                                    title={`Download ${attachment.filename} (${formatFileSize(attachment.size)})${
                                      attachment.document_type ? `\nType: ${attachment.document_type} (${Math.round(attachment.classification_confidence * 100)}% confidence)` : ''
                                    }`}
                                  >
                                    <Download className="w-3 h-3 mr-1" />
                                    {attachment.filename}
                                    {attachment.document_type && (
                                      <span className="ml-1 px-1 py-0.5 rounded bg-blue-100 text-blue-800">
                                        {attachment.document_type}
                                      </span>
                                    )}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {email.recipients && (
                            <div>
                              To: {email.recipients.slice(0, 2).join(', ')}
                              {email.recipients.length > 2 && ` +${email.recipients.length - 2} more`}
                            </div>
                          )}
                        </div>
                        
                        {email.labels && email.labels.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {email.labels.slice(0, 3).map((label, idx) => (
                              <span key={idx} className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                                {label.replace('CATEGORY_', '').toLowerCase()}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
      
      {emails.length > 0 && (
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Showing {emails.length} recent emails
          </p>
        </div>
      )}
    </div>
  )
}

export default EmailList