"""
Services module for PromptRepo.
Provides factory functions for creating service instances.
"""
from typing import Optional
from .github_service import GitHubService
from settings.base_settings import settings


def create_github_service() -> GitHubService:
    """
    Factory function to create GitHubService instance from settings.

    Args:
        redirect_uri: Override redirect URI (defaults to frontend callback URL)

    Returns:
        Configured GitHubService instance

    Raises:
        ValueError: If GitHub credentials are not configured
    """
    if not settings.auth_settings.github_client_id or not settings.auth_settings.github_client_secret:
        raise ValueError(
            "GitHub OAuth credentials not configured. "
            "Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables."
        )

    # Default redirect URI to frontend callback
        # Adjust for production environment
    return GitHubService(
        client_id=settings.auth_settings.github_client_id,
        client_secret=settings.auth_settings.github_client_secret,
    )

# You can add more service factories here as needed
# def create_openai_service() -> OpenAIService:
#     ...

# def create_anthropic_service() -> AnthropicService:
#     ...