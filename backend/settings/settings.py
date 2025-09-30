# backend/settings/base_settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict


class Settings(BaseSettings):
    """Main application settings combining all configuration modules"""
    
    # App Configuration
    app_name: str = Field(default="PromptRepo", description="Application name")
    description: str = Field(default="A repository for AI prompts", description="Application description")
    environment: str = Field(default="development", description="Environment")
    version: str = Field(default="0.1.0", description="Application version")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:////persistence/database/promptrepo.db",
        description="Database URL"
    )
    database_echo: bool = Field(default=True, description="Echo SQL queries")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on changes")

    session_key_expiry_minutes: int = Field(
        default=60,
        description="Session expiry in minutes"
    )

    # Security Configuration
    fernet_key: str = Field(
        default="a_very_secret_default_key_for_development",
        description="Secret key for session and other data encryption"
    )

    # Core Repository Paths
    local_repo_path: str = Field(
        default="persistence/repos/",
        description="Path for individual local repositories"
    )

    multi_user_repo_path: str = Field(
        default="persistence/repos/workspaces/",
        description="Path for multi-user repository workspaces"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Create global settings instance
settings = Settings()
