from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from schemas.hosting_type_enum import HostingType


class LLMConfigScope(Enum):
    ORGANIZATION = "organization"
    USER = "user"


class HostingConfig(BaseModel):
    """Hosting-specific configuration settings"""
    
    # Hosting Configuration
    type: HostingType = Field(
        default=HostingType.INDIVIDUAL,
        description="Hosting type: individual, organization"
    )


class OAuthConfig(BaseModel):
    """Authentication-specific configuration settings"""

    # OAuth Configuration
    provider: str = Field(
        default="",
        description="OAuth provider name (e.g., 'github', 'google', 'microsoft')"
    )
    
    client_id: str = Field(
        default="",
        description="OAuth client ID"
    )
    
    client_secret: str = Field(
        default="",
        description="OAuth client secret"
    )

    redirect_url: str = Field(
        default="",
        description="OAuth redirect URL"
    )


class LLMConfig(BaseModel):
    """LLM Provider configuration settings"""
    id: str = Field(
        description="Unique identifier for the llm configuration"
    )
    provider: str = Field(
        default="",
        description="LLM provider name"
    )
    model: str = Field(
        default="",
        description="LLM model name"
    )
    api_key: str = Field(
        default="",
        description="LLM API key"
    )
    api_base_url: str = Field(
        default="",
        description="LLM API base URL"
    )
    scope: LLMConfigScope = Field(
        default=LLMConfigScope.ORGANIZATION,
        description="Scope of the LLM config: 'organization' for ENV configs, 'user' for user-specific configs"
    )


class RepoConfig(BaseModel):
    """Repository management settings"""
    id: str = Field(
        description="Unique identifier for the repository configuration"
    )
    repo_name: str = Field(
        default="",
        description="Repository name (e.g., 'owner/repo-name')"
    )
    repo_url: str = Field(
        default="",
        description="Repository URL"
    )
    base_branch: str = Field(
        default="main",
        description="Repository base branch"
    )
    current_branch: Optional[str] = Field(
        default="main",
        description="Repository current branch"
    )


class AppConfig(BaseModel):
    """Main application configuration"""
    
    # Main Configuration
    hosting_config: Optional[HostingConfig] = Field(
        default=None,
        description="Hosting-specific configuration settings"
    )
    oauth_configs: Optional[List[OAuthConfig]] = Field(
        default=None,
        description="List of OAuth provider configurations"
    )
    llm_configs: Optional[List[LLMConfig]] = Field(
        default=None,
        description="List of LLM provider configurations"
    )
    repo_configs: Optional[List[RepoConfig]] = Field(
        default=None,
        description="List of repository configurations"
    )