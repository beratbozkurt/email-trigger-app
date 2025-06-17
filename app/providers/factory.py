from typing import Optional
from app.email import EmailProvider, GmailProvider, OutlookProvider
from app.auth import get_oauth_provider


class EmailProviderFactory:
    """Factory class for creating email providers"""
    
    @staticmethod
    def create_email_provider(provider_type: str, access_token: str, 
                            refresh_token: Optional[str] = None) -> Optional[EmailProvider]:
        """Create an email provider instance based on type"""
        if provider_type == "gmail":
            return GmailProvider(access_token, refresh_token)
        elif provider_type == "outlook":
            return OutlookProvider(access_token)
        else:
            raise ValueError(f"Unsupported email provider type: {provider_type}")
    
    @staticmethod
    def get_supported_providers() -> list:
        """Get list of supported email providers"""
        return ["gmail", "outlook"]
    
    @staticmethod
    def validate_provider_type(provider_type: str) -> bool:
        """Validate if provider type is supported"""
        return provider_type in EmailProviderFactory.get_supported_providers()


class OAuthProviderFactory:
    """Factory class for creating OAuth providers"""
    
    @staticmethod
    def create_oauth_provider(provider_type: str):
        """Create an OAuth provider instance"""
        return get_oauth_provider(provider_type)
    
    @staticmethod
    def get_supported_oauth_providers() -> list:
        """Get list of supported OAuth providers"""
        return ["gmail", "outlook"]


class ProviderRegistry:
    """Registry to manage and extend providers"""
    
    def __init__(self):
        self._email_providers = {
            "gmail": GmailProvider,
            "outlook": OutlookProvider
        }
        self._oauth_providers = {
            "gmail": "app.auth.oauth.GmailOAuth",
            "outlook": "app.auth.oauth.OutlookOAuth"
        }
    
    def register_email_provider(self, provider_type: str, provider_class):
        """Register a new email provider"""
        self._email_providers[provider_type] = provider_class
    
    def register_oauth_provider(self, provider_type: str, provider_class_path: str):
        """Register a new OAuth provider"""
        self._oauth_providers[provider_type] = provider_class_path
    
    def get_email_provider_class(self, provider_type: str):
        """Get email provider class by type"""
        return self._email_providers.get(provider_type)
    
    def get_oauth_provider_path(self, provider_type: str) -> str:
        """Get OAuth provider class path by type"""
        return self._oauth_providers.get(provider_type)
    
    def list_email_providers(self) -> list:
        """List all registered email providers"""
        return list(self._email_providers.keys())
    
    def list_oauth_providers(self) -> list:
        """List all registered OAuth providers"""
        return list(self._oauth_providers.keys())


# Global registry instance
provider_registry = ProviderRegistry()