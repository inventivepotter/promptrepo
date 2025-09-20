"""
Configuration strategy for multi-tenant hosting type.
Requirements:
- Hosting type from ENV
- OAuth config from ENV (system-wide)
- LLM config from users (tenant-specific)
- Repo config from users (tenant-specific)
"""

import os
import json
from typing import List

from services.config.models import HostingConfig, HostingType, LLMConfig, OAuthConfig, RepoConfig
from .config_interface import IConfig


class MultiTenantConfig(IConfig):
    """
    Configuration strategy for multi-tenant hosting type.
    - Hosting type: From ENV
    - OAuth: From ENV (system-wide OAuth for all tenants)
    - LLM configs: From user/tenant context (database/session)
    - Repo configs: From user/tenant context (database/session)
    """
    
    # In-memory storage for tenant-specific configurations
    # In production, this would be replaced with database/session storage
    _tenant_configs = {}
    
    @classmethod
    def _get_current_tenant_id(cls) -> str:
        """
        Get the current tenant ID.
        In production, this would come from session/auth context.
        For now, we'll use a default tenant ID for demonstration.
        """
        # TODO: In production, retrieve from request context/session
        return os.environ.get("TENANT_ID", "default_tenant")
    
    @classmethod
    def _get_tenant_storage(cls, tenant_id: str) -> dict:
        """Get or create storage for a specific tenant."""
        if tenant_id not in cls._tenant_configs:
            cls._tenant_configs[tenant_id] = {
                "llm_configs": None,
                "repo_configs": None
            }
        return cls._tenant_configs[tenant_id]
    
    def set_hosting_type(self) -> HostingConfig:
        """Set hosting type in environment variables."""
        hosting_config = HostingConfig()
        hosting_config.type = HostingType.MULTI_TENANT
        os.environ["HOSTING_TYPE"] = HostingType.MULTI_TENANT.value
        return hosting_config
    
    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        """
        Set OAuth configurations in environment variables.
        For multi-tenant, OAuth is system-wide and stored in ENV.
        """
        if oauth_configs:
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
        return None
    
    def set_llm_configs(self, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        """
        Set LLM configuration.
        For multi-tenant hosting, LLM configs are stored per-tenant in database/session.
        This implementation uses in-memory storage to demonstrate the pattern.
        """
        tenant_id = self._get_current_tenant_id()
        tenant_storage = self._get_tenant_storage(tenant_id)
        tenant_storage["llm_configs"] = llm_configs
        return llm_configs
    
    def set_repo_configs(self, repo_configs: List[RepoConfig]) -> List[RepoConfig] | None:
        """
        Set repository configuration.
        For multi-tenant hosting, repo configs are stored per-tenant in database/session.
        This implementation uses in-memory storage to demonstrate the pattern.
        """
        tenant_id = self._get_current_tenant_id()
        tenant_storage = self._get_tenant_storage(tenant_id)
        tenant_storage["repo_configs"] = repo_configs
        return repo_configs
    
    def get_hosting_config(self) -> HostingConfig:
        """Get hosting configuration."""
        hosting_config = HostingConfig()
        hosting_type_str = os.environ.get("HOSTING_TYPE", "multi-tenant")
        try:
            hosting_config.type = HostingType(hosting_type_str)
        except ValueError:
            hosting_config.type = HostingType.MULTI_TENANT
        return hosting_config
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        """
        Get OAuth configurations from environment variables.
        For multi-tenant, OAuth is system-wide.
        """
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
        """
        Get LLM configuration.
        For multi-tenant hosting, LLM configs are retrieved from tenant context.
        This implementation uses in-memory storage to demonstrate the pattern.
        """
        tenant_id = self._get_current_tenant_id()
        tenant_storage = self._get_tenant_storage(tenant_id)
        return tenant_storage.get("llm_configs")
    
    def get_repo_configs(self) -> List[RepoConfig] | None:
        """
        Get repository configuration.
        For multi-tenant hosting, repo configs are retrieved from tenant context.
        This implementation uses in-memory storage to demonstrate the pattern.
        """
        tenant_id = self._get_current_tenant_id()
        tenant_storage = self._get_tenant_storage(tenant_id)
        return tenant_storage.get("repo_configs")