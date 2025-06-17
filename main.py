from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload, selectinload
from app.database import get_db, engine
from app.models import User, EmailProvider, Email, Attachment
from app.auth import get_oauth_provider
from app.providers import EmailProviderFactory, provider_registry
from app.triggers import TriggerHandler, create_sample_rules
from app.core.config import settings
from typing import Optional, Dict, List
import uvicorn
import json
from datetime import datetime
from fastapi.responses import Response
from app.schemas import EmailResponse, EmailSchema, AttachmentSchema

app = FastAPI(title="Email Trigger App", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize trigger handler with sample rules
trigger_handler = TriggerHandler()
for rule in create_sample_rules():
    trigger_handler.add_rule(rule)


@app.on_event("startup")
async def startup_event():
    """Initialize database and setup"""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
    print(f"Supported email providers: {provider_registry.list_email_providers()}")


@app.get("/")
async def root():
    return {"message": "Email Trigger App", "version": "1.0.0"}


@app.get("/providers")
async def get_supported_providers():
    """Get list of supported email providers"""
    return {
        "email_providers": provider_registry.list_email_providers(),
        "oauth_providers": provider_registry.list_oauth_providers()
    }


@app.get("/auth/{provider_type}/login")
async def initiate_oauth(provider_type: str):
    """Initiate OAuth login for a provider"""
    try:
        if not EmailProviderFactory.validate_provider_type(provider_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider type: {provider_type}"
            )
        
        oauth_provider = get_oauth_provider(provider_type)
        authorization_url = oauth_provider.get_authorization_url()
        
        return {"authorization_url": authorization_url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/auth/{provider_type}/callback")
async def oauth_callback(
    provider_type: str,
    code: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback and store user tokens"""
    try:
        # Debug logging
        print(f"OAuth callback received - Provider: {provider_type}, Code: {code[:20] if code else None}..., Error: {error}")
        
        # Check for OAuth error
        if error:
            raise Exception(f"OAuth error from provider: {error}")
        
        if not code:
            raise Exception("No authorization code provided by OAuth provider")
        
        oauth_provider = get_oauth_provider(provider_type)
        
        # Exchange code for tokens
        token_data = oauth_provider.exchange_code_for_tokens(code)
        
        # Get user info
        user_info = oauth_provider.get_user_info(token_data["access_token"])
        
        # Debug logging
        print(f"User info received: {user_info}")
        
        # Extract email and name with fallbacks
        email = user_info.get("email") or user_info.get("mail") or user_info.get("userPrincipalName")
        name = user_info.get("name") or user_info.get("displayName") or "Unknown User"
        
        if not email:
            raise Exception(f"No email found in user info: {user_info}")
        
        # Create or get user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create or update email provider
        email_provider = db.query(EmailProvider).filter(
            EmailProvider.user_id == user.id,
            EmailProvider.provider_type == provider_type
        ).first()
        
        if not email_provider:
            email_provider = EmailProvider(
                user_id=user.id,
                provider_type=provider_type,
                email_address=email,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_expires_at=token_data.get("expires_at")
            )
            db.add(email_provider)
        else:
            email_provider.access_token = token_data["access_token"]
            email_provider.refresh_token = token_data.get("refresh_token")
            email_provider.token_expires_at = token_data.get("expires_at")
            email_provider.is_active = True
        
        db.commit()
        
        # Return HTML page that redirects to frontend
        from fastapi.responses import HTMLResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .loading {{ animation: spin 1s linear infinite; }}
                @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            </style>
        </head>
        <body>
            <div class="loading">⟳</div>
            <h2>Authentication Successful!</h2>
            <p>Redirecting you back to the application...</p>
            <script>
                // Store user data in localStorage
                const userData = {{
                    user_id: {user.id},
                    provider_id: {email_provider.id},
                    email: "{user.email}",
                    message: "OAuth login successful"
                }};
                
                console.log('🔄 Storing user data in localStorage:', userData);
                
                // Store user data and redirect
                localStorage.setItem('emailTriggerUser', JSON.stringify(userData));
                
                // Verify storage
                const stored = localStorage.getItem('emailTriggerUser');
                console.log('✅ Verified stored data:', stored);
                
                // Encode user data for URL to ensure it gets through
                const encodedUserData = encodeURIComponent(JSON.stringify(userData));
                
                // Force redirect to frontend with success flag and user data
                setTimeout(() => {{
                    window.location.href = `http://localhost:3000?oauth_success=true&user_data=${{encodedUserData}}`;
                }}, 1500);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        db.rollback()
        # Log the error for debugging
        print(f"OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error page instead of JSON error
        from fastapi.responses import HTMLResponse
        error_details = str(e).replace('"', "'")  # Escape quotes for HTML
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; color: #e74c3c; }}
                .error-details {{ background: #f8f9fa; padding: 15px; margin: 20px; border-radius: 5px; font-family: monospace; text-align: left; }}
            </style>
        </head>
        <body>
            <h2>Authentication Failed</h2>
            <div class="error-details">
                <strong>Error Details:</strong><br>
                {error_details}
            </div>
            <p>Redirecting you back to try again...</p>
            <script>
                setTimeout(() => {{
                    window.location.href = 'http://localhost:3000?oauth_error=true';
                }}, 5000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html)


@app.get("/users/{user_id}/emails")
async def get_user_emails(
    user_id: int,
    limit: int = 10,
    from_db: bool = False,
    db: Session = Depends(get_db)
):
    """Get user's emails"""
    try:
        if from_db:
            # Get emails from database
            emails = db.query(Email).options(
                joinedload(Email.email_provider),
                selectinload(Email.attachments)
            ).filter(
                Email.user_id == user_id
            ).order_by(
                Email.received_at.desc()
            ).limit(limit).all()
            
            return {
                "emails": [
                    EmailResponse(
                        provider_type=email.email_provider.provider_type,
                        message=EmailSchema(
                            id=email.id,
                            provider_message_id=email.external_id,
                            subject=email.subject,
                            sender=email.sender,
                            recipients=email.recipients,
                            body=email.body,
                            html_body=email.html_body,
                            received_at=email.received_at,
                            is_read=email.is_read,
                            labels=email.labels,
                            thread_id=email.thread_id,
                            attachments=[
                                AttachmentSchema(
                                    id=attachment.id,
                                    provider_attachment_id=attachment.external_id,
                                    filename=attachment.filename,
                                    content_type=attachment.content_type,
                                    size=attachment.size,
                                    is_downloaded=attachment.is_downloaded,
                                    document_type=attachment.document_type,
                                    classification_confidence=attachment.classification_confidence,
                                    page_count=attachment.page_count,
                                    classification_error=attachment.classification_error,
                                    classification_metadata=attachment.classification_metadata
                                )
                                for attachment in email.attachments
                            ]
                        )
                    ).model_dump(mode='json', exclude_none=True)
                    for email in emails
                ],
                "source": "database"
            }
        
        else:
            # Get emails live from email providers (existing behavior)
            providers = db.query(EmailProvider).filter(
                EmailProvider.user_id == user_id,
                EmailProvider.is_active == True
            ).all()
            
            if not providers:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active email providers found"
                )
            
            all_emails = []
            for provider in providers:
                email_provider = EmailProviderFactory.create_email_provider(
                    provider.provider_type,
                    provider.access_token,
                    provider.refresh_token
                )
                
                if email_provider:
                    result = email_provider.get_messages(limit=limit)
                    for message in result.get("messages", []):
                        attachments_for_schema = []
                        if hasattr(message, 'attachments') and message.attachments:
                            # Collect all external attachment and email IDs
                            attachment_external_ids = [att.get('id') for att in message.attachments if att.get('id')]
                            email_external_id = message.id

                            # Batch query for attachments and their associated emails from the database
                            if attachment_external_ids and email_external_id:
                                db_attachments = db.query(Attachment).join(Email).filter(
                                    Attachment.external_id.in_(attachment_external_ids),
                                    Email.external_id == email_external_id,
                                    Email.user_id == user_id
                                ).all()
                                db_attachments_map = {
                                    att.external_id: att for att in db_attachments
                                }
                            else:
                                db_attachments_map = {}

                            for att in message.attachments:
                                # Look up document type from the batch-queried database attachments
                                db_attachment = db_attachments_map.get(att.get('id'))
                                
                                attachments_for_schema.append(
                                    AttachmentSchema(
                                        id=db_attachment.id if db_attachment else None,
                                        provider_attachment_id=att.get('id'),
                                        filename=att.get('filename'),
                                        content_type=att.get('content_type'),
                                        size=att.get('size'),
                                        is_downloaded=att.get('is_downloaded', False),
                                        document_type=db_attachment.document_type if db_attachment else None,
                                        classification_confidence=db_attachment.classification_confidence if db_attachment else None,
                                        page_count=db_attachment.page_count if db_attachment else None,
                                        classification_error=db_attachment.classification_error if db_attachment else None,
                                        classification_metadata=db_attachment.classification_metadata if db_attachment else None
                                    ).model_dump(mode='json', exclude_none=True)
                                )

                        all_emails.append(
                            EmailResponse(
                                provider_type=provider.provider_type,
                                message=EmailSchema(
                                    id=None, # Live emails don't have a DB ID yet
                                    provider_message_id=message.id,
                                    subject=message.subject,
                                    sender=message.sender,
                                    recipients=message.recipients,
                                    body=message.body,
                                    html_body=message.html_body,
                                    received_at=message.received_at,
                                    is_read=message.is_read,
                                    labels=message.labels,
                                    thread_id=message.thread_id,
                                    attachments=attachments_for_schema
                                )
                            ).model_dump(mode='json', exclude_none=True)
                        )
            
            return {"emails": all_emails, "source": "live"}
    
    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()
        # Log the error for debugging
        print(f"Error fetching user emails: {str(e)}")
        print(full_traceback)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred. Details: {full_traceback}"
        )


@app.get("/users/{user_id}/triggers")
async def get_user_triggers(user_id: int):
    """Get all trigger rules for a user"""
    user_rules = trigger_handler.rules.get(user_id, [])
    
    # Convert TriggerRule objects to dictionaries
    rules_data = []
    for rule in user_rules:
        rules_data.append({
            "id": rule.id,
            "name": f"Trigger {rule.id}",
            "triggerType": rule.trigger_type.value,
            "condition": rule.condition,
            "action": rule.action,
            "isActive": rule.is_active,
            "metadata": rule.metadata or {},
            "description": f"{rule.trigger_type.value.replace('_', ' ').title()} trigger"
        })
    
    return {"triggers": rules_data}


@app.post("/users/{user_id}/triggers")
async def create_trigger(user_id: int, trigger_data: dict):
    """Create a new trigger rule for a user"""
    from app.triggers.handler import TriggerRule, TriggerType
    
    # Generate new rule ID
    import uuid
    rule_id = f"rule_{uuid.uuid4().hex[:8]}"
    
    # Create new trigger rule
    rule = TriggerRule(
        id=rule_id,
        user_id=user_id,
        trigger_type=TriggerType(trigger_data["triggerType"]),
        condition=trigger_data.get("condition", ""),
        action=trigger_data["action"],
        is_active=True,
        metadata=trigger_data.get("metadata", {})
    )
    
    trigger_handler.add_rule(rule)
    
    return {
        "message": "Trigger created successfully",
        "trigger": {
            "id": rule.id,
            "name": trigger_data.get("name", f"Trigger {rule.id}"),
            "triggerType": rule.trigger_type.value,
            "condition": rule.condition,
            "action": rule.action,
            "isActive": rule.is_active,
            "metadata": rule.metadata,
            "description": trigger_data.get("description", "")
        }
    }


@app.put("/users/{user_id}/triggers/{trigger_id}")
async def update_trigger(user_id: int, trigger_id: str, trigger_data: dict):
    """Update an existing trigger rule"""
    from app.triggers.handler import TriggerType
    
    # Find and remove the old rule
    if user_id in trigger_handler.rules:
        trigger_handler.rules[user_id] = [
            rule for rule in trigger_handler.rules[user_id]
            if rule.id != trigger_id
        ]
    
    # Create updated rule
    from app.triggers.handler import TriggerRule
    rule = TriggerRule(
        id=trigger_id,
        user_id=user_id,
        trigger_type=TriggerType(trigger_data["triggerType"]),
        condition=trigger_data.get("condition", ""),
        action=trigger_data["action"],
        is_active=trigger_data.get("isActive", True),
        metadata=trigger_data.get("metadata", {})
    )
    
    trigger_handler.add_rule(rule)
    
    return {
        "message": "Trigger updated successfully",
        "trigger": {
            "id": rule.id,
            "name": trigger_data.get("name", f"Trigger {rule.id}"),
            "triggerType": rule.trigger_type.value,
            "condition": rule.condition,
            "action": rule.action,
            "isActive": rule.is_active,
            "metadata": rule.metadata,
            "description": trigger_data.get("description", "")
        }
    }


@app.delete("/users/{user_id}/triggers/{trigger_id}")
async def delete_trigger(user_id: int, trigger_id: str):
    """Delete a trigger rule"""
    trigger_handler.remove_rule(user_id, trigger_id)
    return {"message": "Trigger deleted successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.get("/auth/test-oauth")
async def test_oauth_flow(db: Session = Depends(get_db)):
    """Test OAuth flow with dummy data for development"""
    try:
        # Create a test user
        user = User(
            email="test@example.com",
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create a test email provider
        email_provider = EmailProvider(
            user_id=user.id,
            provider_type="outlook",
            email_address=user.email,
            access_token="test_token",
            refresh_token="test_refresh",
            is_active=True
        )
        db.add(email_provider)
        db.commit()
        
        # Return success HTML
        from fastapi.responses import HTMLResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test OAuth Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .success {{ color: #27ae60; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h2>✅ Test Authentication Successful!</h2>
                <p>Test user created and logged in</p>
                <p>Redirecting to dashboard...</p>
            </div>
            <script>
                const userData = {{
                    user_id: {user.id},
                    provider_id: {email_provider.id},
                    email: "{user.email}",
                    message: "Test OAuth login successful"
                }};
                
                localStorage.setItem('emailTriggerUser', JSON.stringify(userData));
                setTimeout(() => {{
                    window.location.href = 'http://localhost:3000?oauth_success=true';
                }}, 2000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/test-email-notification/{user_id}")
async def test_email_notification(user_id: int, db: Session = Depends(get_db)):
    """Test email notification for a user"""
    try:
        # Get user's active email provider
        provider = db.query(EmailProvider).filter(
            EmailProvider.user_id == user_id,
            EmailProvider.is_active == True
        ).first()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active email provider found for user"
            )
        
        # Get provider instance
        email_provider = EmailProviderFactory.create_email_provider(
            provider.provider_type,
            provider.access_token,
            provider.refresh_token
        )
        
        # Test notification
        try:
            # Create a test message
            test_message = EmailMessage(
                id="test-message-id",
                subject="Test Notification",
                sender="test@example.com",
                recipients=[provider.email_address],
                body="This is a test notification message.",
                received_at=datetime.now()
            )
            
            # Process the test message
            await process_new_email(user_id, provider.id, test_message.__dict__)
            
            return {"status": "success", "message": "Test notification sent"}
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/debug-oauth-credentials")
async def debug_oauth_credentials():
    """Debug endpoint to check OAuth credentials"""
    return {
        "outlook": {
            "client_id": settings.OUTLOOK_CLIENT_ID,
            "client_secret": settings.OUTLOOK_CLIENT_SECRET,
            "redirect_uri": settings.OUTLOOK_REDIRECT_URI
        },
        "gmail": {
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "redirect_uri": settings.GMAIL_REDIRECT_URI
        }
    }


@app.get("/attachments/{attachment_id}")
async def download_attachment(attachment_id: str, db: Session = Depends(get_db)):
    """Download an email attachment"""
    try:
        # Try to find by external ID first since that's what we're getting from the frontend
        attachment = db.query(Attachment).filter(Attachment.external_id == attachment_id).first()
        
        # If not found, try to find by internal ID (in case it's a numeric ID)
        if not attachment and attachment_id.isdigit():
            attachment = db.query(Attachment).filter(Attachment.id == int(attachment_id)).first()
        
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        
        return Response(
            content=attachment.data,
            media_type=attachment.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{attachment.filename}"'
            }
        )
    except Exception as e:
        print(f"Error downloading attachment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )