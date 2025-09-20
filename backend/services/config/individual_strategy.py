"""
Configuration strategy for individual hosting type.
Requirements: llmConfigs only
"""

import json
import os
from typing import List

from services.config.models import HostingConfig, HostingType, LLMConfig, OAuthConfig, RepoConfig
from .config_interface import IConfig


class IndividualConfig(IConfig):
    """
    Configuration strategy for individual hosting type.
    Requirements: llmConfigs only
    """
    def set_hosting_type(self) -> HostingConfig:
        """Set hosting type in environment variables."""
        hosting_config = HostingConfig()
        hosting_config.type = HostingType.INDIVIDUAL
        os.environ["HOSTING_TYPE"] = HostingType.INDIVIDUAL.value
        return hosting_config

    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        # For individual hosting, OAuth will not be configured
        return None

    def set_llm_configs(self, llm_configs: List[LLMConfig]) -> List[LLMConfig]:
        """Set LLM configuration in environment variables."""
        # Handle LLM configs
        if llm_configs:
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
        else:
            raise ValueError("LLM configuration is required for individual hosting type.")
        return llm_configs
    
    def set_repo_configs(self, repo_configs: List[RepoConfig]) -> List[RepoConfig] | None:
        # Individual hosting does not manage repo configs
        return None

    def get_hosting_config(self) -> HostingConfig:
        """Get hosting configuration."""
        hosting_config = HostingConfig()
        hosting_type_str = os.environ.get("HOSTING_TYPE", "individual")
        try:
            hosting_config.type = HostingType(hosting_type_str)
        except ValueError:
            hosting_config.type = HostingType.INDIVIDUAL
        return hosting_config
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        """Get OAuth configurations."""
        # For individual hosting, OAuth might not be configured
        return None

    def get_llm_configs(self) -> List[LLMConfig]:
        """Get LLM configuration."""
        llm_configs_str = os.environ.get("LLM_CONFIGS", "[]")
        try:
            llm_configs_data = json.loads(llm_configs_str)
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
            raise ValueError("Invalid LLM_CONFIGS format in environment variables")

    def get_repo_configs(self) -> List[RepoConfig] | None:
        # Individual hosting does not manage repo configs
        return None