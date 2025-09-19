"""
Configuration strategy for individual hosting type.
Requirements: llmConfigs only
"""

import json
import os
from typing import List, Dict, Any

from schemas.config import HostingConfig, HostingType, LLMConfig, OAuthConfig
from .config_base import ConfigBase


class IndividualConfig(ConfigBase):
    """
    Configuration strategy for individual hosting type.
    Requirements: llmConfigs only
    """
    
    def validate(self) -> bool:
        """Individual hosting requires only LLM configs."""
        return bool(self.get_hosting_config() and self.get_llm_config())
    
    def set_hosting_type(self) -> HostingConfig:
        """Set hosting type in environment variables."""
        hosting_config = HostingConfig()
        hosting_config.type = HostingType.INDIVIDUAL
        os.environ["HOSTING_TYPE"] = HostingType.INDIVIDUAL.value
        return hosting_config

    def set_oauth_config(self, oauth_config_json: Dict[str, str]) -> None:
        """Set OAuth configuration in environment variables."""
        # For individual hosting, OAuth might not be configured
        return None

    def set_llm_config(self, llm_config_json: Dict[str, str]) -> LLMConfig:
        """Set LLM configuration in environment variables."""
        # Handle LLM configs
        if llm_config_json:
            llm_configs_data = [
                {
                    "provider": config.provider,
                    "model": config.model,
                    "apiKey": config.apiKey,
                    "apiBaseUrl": config.apiBaseUrl or ""
                }
                for config in llm_config_json
            ]
            env_dict["LLM_CONFIGS"] = json.dumps(llm_configs_data)
        else:
            env_dict["LLM_CONFIGS"] = "[]"
        return env_dict
    
    def get_hosting_type(self) -> str:
        """Get hosting type."""
        return os.environ.get("HOSTING_TYPE", "individual")
    
    def get_oauth_config(self) -> Dict[str, Any]:
        """Get OAuth configuration."""
        # For individual hosting, OAuth might not be configured
        return {}
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        if self._config.llmConfigs:
            return {
                "llmConfigs": [
                    {
                        "provider": config.provider,
                        "model": config.model,
                        "apiKey": config.apiKey,
                        "apiBaseUrl": config.apiBaseUrl or ""
                    }
                    for config in self._config.llmConfigs
                ]
            }
        return {"llmConfigs": []}
    
    def is_oauth_required(self) -> bool:
        """Individual hosting does not require OAuth."""
        return False
    
    def is_llm_required(self) -> bool:
        """Individual hosting requires LLM configuration."""
        return True