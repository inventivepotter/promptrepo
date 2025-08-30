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

    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-sonnet", description="Default Anthropic model")

    # File paths
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    logs_dir: Path = Field(default=Path("./logs"), description="Logs directory")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.logs_dir.mkdir(exist_ok=True, parents=True)

        # Adjust database path to be absolute if using SQLite
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                absolute_path = self.data_dir / db_path.lstrip("./")
                self.database_url = f"sqlite:///{absolute_path}"


# Create global settings instance
settings = Settings()
