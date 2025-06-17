from typing import List, Dict, Optional
from datetime import datetime
import base64
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import re
from .base import EmailProvider, EmailMessage


class GmailProvider(EmailProvider):
    def __init__(self, access_token: str, refresh_token: str = None):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token
        )
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def get_messages(self, limit: int = 10, page_token: str = None) -> Dict:
        try:
            params = {'userId': 'me', 'maxResults': limit}
            if page_token:
                params['pageToken'] = page_token
            
            result = self.service.users().messages().list(**params).execute()
            messages = result.get('messages', [])
            
            detailed_messages = []
            
            if messages:
                batch = BatchHttpRequest()
                results = {}

                def callback(request_id, response, exception):
                    if exception is not None:
                        print(f"Error fetching message {request_id}: {exception}")
                        results[request_id] = None
                    else:
                        results[request_id] = self._parse_message(response)
                
                for msg in messages:
                    batch.add(self.service.users().messages().get(userId='me', id=msg['id'], format='full'), callback=callback, request_id=msg['id'])
                
                batch.execute()
                
                for msg_id in [msg['id'] for msg in messages]:
                    if results.get(msg_id):
                        detailed_messages.append(results[msg_id])
            
            return {
                'messages': detailed_messages,
                'next_page_token': result.get('nextPageToken'),
                'total_count': result.get('resultSizeEstimate', 0)
            }
        except Exception as e:
            print(f"Error fetching Gmail messages: {e}")
            return {'messages': [], 'next_page_token': None, 'total_count': 0}
    
    def get_message_by_id(self, message_id: str) -> Optional[EmailMessage]:
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            return self._parse_message(message)
        except Exception as e:
            print(f"Error fetching Gmail message {message_id}: {e}")
            return None
    
    def _parse_message(self, message: Dict) -> EmailMessage:
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        
        body = ""
        html_body = None
        attachments = []
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part.get('filename') and part.get('body', {}).get('attachmentId'):
                    attachments.append({
                        'id': part['body']['attachmentId'],
                        'filename': part['filename'],
                        'content_type': part['mimeType'],
                        'size': part['body'].get('size', 0)
                    })
        elif 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        received_timestamp = int(message['internalDate'])
        received_at = datetime.fromtimestamp(received_timestamp / 1000)
        
        email_subject = headers.get('Subject', '')
        email_thread_id = message.get('threadId')

        # If the subject starts with the thread_id, remove it
        if email_thread_id and email_subject.startswith(email_thread_id):
            email_subject = email_subject[len(email_thread_id):].strip()

        return EmailMessage(
            id=message['id'],
            subject=email_subject,
            sender=headers.get('From', ''),
            recipients=headers.get('To', '').split(',') if headers.get('To') else [],
            body=body,
            html_body=html_body,
            received_at=received_at,
            thread_id=message.get('threadId'),
            labels=message.get('labelIds', []),
            is_read='UNREAD' not in message.get('labelIds', []),
            attachments=attachments
        )
    
    def get_attachment_data(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """Get attachment data for a specific message and attachment"""
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            if attachment and 'data' in attachment:
                return base64.urlsafe_b64decode(attachment['data'])
            return None
        except Exception as e:
            print(f"Error fetching Gmail attachment data: {e}")
            return None
    
    def mark_as_read(self, message_id: str) -> bool:
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking Gmail message as read: {e}")
            return False
    
    def get_new_messages_since(self, since: datetime) -> List[EmailMessage]:
        try:
            since_str = since.strftime("%Y/%m/%d")
            query = f"after:{since_str}"
            
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = result.get('messages', [])
            detailed_messages = []
            
            if messages:
                batch = BatchHttpRequest()
                results = {}

                def callback(request_id, response, exception):
                    if exception is not None:
                        print(f"Error fetching new message {request_id}: {exception}")
                        results[request_id] = None
                    else:
                        results[request_id] = self._parse_message(response)
                
                for msg in messages:
                    batch.add(self.service.users().messages().get(userId='me', id=msg['id'], format='full'), callback=callback, request_id=msg['id'])
                
                batch.execute()

                for msg_id in [msg['id'] for msg in messages]:
                    if results.get(msg_id):
                        detailed_messages.append(results[msg_id])
            
            return detailed_messages
        except Exception as e:
            print(f"Error fetching new Gmail messages: {e}")
            return []
    
    def setup_webhook(self, webhook_url: str) -> bool:
        # Gmail uses push notifications instead of webhooks
        # This would require setting up Google Cloud Pub/Sub
        return False