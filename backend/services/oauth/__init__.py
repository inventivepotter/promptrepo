"""
OAuth Service Package

This package provides OAuth authentication functionality for multiple providers
including GitHub, GitLab, and Bitbucket.
"""

from .oauth_service import OAuthService
from .oauth_interface import IOAuthProvider
from .oauth_factory import OAuthProviderFactory
from .state_manager import StateManager
from .models import (
    OAuthToken,
    OAuthUserInfo,
    OAuthUserEmail,
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
    "OAuthService",
    "IOAuthProvider",
    "OAuthProviderFactory",
    "StateManager",
    "OAuthToken",
    "OAuthUserInfo",
    "OAuthUserEmail",
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