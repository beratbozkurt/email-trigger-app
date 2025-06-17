from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import msal
from app.core.config import settings


class OAuthProvider(ABC):
    @abstractmethod
    def get_authorization_url(self) -> str:
        pass
    
    @abstractmethod
    def exchange_code_for_tokens(self, code: str) -> Dict:
        pass
    
    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> Dict:
        pass
    
    @abstractmethod
    def get_user_info(self, access_token: str) -> Dict:
        pass


class GmailOAuth(OAuthProvider):
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.gmail_redirect_uri]
            }
        }
        self.scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    
    def get_authorization_url(self) -> str:
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = settings.gmail_redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = settings.gmail_redirect_uri
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry,
            "provider_type": "gmail"
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.gmail_client_id,
            client_secret=settings.gmail_client_secret
        )
        
        credentials.refresh(Request())
        
        return {
            "access_token": credentials.token,
            "expires_at": credentials.expiry
        }
    
    def get_user_info(self, access_token: str) -> Dict:
        import requests
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()


class OutlookOAuth(OAuthProvider):
    def __init__(self):
        self.client_id = settings.outlook_client_id
        self.client_secret = settings.outlook_client_secret
        self.tenant_id = settings.outlook_tenant_id
        self.redirect_uri = settings.outlook_redirect_uri
        self.scopes = ["https://graph.microsoft.com/Mail.Read", "https://graph.microsoft.com/User.Read"]
        
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )
    
    def get_authorization_url(self) -> str:
        # Build manual authorization URL to avoid MSAL auto-scopes
        import urllib.parse
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_mode': 'query',
            'prompt': 'consent',  # Force consent screen to show permissions
            'state': 'oauth_state_123'  # Add state for security
        }
        
        query_string = urllib.parse.urlencode(params)
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize?{query_string}"
        
        return auth_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        result = self.app.acquire_token_by_authorization_code(
            code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        if "access_token" in result:
            expires_at = datetime.now() + timedelta(seconds=result.get("expires_in", 3600))
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "expires_at": expires_at,
                "provider_type": "outlook"
            }
        else:
            raise Exception(f"Failed to get access token: {result.get('error_description', 'Unknown error')}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        result = self.app.acquire_token_by_refresh_token(
            refresh_token,
            scopes=self.scopes
        )
        
        if "access_token" in result:
            expires_at = datetime.now() + timedelta(seconds=result.get("expires_in", 3600))
            return {
                "access_token": result["access_token"],
                "expires_at": expires_at
            }
        else:
            raise Exception(f"Failed to refresh token: {result.get('error_description', 'Unknown error')}")
    
    def get_user_info(self, access_token: str) -> Dict:
        import requests
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()


def get_oauth_provider(provider_type: str) -> OAuthProvider:
    if provider_type == "gmail":
        return GmailOAuth()
    elif provider_type == "outlook":
        return OutlookOAuth()
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")