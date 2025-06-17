from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_redirect_uri: str = "http://localhost:8000/auth/gmail/callback"
    
    outlook_client_id: Optional[str] = None
    outlook_client_secret: Optional[str] = None
    outlook_redirect_uri: str = "http://localhost:8000/auth/outlook/callback"
    outlook_tenant_id: str = "common"
    
 
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }


settings = Settings()