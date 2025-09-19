"""
Configuration strategy for multi-tenant hosting type.
Requirements: None (always valid)
"""

from typing import List, Dict, Any
from .config_base import ConfigBase


class MultiTenantConfig(ConfigBase):
    """
    Configuration strategy for multi-tenant hosting type.
    Requirements: None (always valid)
    """
    
    def validate(self) -> bool:
        """Multi-tenant configuration is always valid."""
        return True
    
    def get_missing_items(self) -> List[str]:
        """Multi-tenant has no required configs."""
        return []
    
    def set_hosting_type(self, env_dict: Dict[str, str]) -> Dict[str, str]:
        """Set hosting type in environment variables."""
        env_dict["HOSTING_TYPE"] = "multi-tenant"
        return env_dict
    
    def set_oauth_config(self, env_dict: Dict[str, str]) -> Dict[str, str]:
        """Set OAuth configuration in environment variables."""
        # For multi-tenant hosting, OAuth might be handled differently
        return env_dict
    
    def set_llm_config(self, env_dict: Dict[str, str]) -> Dict[str, str]:
        """Set LLM configuration in environment variables."""
        # Multi-tenant doesn't manage LLM configs in env vars
        # These are handled at the tenant level
        return env_dict
    
    def get_hosting_type(self) -> str:
        """Get hosting type."""
        return "multi-tenant"
    
    def get_oauth_config(self) -> Dict[str, Any]:
        """Get OAuth configuration."""
        # For multi-tenant hosting, OAuth might be handled differently
        return {}
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        # For multi-tenant hosting, configuration might be handled differently
        return {"llmConfigs": []}
    
    def is_oauth_required(self) -> bool:
        """Multi-tenant does not require OAuth configuration."""
        return False
    
    def is_llm_required(self) -> bool:
        """Multi-tenant does not require LLM configuration."""
        return False