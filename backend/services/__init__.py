"""
Services module for PromptRepo.
Provides factory functions for creating service instances.
"""
from typing import Optional
import os
from .github_service import GitHubService
from .provider_service import provider_service
from .config import ConfigStrategyFactory, IConfig
from .repo_locator_service import RepoLocatorService
from .repo_service import RepoService
from .session_service import SessionService
from .user_service import UserService


def create_github_service() -> GitHubService:
    """
    Create a GitHub service instance using configuration from environment or config service.
    
    Returns:
        GitHubService: Configured GitHub service instance
        
    Raises:
        ValueError: If GitHub OAuth credentials are not configured
    """
    # Try to get OAuth configs from the config strategy
    config = ConfigStrategyFactory.get_strategy()
    oauth_configs = config.get_oauth_configs()
    
    # Find GitHub OAuth config if available
    github_oauth_config = None
    if oauth_configs:
        for oauth_config in oauth_configs:
            if oauth_config.provider == "github":
                github_oauth_config = oauth_config
                break
    
    if github_oauth_config and github_oauth_config.client_id and github_oauth_config.client_secret:
        return GitHubService(
            client_id=github_oauth_config.client_id,
            client_secret=github_oauth_config.client_secret
        )
    else:
        raise ValueError("GitHub OAuth configuration is not set.")