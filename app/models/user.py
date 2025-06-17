from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, LargeBinary, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    email_providers = relationship("EmailProvider", back_populates="user")
    emails = relationship("Email", back_populates="user")


class EmailProvider(Base):
    __tablename__ = "email_providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_type = Column(String, nullable=False)  # 'gmail', 'outlook'
    email_address = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="email_providers")
    emails = relationship("Email", back_populates="email_provider")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String, nullable=False, index=True)  # Gmail/Outlook attachment ID
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)  # Size in bytes
    data = Column(LargeBinary, nullable=True)  # The actual file data
    is_downloaded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Document AI classification fields
    document_type = Column(String, nullable=True)
    classification_confidence = Column(Float, nullable=True)
    page_count = Column(Integer, nullable=True)
    classification_error = Column(String, nullable=True)
    classification_metadata = Column(JSON, nullable=True)
    last_extracted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    email = relationship("Email", back_populates="attachments")


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, nullable=False, index=True)  # Gmail/Outlook message ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("email_providers.id"), nullable=False)
    
    # Email metadata
    subject = Column(String, nullable=True)
    sender = Column(String, nullable=False, index=True)
    recipients = Column(JSON, nullable=True)  # Array of recipient emails
    thread_id = Column(String, nullable=True, index=True)  # Conversation/thread ID
    
    # Email content
    body = Column(Text, nullable=True)
    html_body = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    is_important = Column(Boolean, default=False)
    labels = Column(JSON, nullable=True)  # Array of labels/folders
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=True, index=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="emails")
    email_provider = relationship("EmailProvider", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")
    
    # Unique constraint to prevent duplicate emails
    __table_args__ = (
        UniqueConstraint('external_id', 'provider_id', name='uix_email_provider'),
    )