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

from services.config.models import HostingConfig, HostingType, LLMConfig, OAuthConfig, RepoConfig
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
    
    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        """Set OAuth configurations in environment variables."""
        # For organization hosting, OAuth is required and stored in ENV
        if not oauth_configs:
            raise ValueError("OAuth configuration is required for organization hosting type.")
        
        # Convert OAuthConfig objects to dictionaries for JSON serialization
        oauth_configs_dict = [
            {
                "provider": config.provider,
                "client_id": config.client_id,
                "client_secret": config.client_secret
            }
            for config in oauth_configs
        ]
        os.environ["OAUTH_CONFIGS"] = json.dumps(oauth_configs_dict)
        return oauth_configs
    
    def set_llm_configs(self, llm_configs: List[LLMConfig]) -> List[LLMConfig]:
        """Set LLM configuration in environment variables."""
        # For organization hosting, LLM configs are stored in ENV
        if not llm_configs:
            raise ValueError("LLM configuration is required for organization hosting type.")
        
        llm_configs_data = [
            {
                "provider": config.provider,
                "model": config.model,
                "apiKey": config.apiKey,
                "apiBaseUrl": config.apiBaseUrl or ""
            }
            for config in llm_configs
        ]
        os.environ["LLM_CONFIGS"] = json.dumps(llm_configs_data)
        return llm_configs
    
    def set_repo_configs(self, repo_configs: List[RepoConfig]) -> List[RepoConfig] | None:
        """
        Set repository configuration.
        For organization hosting, repo configs are managed per-user in database/session.
        This method doesn't store in ENV but would typically store in user session/DB.
        """
        # TODO: Implement user-specific repo storage (database/session)
        # For now, return the configs as is
        # In production, this would handle user-specific storage
        return repo_configs
    
    def get_hosting_config(self) -> HostingConfig:
        """Get hosting configuration."""
        hosting_config = HostingConfig()
        hosting_type_str = os.environ.get("HOSTING_TYPE", "organization")
        try:
            hosting_config.type = HostingType(hosting_type_str)
        except ValueError:
            hosting_config.type = HostingType.ORGANIZATION
        return hosting_config
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        """Get OAuth configurations from environment variables."""
        oauth_configs_json = os.environ.get("OAUTH_CONFIGS")
        
        if oauth_configs_json:
            try:
                oauth_configs_dict = json.loads(oauth_configs_json)
                oauth_configs = [
                    OAuthConfig(
                        provider=config["provider"],
                        client_id=config["client_id"],
                        client_secret=config["client_secret"]
                    )
                    for config in oauth_configs_dict
                ]
                return oauth_configs
            except (json.JSONDecodeError, KeyError):
                pass
        
        return None
    
    def get_llm_configs(self) -> List[LLMConfig] | None:
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
    
    def get_repo_configs(self) -> List[RepoConfig] | None:
        """
        Get repository configuration.
        For organization hosting, repo configs are retrieved from user context.
        This would typically fetch from database/session based on current user.
        """
        # TODO: Implement fetching from user session/database
        # For now, return None as repos are user-specific
        return None