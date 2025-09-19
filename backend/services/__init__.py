"""
Services module for PromptRepo.
Provides factory functions for creating service instances.
"""
from typing import Optional
from .github_service import GitHubService
from .config import config_service
from .provider_service import provider_service


def create_github_service() -> GitHubService:
    """
    Factory function to create GitHubService instance from config service.

    Returns:
        Configured GitHubService instance

    Raises:
        ValueError: If GitHub credentials are not configured
    """
    if not config_service.is_github_oauth_configured():
        raise ValueError(
            "GitHub OAuth credentials not configured. "
            "Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables."
        )

    client_id, client_secret = config_service.get_github_oauth_config()
    return GitHubService(
        client_id=client_id,
        client_secret=client_secret,
    )