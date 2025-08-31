# backend/settings/base_settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from schemas.config import AppConfig, LlmConfig
from .hosting import HostingSettings
from .auth import AuthSettings
from .llm import LLMSettings
from .admin import AdminSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    """Main application settings combining all configuration modules"""
    
    # App Configuration
    app_name: str = Field(default="PromptRepo", description="Application name")
    description: str = Field(default="A repository for AI prompts", description="Application description")
    environment: str = Field(default="development", description="Environment")
    version: str = Field(default="0.1.0", description="Application version")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./persistence/database/promptrepo.db",
        description="Database URL"
    )
    database_echo: bool = Field(default=True, description="Echo SQL queries")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on changes")

    # Session Configuration
    redirect_uri: str = Field(
        default="http://localhost:8080/auth/callback",
        description="OAuth redirect URI"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize sub-settings
        self._hosting_settings = HostingSettings()
        self._auth_settings = AuthSettings()
        self._llm_settings = LLMSettings()
        self._admin_settings = AdminSettings()

    def reload_settings(self):
        """Reload all settings from environment variables and .env file"""
        # Reload environment variables from .env file
        load_dotenv(override=True)
        
        # Reinitialize all sub-settings to pick up new values
        self._hosting_settings = HostingSettings()
        self._auth_settings = AuthSettings()
        self._llm_settings = LLMSettings()
        self._admin_settings = AdminSettings()

    @property
    def hosting_settings(self) -> HostingSettings:
        """Get hosting configuration"""
        return self._hosting_settings

    @property
    def auth_settings(self) -> AuthSettings:
        """Get auth configuration"""
        return self._auth_settings

    @property
    def llm_settings(self) -> LLMSettings:
        """Get LLM configuration"""
        return self._llm_settings

    @property
    def admin_settings(self) -> AdminSettings:
        """Get admin configuration"""
        return self._admin_settings

    @property
    def app_config(self) -> AppConfig:
        """Get the structured app configuration with proper null handling"""
        hosting_type = self.hosting_settings.hosting_type
        
        # Handle conditional configurations based on hosting type
        github_client_id = ""
        github_client_secret = ""
        llm_configs = []
        admin_emails = []
        
        if hosting_type == "organization":
            # Organization needs all configurations
            github_client_id = self.auth_settings.github_client_id or ""
            github_client_secret = self.auth_settings.github_client_secret or ""
            # Convert dict configs to LlmConfig objects
            raw_configs = self.llm_settings.llm_configs or []
            llm_configs = [LlmConfig(**config) for config in raw_configs] if raw_configs else []
            admin_emails = self.admin_settings.admin_emails_list or []
        elif hosting_type == "individual":
            # Individual only needs LLM configs, no auth or admin
            raw_configs = self.llm_settings.llm_configs or []
            llm_configs = [LlmConfig(**config) for config in raw_configs] if raw_configs else []
        elif hosting_type == "multi-tenant":
            # Multi-tenant has no global LLM configs, but has admin configs
            admin_emails = self.admin_settings.admin_emails_list or []
        
        return AppConfig(
            hostingType=hosting_type,
            githubClientId=github_client_id,
            githubClientSecret=github_client_secret,
            llmConfigs=llm_configs,
            adminEmails=admin_emails
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Create global settings instance
settings = Settings()
