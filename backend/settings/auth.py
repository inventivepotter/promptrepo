# backend/settings/auth.py
from pydantic_settings import BaseSettings
from pydantic import Field


class AuthSettings(BaseSettings):
    """Authentication-specific configuration settings"""
    
    # OAuth Configuration
    github_client_id: str = Field(
        default="", 
        description="GitHub OAuth client ID", 
        alias="GITHUB_CLIENT_ID"
    )
    
    github_client_secret: str = Field(
        default="", 
        description="GitHub OAuth client secret", 
        alias="GITHUB_CLIENT_SECRET"
    )

    session_key_expiry_minutes: int = Field(
        default=60, 
        description="Session expiry in minutes"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }