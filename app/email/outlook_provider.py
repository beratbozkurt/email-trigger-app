from typing import List, Dict, Optional
from datetime import datetime
import requests
from .base import EmailProvider, EmailMessage


class OutlookProvider(EmailProvider):
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_messages(self, limit: int = 10, page_token: str = None) -> Dict:
        try:
            url = f"{self.base_url}/me/messages"
            params = {"$top": limit, "$orderby": "receivedDateTime desc"}
            
            if page_token:
                params["$skip"] = page_token
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            messages = [self._parse_message(msg) for msg in data.get('value', [])]
            
            return {
                'messages': messages,
                'next_page_token': data.get('@odata.nextLink'),
                'total_count': len(messages)
            }
        except Exception as e:
            print(f"Error fetching Outlook messages: {e}")
            return {'messages': [], 'next_page_token': None, 'total_count': 0}
    
    def get_message_by_id(self, message_id: str) -> Optional[EmailMessage]:
        try:
            url = f"{self.base_url}/me/messages/{message_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            message_data = response.json()
            return self._parse_message(message_data)
        except Exception as e:
            print(f"Error fetching Outlook message {message_id}: {e}")
            return None
    
    def _parse_message(self, message: Dict) -> EmailMessage:
        sender = message.get('sender', {}).get('emailAddress', {})
        sender_email = sender.get('address', '')
        sender_name = sender.get('name', '')
        sender_full = f"{sender_name} <{sender_email}>" if sender_name else sender_email
        
        recipients = []
        for recipient in message.get('toRecipients', []):
            email_addr = recipient.get('emailAddress', {})
            recipients.append(email_addr.get('address', ''))
        
        received_at = None
        if message.get('receivedDateTime'):
            received_at = datetime.fromisoformat(
                message['receivedDateTime'].replace('Z', '+00:00')
            )
        
        body = message.get('body', {}).get('content', '')
        html_body = body if message.get('body', {}).get('contentType') == 'html' else None
        
        # Get attachments
        attachments = []
        if message.get('hasAttachments', False):
            print(f"📎 Message has attachments, fetching details...")
            attachments_url = f"{self.base_url}/me/messages/{message['id']}/attachments"
            try:
                attachments_response = requests.get(attachments_url, headers=self.headers)
                attachments_response.raise_for_status()
                attachments_data = attachments_response.json()
                
                print(f"📎 Found {len(attachments_data.get('value', []))} attachments")
                for attachment in attachments_data.get('value', []):
                    print(f"📎 Processing attachment: {attachment.get('name')}")
                    attachments.append({
                        'id': attachment['id'],
                        'filename': attachment['name'],
                        'content_type': attachment['contentType'],
                        'size': attachment['size'],
                        'is_inline': attachment.get('contentId') is not None
                    })
                    print(f"📎 Added attachment to list: {attachment.get('name')}")
            except Exception as e:
                print(f"❌ Error fetching attachments for message {message['id']}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"ℹ️ Message has no attachments")
        
        # Check for inline images in HTML body
        if html_body:
            import re
            cid_pattern = r'cid:([^"\')\s]+)'
            cid_matches = re.findall(cid_pattern, html_body)
            if cid_matches:
                print(f"📎 Found {len(cid_matches)} inline images in HTML body")
                # Fetch attachments again to get inline images
                try:
                    attachments_url = f"{self.base_url}/me/messages/{message['id']}/attachments"
                    attachments_response = requests.get(attachments_url, headers=self.headers)
                    attachments_response.raise_for_status()
                    attachments_data = attachments_response.json()
                    
                    for attachment in attachments_data.get('value', []):
                        if attachment.get('contentId') in cid_matches:
                            print(f"📎 Processing inline image: {attachment.get('name')}")
                            attachments.append({
                                'id': attachment['id'],
                                'filename': attachment['name'],
                                'content_type': attachment['contentType'],
                                'size': attachment['size'],
                                'is_inline': True
                            })
                            print(f"📎 Added inline image to list: {attachment.get('name')}")
                except Exception as e:
                    print(f"❌ Error fetching inline images: {e}")
                    import traceback
                    traceback.print_exc()
        
        return EmailMessage(
            id=message['id'],
            subject=message.get('subject', ''),
            sender=sender_full,
            recipients=recipients,
            body=body,
            html_body=html_body,
            received_at=received_at,
            thread_id=message.get('conversationId'),
            is_read=message.get('isRead', False),
            attachments=attachments
        )
    
    def get_attachment_data(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """Get attachment data for a specific message and attachment"""
        try:
            url = f"{self.base_url}/me/messages/{message_id}/attachments/{attachment_id}/$value"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error fetching attachment data: {e}")
            return None
    
    def mark_as_read(self, message_id: str) -> bool:
        try:
            url = f"{self.base_url}/me/messages/{message_id}"
            data = {"isRead": True}
            
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error marking Outlook message as read: {e}")
            return False
    
    def get_new_messages_since(self, since: datetime) -> List[EmailMessage]:
        try:
            since_str = since.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            url = f"{self.base_url}/me/messages"
            params = {
                "$filter": f"receivedDateTime ge {since_str}",
                "$orderby": "receivedDateTime desc",
                "$top": 100
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            messages = [self._parse_message(msg) for msg in data.get('value', [])]
            return messages
        except Exception as e:
            print(f"Error fetching new Outlook messages: {e}")
            return []
    
    def setup_webhook(self, webhook_url: str) -> bool:
        try:
            url = f"{self.base_url}/subscriptions"
            data = {
                "changeType": "created",
                "notificationUrl": webhook_url,
                "resource": "me/messages",
                "expirationDateTime": (datetime.now().isoformat() + "Z"),
                "clientState": "subscription-identifier"
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error setting up Outlook webhook: {e}")
            return False