"""
OAuth Service Package

This package provides OAuth authentication functionality for multiple providers
including GitHub, GitLab, and Bitbucket.
"""

from .git_provider_service import GitProviderService
from .git_provider_interface import IOAuthProvider
from .git_provider_factory import OAuthProviderFactory
from .state_manager import StateManager
from .models import (
    OAuthToken,
    UserInfo,
    UserEmail,
    AuthUrlResponse,
    LoginResponse,
    OAuthState,
    OAuthProvider,
    OAuthError,
    ProviderNotFoundError,
    InvalidStateError,
    TokenExchangeError,
    ConfigurationError
)

# Import provider implementations
from .providers.github_provider import GitHubOAuthProvider
from .providers.gitlab_provider import GitLabOAuthProvider
from .providers.bitbucket_provider import BitbucketOAuthProvider

# Export main service class
__all__ = [
    "GitProviderService",
    "IOAuthProvider",
    "OAuthProviderFactory",
    "StateManager",
    "OAuthToken",
    "UserInfo",
    "UserEmail",
    "AuthUrlResponse",
    "LoginResponse",
    "OAuthState",
    "OAuthProvider",
    "OAuthError",
    "ProviderNotFoundError",
    "InvalidStateError",
    "TokenExchangeError",
    "ConfigurationError",
    "GitHubOAuthProvider",
    "GitLabOAuthProvider",
    "BitbucketOAuthProvider"
]