"""
Configuration service for application configurations.
"""
from fastapi import HTTPException
from settings.base_settings import settings
from schemas.config import AppConfig, LlmConfig
from typing import List, Tuple, Optional
import json
from pathlib import Path

class ConfigService:
    """Unified service for accessing application configurations."""
    
    # LLM Configuration (existing functionality)
    @staticmethod
    def get_api_config_for_provider_model(provider: str, model: str) -> tuple[str, str | None]:
        """Get API key and base URL from settings for the given provider/model combination."""
        llm_configs = settings.llm_settings.llm_configs
        
        for config in llm_configs:
            if config.get("provider") == provider and config.get("model") == model:
                api_key = config.get("apiKey")
                if api_key:
                    api_base_url = config.get("apiBaseUrl")
                    return api_key, api_base_url
                break
        
        raise HTTPException(
            status_code=400,
            detail=f"No API key found for provider '{provider}' and model '{model}'. Please configure the API key in settings."
        )
    
    @staticmethod
    def get_all_llm_configs() -> List[LlmConfig]:
        """Get all configured LLM providers/models."""
        return settings.app_config.llmConfigs
    
    @staticmethod
    def get_configured_providers() -> List[str]:
        """Get list of all configured provider names."""
        providers = set()
        for config in settings.app_config.llmConfigs:
            providers.add(config.provider)
        return list(providers)
    
    # Hosting Configuration
    @staticmethod
    def get_hosting_type() -> str:
        """Get current hosting type."""
        return settings.app_config.hostingType
    
    @staticmethod
    def is_hosting_type(hosting_type: str) -> bool:
        """Check if current hosting matches specified type."""
        return settings.app_config.hostingType == hosting_type
    
    # GitHub OAuth Configuration
    @staticmethod
    def get_github_oauth_config() -> Tuple[str, str]:
        """Get GitHub OAuth client ID and secret."""
        config = settings.app_config
        return config.githubClientId, config.githubClientSecret
    
    @staticmethod
    def is_github_oauth_configured() -> bool:
        """Check if GitHub OAuth is properly configured."""
        client_id, client_secret = ConfigService.get_github_oauth_config()
        return bool(client_id and client_secret)
    
    # Admin Configuration
    @staticmethod
    def get_admin_emails() -> List[str]:
        """Get list of admin email addresses."""
        return settings.app_config.adminEmails
    
    @staticmethod
    def is_admin_email(email: str) -> bool:
        """Check if email is in admin list."""
        return email in ConfigService.get_admin_emails()
    
    # App Configuration Validation
    @staticmethod
    def validate_app_config(config: Optional[AppConfig] = None) -> bool:
        """Validate app configuration completeness for hosting type."""
        if config is None:
            config = settings.app_config
            
        hosting_type = config.hostingType
        
        if hosting_type == "individual":
            # Individual only needs LLM configs
            return bool(config.llmConfigs)
        elif hosting_type == "organization":
            # Organization needs GitHub OAuth and LLM configs
            return bool(config.githubClientId and config.githubClientSecret and config.llmConfigs)
        elif hosting_type == "multi-tenant":
            # Multi-tenant config is never considered "empty"
            return True
        
        return False
    
    @staticmethod
    def get_missing_config_items() -> List[str]:
        """Get list of missing required configuration items."""
        config = settings.app_config
        missing_items = []
        hosting_type = config.hostingType
        
        if hosting_type == "individual":
            if not config.llmConfigs:
                missing_items.append("llmConfigs")
        elif hosting_type == "organization":
            if not config.githubClientId:
                missing_items.append("githubClientId")
            if not config.githubClientSecret:
                missing_items.append("githubClientSecret")
            if not config.llmConfigs:
                missing_items.append("llmConfigs")
        # Multi-tenant doesn't have required configs
        
        return missing_items
    
    @staticmethod
    def is_config_complete() -> bool:
        """Check if current configuration is complete."""
        return ConfigService.validate_app_config()
    
    @staticmethod
    def get_current_config() -> AppConfig:
        """Get current config from settings"""
        return settings.app_config
    
    @staticmethod
    def update_env_vars_from_config(config: AppConfig) -> None:
        """Update .env file with configuration values for individual hosting types"""
        
        env_file_path = Path(".env")
        
        # Read existing .env file
        existing_env = {}
        if env_file_path.exists():
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_env[key.strip()] = value.strip()
        
        # Update environment variables based on config
        hosting_type = getattr(config, 'hostingType', '') or ''
        if hosting_type and hosting_type in ["individual", "organization", "multi-tenant"]:
            existing_env["HOSTING_TYPE"] = hosting_type
            
        # Handle auth settings based on hosting type
        if hosting_type in ["organization"]:
            github_client_id = getattr(config, 'githubClientId', '') or ''
            github_client_secret = getattr(config, 'githubClientSecret', '') or ''
            
            if github_client_id:
                existing_env["GITHUB_CLIENT_ID"] = github_client_id
            if github_client_secret:
                existing_env["GITHUB_CLIENT_SECRET"] = github_client_secret
        
        # Handle LLM configs - not for multi-tenant
        if hosting_type != "multi-tenant":
            llm_configs = getattr(config, 'llmConfigs', []) or []
            if llm_configs:
                llm_configs_data = []
                for llm_config in llm_configs:
                    config_dict = {
                        "provider": getattr(llm_config, 'provider', '') or '',
                        "model": getattr(llm_config, 'model', '') or '',
                        "apiKey": getattr(llm_config, 'apiKey', '') or '',
                        "apiBaseUrl": getattr(llm_config, 'apiBaseUrl', '') or ''
                    }
                    llm_configs_data.append(config_dict)
                
                llm_configs_json = json.dumps(llm_configs_data)
                existing_env["LLM_CONFIGS"] = llm_configs_json
            else:
                existing_env["LLM_CONFIGS"] = "[]"
        
        # Handle admin emails - not for individual hosting
        if hosting_type != "individual":
            admin_emails = getattr(config, 'adminEmails', []) or []
            admin_emails_json = json.dumps(admin_emails)
            existing_env["ADMIN_EMAILS"] = admin_emails_json
        else:
            existing_env["ADMIN_EMAILS"] = "[]"
        
        # Write updated .env file
        with open(env_file_path, 'w') as f:
            for key, value in existing_env.items():
                # Wrap hosting type in quotes
                if key == "HOSTING_TYPE":
                    f.write(f'{key}="{value}"\n')
                else:
                    f.write(f"{key}={value}\n")
        
        # Reload settings to reflect the changes from .env file
        settings.reload_settings()


# Create a singleton instance
config_service = ConfigService()