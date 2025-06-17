from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EmailMessage:
    id: str
    subject: str
    sender: str
    recipients: List[str]
    body: str
    html_body: Optional[str] = None
    received_at: Optional[datetime] = None
    attachments: List[Dict] = None
    thread_id: Optional[str] = None
    labels: List[str] = None
    is_read: bool = False


class EmailProvider(ABC):
    @abstractmethod
    def get_messages(self, limit: int = 10, page_token: str = None) -> Dict:
        pass
    
    @abstractmethod
    def get_message_by_id(self, message_id: str) -> EmailMessage:
        pass
    
    @abstractmethod
    def mark_as_read(self, message_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_new_messages_since(self, since: datetime) -> List[EmailMessage]:
        pass
    
    @abstractmethod
    def setup_webhook(self, webhook_url: str) -> bool:
        pass
    
    @abstractmethod
    def get_attachment_data(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        pass