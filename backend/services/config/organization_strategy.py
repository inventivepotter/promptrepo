"""
Configuration strategy for organization hosting type.
Requirements: githubClientId, githubClientSecret, llmConfigs
"""

import json
from typing import List, Dict, Any
from .config_base import ConfigBase


class OrganizationConfig(ConfigBase):
    """
    Configuration strategy for organization hosting type.
    Requirements: githubClientId, githubClientSecret, llmConfigs
    """
    
    def validate(self) -> bool:
        """Organization hosting requires GitHub OAuth and LLM configs."""
        return bool(
            self._config.githubClientId and 
            self._config.githubClientSecret and 
            self._config.llmConfigs
        )
    
    def get_missing_items(self) -> List[str]:
        """Check for missing OAuth and LLM configs."""
        missing = []
        if not self._config.githubClientId:
            missing.append("githubClientId")
        if not self._config.githubClientSecret:
            missing.append("githubClientSecret")
        if not self._config.llmConfigs:
            missing.append("llmConfigs")
        return missing
    
    def set_hosting_type(self, env_dict: Dict[str, str]) -> Dict[str, str]:
        """Set hosting type in environment variables."""
        env_dict["HOSTING_TYPE"] = "organization"
        return env_dict
    
    def set_oauth_config(self, env_dict: Dict[str, str]) -> Dict[str, str]:
        """Set OAuth configuration in environment variables."""
        # Handle OAuth settings
        if self._config.githubClientId:
            env_dict["GITHUB_CLIENT_ID"] = self._config.githubClientId
        if self._config.githubClientSecret:
            env_dict["GITHUB_CLIENT_SECRET"] = self._config.githubClientSecret
        return env_dict
    
    def set_llm_config(self, env_dict: Dict[str, str]) -> Dict[str, str]:
        """Set LLM configuration in environment variables."""
        # Handle LLM configs
        if self._config.llmConfigs:
            llm_configs_data = [
                {
                    "provider": config.provider,
                    "model": config.model,
                    "apiKey": config.apiKey,
                    "apiBaseUrl": config.apiBaseUrl or ""
                }
                for config in self._config.llmConfigs
            ]
            env_dict["LLM_CONFIGS"] = json.dumps(llm_configs_data)
        else:
            env_dict["LLM_CONFIGS"] = "[]"
        return env_dict
    
    def get_hosting_type(self) -> str:
        """Get hosting type."""
        return "organization"
    
    def get_oauth_config(self) -> Dict[str, Any]:
        """Get OAuth configuration."""
        return {
            "githubClientId": self._config.githubClientId if self._config.githubClientId else None,
            "githubClientSecret": self._config.githubClientSecret if self._config.githubClientSecret else None
        }
    
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
        """Organization hosting requires OAuth."""
        return True
    
    def is_llm_required(self) -> bool:
        """Organization hosting requires LLM configuration."""
        return True