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
    # Try to get OAuth config from the config strategy
    config = ConfigStrategyFactory.get_strategy()
    oauth_config = config.get_oauth_config()
    
    if oauth_config and oauth_config.github_client_id and oauth_config.github_client_secret:
        return GitHubService(
            client_id=oauth_config.github_client_id,
            client_secret=oauth_config.github_client_secret
        )
    else:
        raise ValueError("GitHub OAuth configuration is not set.")