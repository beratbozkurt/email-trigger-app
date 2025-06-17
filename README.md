# Email Trigger App

A cross-provider email monitoring application with OAuth2 authentication, unified email interface, and extensible trigger system.

## Features

- 🔐 **OAuth2 Authentication** - Support for Gmail and Outlook
- 📥 **Unified Email Interface** - Single API for multiple email providers
- 🧠 **Smart Triggers** - Configurable rules for email processing
- 🔄 **Always-On Monitoring** - Background workers with Celery
- 🪄 **Extensible Architecture** - Easy to add new providers
- ♻️ **Token Management** - Automatic token refresh

## Architecture

```
app/
├── auth/           # OAuth2 providers
├── core/           # Configuration
├── database/       # Database connection
├── email/          # Email providers (Gmail, Outlook)
├── models/         # SQLAlchemy models
├── providers/      # Provider factory & registry
├── triggers/       # Trigger handler system
└── workers/        # Background tasks (Celery)
```

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repo>
   cd email-trigger
   cp .env.example .env
   ```

2. **Configure OAuth credentials** in `.env`:
   ```env
   GMAIL_CLIENT_ID=your-gmail-client-id
   GMAIL_CLIENT_SECRET=your-gmail-client-secret
   OUTLOOK_CLIENT_ID=your-outlook-client-id
   OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
   ```

3. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Or run locally:**
   ```bash
   pip install -r requirements.txt
   
   # Start database
   docker run -d -p 5432:5432 -e POSTGRES_DB=email_trigger -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15
   
   # Start Redis
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Run migrations
   alembic upgrade head
   
   # Start app
   uvicorn main:app --reload
   
   # Start workers (in separate terminals)
   celery -A app.workers.celery_app worker --loglevel=info
   celery -A app.workers.celery_app beat --loglevel=info
   ```

## API Endpoints

### Authentication
- `GET /auth/{provider}/login` - Start OAuth flow
- `POST /auth/{provider}/callback` - Handle OAuth callback

### Emails
- `GET /users/{user_id}/emails` - Get user emails
- `POST /users/{user_id}/test-trigger` - Test trigger system

### System
- `GET /providers` - List supported providers
- `GET /health` - Health check

## Trigger System

The app supports various trigger types:

```python
# Example triggers
TriggerRule(
    trigger_type=TriggerType.SENDER_CONTAINS,
    condition="boss@company.com",
    action="send_notification"
)

TriggerRule(
    trigger_type=TriggerType.SUBJECT_REGEX,
    condition=r"urgent|emergency",
    action="forward_email"
)
```

### Available Trigger Types:
- `SENDER_CONTAINS` - Match sender email
- `SUBJECT_CONTAINS` - Match subject text
- `BODY_CONTAINS` - Match email body
- `SUBJECT_REGEX` - Regex pattern matching
- `ATTACHMENT_EXISTS` - Has attachments
- `TIME_RANGE` - Time-based rules

### Available Actions:
- `log_message` - Log to console
- `mark_as_read` - Mark email as read
- `forward_email` - Forward to address
- `send_notification` - Send notification
- `webhook_call` - Call HTTP webhook
- `custom_script` - Execute custom script

## Adding New Providers

1. **Create email provider:**
   ```python
   # app/email/newprovider_provider.py
   class NewProviderProvider(EmailProvider):
       def get_messages(self, limit=10):
           # Implementation
           pass
   ```

2. **Create OAuth provider:**
   ```python
   # app/auth/oauth.py
   class NewProviderOAuth(OAuthProvider):
       def get_authorization_url(self):
           # Implementation
           pass
   ```

3. **Register in factory:**
   ```python
   provider_registry.register_email_provider("newprovider", NewProviderProvider)
   ```

## Background Workers

The app uses Celery for background processing:

- **Email Monitor** - Checks for new emails every 30 seconds
- **Token Refresh** - Automatically refreshes expired tokens
- **Trigger Processing** - Handles email triggers asynchronously

## Configuration

Key environment variables:

```env
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key

# OAuth Credentials
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

## OAuth Setup

### Gmail
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project and enable Gmail API
3. Create OAuth2 credentials
4. Add redirect URI: `http://localhost:8000/auth/gmail/callback`

### Outlook
1. Go to [Azure Portal](https://portal.azure.com)
2. Register app in Azure AD
3. Add API permissions for Microsoft Graph
4. Add redirect URI: `http://localhost:8000/auth/outlook/callback`

## License

MIT License