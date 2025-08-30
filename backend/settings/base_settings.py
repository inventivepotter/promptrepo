# backend/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    # App Configuration
    app_name: str = Field(default="PromptRepo", description="Application name")
    environment: str = Field(default="development", description="Environment")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./data/promptrepo.db",
        description="Database URL"
    )
    database_echo: bool = Field(default=True, description="Echo SQL queries")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=7768, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on changes")

    # Authentication
    github_client_id: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    github_client_secret: Optional[str] = Field(default=None, description="GitHub OAuth client secret")
    session_key_expiry_minutes: int = Field(default=60, description="Session expiry in minutes")
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-sonnet", description="Default Anthropic model")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()
