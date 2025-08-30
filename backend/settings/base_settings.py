# backend/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
import json
from schemas.config import AppConfig


class Settings(BaseSettings):
    # App Configuration
    app_name: str = Field(default="PromptRepo", description="Application name")
    description: str = Field(default="A repository for AI prompts", description="Application description")
    environment: str = Field(default="development", description="Environment")
    version: str = Field(default="0.1.0", description="Application version")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./database.db",
        description="Database URL"
    )
    database_echo: bool = Field(default=True, description="Echo SQL queries")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on changes")

    # OAuth Configuration
    redirect_uri: str = Field(default="http://localhost:8080/auth/callback", description="OAuth redirect URI")
    session_key_expiry_minutes: int = Field(default=60, description="Session expiry in minutes")

    # Authentication & App Configuration (Required from ENV)
    hosting_type: Literal["multi-user", "single-user"] = Field(default="multi-user", description="Hosting type: multi-user or single-user", alias="HOSTING_TYPE")
    github_client_id: str = Field(default="", description="GitHub OAuth client ID", alias="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(default="", description="GitHub OAuth client secret", alias="GITHUB_CLIENT_SECRET")
    llm_configs_json: str = Field(default="[]", description="LLM configurations as JSON string", alias="LLM_CONFIGS")

    @property
    def app_config(self) -> AppConfig:
        """Get the structured app configuration"""
        llm_configs = json.loads(self.llm_configs_json) if self.llm_configs_json else []
        return AppConfig(
            hostingType=self.hosting_type,
            githubClientId=self.github_client_id,
            githubClientSecret=self.github_client_secret,
            llmConfigs=llm_configs
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Create global settings instance
settings = Settings()
