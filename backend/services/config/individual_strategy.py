"""
Configuration strategy for individual hosting type.
Requirements: llmConfigs only
"""

import json
import os
from typing import List, Dict, Any

from schemas.config import AppConfig, HostingConfig, HostingType, LLMConfig, OAuthConfig, RepoConfig
from .config_base import ConfigBase


class IndividualConfig(ConfigBase):
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

    def set_oauth_config(self, github_client_id: str, github_client_secret: str) -> None:
        # For individual hosting, OAuth will not be configured
        return None

    def set_llm_config(self, llm_config: List[LLMConfig]) -> List[LLMConfig]:
        """Set LLM configuration in environment variables."""
        # Handle LLM configs
        if llm_config:
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
        else:
            raise ValueError("LLM configuration is required for individual hosting type.")
        return llm_config
    
    def set_repo_config(self, repo_config: List[RepoConfig]) -> None:
        # Individual hosting does not manage repo configs
        return None

    def get_hosting_type(self) -> str:
        """Get hosting type."""
        return os.environ.get("HOSTING_TYPE", "individual")
    
    def get_oauth_config(self) -> None:
        """Get OAuth configuration."""
        # For individual hosting, OAuth might not be configured
        return None

    def get_llm_config(self) -> List[LLMConfig]:
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

    def get_repo_config(self) -> List[RepoConfig] | None:
        # Individual hosting does not manage repo configs
        return None  