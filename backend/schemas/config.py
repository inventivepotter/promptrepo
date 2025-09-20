from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class HostingType(Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    MULTI_TENANT = "multi-tenant"


class HostingConfig(BaseModel):
    """Hosting-specific configuration settings"""
    
    # Hosting Configuration
    type: HostingType = Field(
        default=HostingType.INDIVIDUAL,
        description="Hosting type: individual, organization, or multi-tenant"
    )


class OAuthConfig(BaseModel):
    """Authentication-specific configuration settings"""
    
    # OAuth Configuration
    github_client_id: str = Field(
        default="",
        description="GitHub OAuth client ID"
    )
    
    github_client_secret: str = Field(
        default="",
        description="GitHub OAuth client secret"
    )


class LLMConfig(BaseModel):
    """LLM Provider configuration settings"""
    provider: str = Field(
        default="",
        description="LLM provider name"
    )
    model: str = Field(
        default="",
        description="LLM model name"
    )
    apiKey: str = Field(
        default="",
        description="LLM API key"
    )
    apiBaseUrl: str = Field(
        default="",
        description="LLM API base URL"
    )


class RepoConfig(BaseModel):
    """Repository management settings"""
    repo_url: str = Field(
        default="",
        description="Repository URL"
    )
    base_branch: str = Field(
        default="",
        description="Repository branch"
    )
    current_branch: str = Field(
        default="",
        description="Repository branch"
    )


class AppConfig(BaseModel):
    """Main application configuration"""
    hostingConfig: HostingConfig
    oauthConfig: OAuthConfig | None = None
    llmConfigs: List[LLMConfig] | None = None
    repoConfigs: List[RepoConfig] | None = None