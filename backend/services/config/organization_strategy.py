"""
Configuration strategy for organization hosting type.
Requirements:
- Hosting type from ENV
- OAuth config from ENV (GitHub Client ID/Secret)
- LLM config from ENV
- Repo config from users (stored in session/database)
"""

import json
import os
from typing import List

from schemas.config import HostingConfig, HostingType, LLMConfig, OAuthConfig, RepoConfig
from .config_interface import IConfig


class OrganizationConfig(IConfig):
    """
    Configuration strategy for organization hosting type.
    - Hosting type: From ENV
    - OAuth: From ENV (GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
    - LLM configs: From ENV (LLM_CONFIGS as JSON)
    - Repo configs: From user context (database/session)
    """
    
    def set_hosting_type(self) -> HostingConfig:
        """Set hosting type in environment variables."""
        hosting_config = HostingConfig()
        hosting_config.type = HostingType.ORGANIZATION
        os.environ["HOSTING_TYPE"] = HostingType.ORGANIZATION.value
        return hosting_config
    
    def set_oauth_config(self, github_client_id: str, github_client_secret: str) -> OAuthConfig:
        """Set OAuth configuration in environment variables."""
        # For organization hosting, OAuth is required and stored in ENV
        if not github_client_id or not github_client_secret:
            raise ValueError("GitHub OAuth configuration is required for organization hosting type.")
        
        os.environ["GITHUB_CLIENT_ID"] = github_client_id
        os.environ["GITHUB_CLIENT_SECRET"] = github_client_secret
        
        oauth_config = OAuthConfig(
            github_client_id=github_client_id,
            github_client_secret=github_client_secret
        )
        return oauth_config
    
    def set_llm_config(self, llm_config: List[LLMConfig]) -> List[LLMConfig]:
        """Set LLM configuration in environment variables."""
        # For organization hosting, LLM configs are stored in ENV
        if not llm_config:
            raise ValueError("LLM configuration is required for organization hosting type.")
        
        llm_configs_data = [
            {
                "provider": config.provider,
                "model": config.model,
                "apiKey": config.apiKey,
                "apiBaseUrl": config.apiBaseUrl or ""
            }
            for config in llm_config
        ]
        os.environ["LLM_CONFIGS"] = json.dumps(llm_configs_data)
        return llm_config
    
    def set_repo_config(self, repo_config: List[RepoConfig]) -> RepoConfig | None:
        """
        Set repository configuration.
        For organization hosting, repo configs are managed per-user in database/session.
        This method doesn't store in ENV but would typically store in user session/DB.
        """
        # TODO: Implement user-specific repo storage (database/session)
        # For now, return the first config or None
        # In production, this would handle user-specific storage
        if repo_config and len(repo_config) > 0:
            return repo_config[0]
        return None
    
    def get_hosting_config(self) -> HostingConfig:
        """Get hosting configuration."""
        hosting_config = HostingConfig()
        hosting_type_str = os.environ.get("HOSTING_TYPE", "organization")
        try:
            hosting_config.type = HostingType(hosting_type_str)
        except ValueError:
            hosting_config.type = HostingType.ORGANIZATION
        return hosting_config
    
    def get_oauth_config(self) -> OAuthConfig | None:
        """Get OAuth configuration from environment variables."""
        github_client_id = os.environ.get("GITHUB_CLIENT_ID", "")
        github_client_secret = os.environ.get("GITHUB_CLIENT_SECRET", "")
        
        # For organization hosting, OAuth should be configured
        if github_client_id and github_client_secret:
            return OAuthConfig(
                github_client_id=github_client_id,
                github_client_secret=github_client_secret
            )
        return None
    
    def get_llm_config(self) -> List[LLMConfig] | None:
        """Get LLM configuration from environment variables."""
        llm_configs_str = os.environ.get("LLM_CONFIGS", "[]")
        try:
            llm_configs_data = json.loads(llm_configs_str)
            if llm_configs_data:
                llm_configs = [
                    LLMConfig(
                        provider=config.get("provider"),
                        model=config.get("model"),
                        apiKey=config.get("apiKey"),
                        apiBaseUrl=config.get("apiBaseUrl") or ""
                    )
                    for config in llm_configs_data
                ]
                return llm_configs
        except json.JSONDecodeError:
            pass
        return None
    
    def get_repo_config(self) -> List[RepoConfig] | None:
        """
        Get repository configuration.
        For organization hosting, repo configs are retrieved from user context.
        This would typically fetch from database/session based on current user.
        """
        # TODO: Implement fetching from user session/database
        # For now, return None as repos are user-specific
        return None