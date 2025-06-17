from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

class AttachmentSchema(BaseModel):
    id: Optional[int] = None
    provider_attachment_id: str
    filename: str
    content_type: str
    size: int
    is_downloaded: Optional[bool] = False
    
    # Document AI classification fields
    document_type: Optional[str] = None
    classification_confidence: Optional[float] = None
    page_count: Optional[int] = None
    classification_error: Optional[str] = None
    classification_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True # Was orm_mode = True in older Pydantic versions

class EmailSchema(BaseModel):
    id: Optional[int] = None
    provider_message_id: str
    subject: Optional[str] = None
    sender: str
    recipients: List[str]
    body: Optional[str] = None
    html_body: Optional[str] = None
    received_at: Optional[datetime] = None
    is_read: Optional[bool] = False
    is_important: Optional[bool] = False
    labels: Optional[List[str]] = None
    thread_id: Optional[str] = None
    attachments: Optional[List[AttachmentSchema]] = None

    class Config:
        from_attributes = True # Was orm_mode = True in older Pydantic versions

class EmailResponse(BaseModel):
    provider_type: str
    message: EmailSchema 