"""
Services module for PromptRepo.
Provides factory functions for creating service instances.
"""
from typing import Optional
import os
from .llm import ProviderService, ChatCompletionService
from .config import ConfigStrategyFactory, IConfig
from .repo_locator_service import RepoLocatorService
from .repo_service import RepoService
from .auth import AuthService, SessionService
from .user_service import UserService
from .oauth.oauth_service import OAuthService

def create_oauth_service() -> OAuthService:
    """
    Create an OAuth service instance using configuration from environment or config service.
    
    Returns:
        OAuthService: Configured OAuth service instance
        
    Raises:
        ValueError: If OAuth configuration is not available
    """
    # Get configuration strategy
    config = ConfigStrategyFactory.get_strategy()
    
    # Create OAuth service with auto-registration of providers
    return OAuthService(config_service=config, auto_register=True)