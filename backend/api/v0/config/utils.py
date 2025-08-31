"""
Shared utilities for config endpoints.
"""
import json
from pathlib import Path
from schemas.config import AppConfig
from settings.base_settings import settings


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


def get_current_config() -> AppConfig:
    """Get current config from settings"""
    return settings.app_config


def is_config_empty(config: AppConfig) -> bool:
    """
    Check if configuration is empty/not properly set based on hosting type
    """
    hosting_type = getattr(config, 'hostingType', '') or ''
    
    if hosting_type == "individual":
        # Individual only needs LLM configs
        llm_configs = getattr(config, 'llmConfigs', []) or []
        return not llm_configs
    elif hosting_type == "organization":
        # Organization needs GitHub OAuth and LLM configs
        github_client_id = getattr(config, 'githubClientId', '') or ''
        github_client_secret = getattr(config, 'githubClientSecret', '') or ''
        llm_configs = getattr(config, 'llmConfigs', []) or []
        return not github_client_id or not github_client_secret or not llm_configs
    elif hosting_type == "multi-tenant":
        # Multi-tenant doesn't need LLM configs globally, might need admin emails
        return False  # Multi-tenant config is never considered "empty"
    else:
        # Default/unknown hosting type
        return True

