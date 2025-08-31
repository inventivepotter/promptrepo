"""
Shared utilities for config endpoints.
"""
import os
import json
from typing import Optional
from sqlmodel import Session
from schemas.config import AppConfig
from settings.base_settings import settings
from .auth import get_current_user
from services import create_github_service
from services.session_service import SessionService


async def get_user_email(session_token: str, db: Session) -> Optional[str]:
    """
    Get user's email from their session token by fetching from GitHub API
    
    Args:
        session_token: User's session token
        db: Database session
        
    Returns:
        User's email address or None if not found
    """
    try:
        # Get user session
        user_session = SessionService.get_session_by_id(db, session_token)
        if not user_session:
            return None
            
        # Get email from GitHub API using OAuth token
        github_service = create_github_service()
        async with github_service:
            return await github_service.get_primary_email(user_session.oauth_token)
            
    except Exception:
        return None


def update_env_vars_from_config(config: AppConfig) -> None:
    """Update environment variables and app settings from config object"""
    # Update basic config
    if config.hostingType:
        os.environ["HOSTING_TYPE"] = config.hostingType
        settings.hosting_type = config.hostingType
        
    if config.githubClientId:
        os.environ["GITHUB_CLIENT_ID"] = config.githubClientId
        settings.github_client_id = config.githubClientId
        
    if config.githubClientSecret:
        os.environ["GITHUB_CLIENT_SECRET"] = config.githubClientSecret
        settings.github_client_secret = config.githubClientSecret
    
    # Update LLM configs as JSON
    if config.llmConfigs:
        # Convert to the format expected by settings
        llm_configs_data = []
        for llm_config in config.llmConfigs:
            config_dict = {
                "provider": llm_config.provider,
                "model": llm_config.model,
                "apiKey": llm_config.apiKey,
                "apiBaseUrl": llm_config.apiBaseUrl if hasattr(llm_config, 'apiBaseUrl') else ""
            }
            llm_configs_data.append(config_dict)
        
        # Save as JSON string to LLM_CONFIGS env var
        llm_configs_json = json.dumps(llm_configs_data)
        os.environ["LLM_CONFIGS"] = llm_configs_json
        settings.llm_configs_json = llm_configs_json
    
    # Update admin emails
    if config.adminEmails is not None:
        # Convert to JSON string for env var
        admin_emails_json = json.dumps(config.adminEmails)
        os.environ["ADMIN_EMAILS"] = admin_emails_json
        settings.admin_emails = admin_emails_json


def get_current_config() -> AppConfig:
    """Get current config from settings"""
    return settings.app_config


def is_config_empty(config: AppConfig) -> bool:
    """
    Check if configuration is empty/not properly set
    """
    return (
        not config.githubClientId or
        not config.githubClientSecret or
        not config.llmConfigs
    )


def get_current_user_if_config_not_empty():
    """
    Conditional dependency that only requires authentication if config is not empty
    """
    config = get_current_config()
    if is_config_empty(config):
        return None
    else:
        return get_current_user()