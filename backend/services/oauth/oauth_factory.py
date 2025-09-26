"""
OAuth Provider Factory

This module implements a factory pattern with registry for creating
OAuth provider instances. It allows for dynamic registration and
instantiation of OAuth providers.
"""

from typing import Dict, Type, List, Optional

from schemas.oauth_provider_enum import OAuthProvider
from .oauth_interface import IOAuthProvider
from .models import ProviderNotFoundError, ConfigurationError
from services.config import ConfigService


class OAuthProviderFactory:
    """
    Factory for creating OAuth provider instances.
    
    Uses a registry pattern to allow dynamic registration of
    OAuth providers without modifying the factory code.
    """
    
    # Registry of available providers
    _providers: Dict[OAuthProvider, Type[IOAuthProvider]] = {}

    @classmethod
    def register_provider(cls, provider: OAuthProvider, provider_class: Type[IOAuthProvider]) -> None:
        """
        Register a new OAuth provider class.
        
        Args:
            provider: OAuth provider enum member (e.g., OAuthProvider.GITHUB)
            provider_class: Provider class implementing IOAuthProvider
            
        Raises:
            ValueError: If provider name is empty or provider class is invalid
        """
        if not provider or not isinstance(provider, OAuthProvider):
            raise ValueError("Provider name must be a non-empty string")
        
        # Check if it's actually a class first
        try:
            if not issubclass(provider_class, IOAuthProvider):
                raise ValueError("Provider class must implement IOAuthProvider interface")
        except TypeError:
            raise ValueError("Provider class must implement IOAuthProvider interface")
        
        # Store in lowercase for case-insensitive matching
        cls._providers[provider] = provider_class
    
    @classmethod
    def unregister_provider(cls, provider: OAuthProvider) -> bool:
        """
        Unregister an OAuth provider.
        
        Args:
            provider: OAuth provider enum member to unregister
            
        Returns:
            True if provider was unregistered, False if not found
        """
        return cls._providers.pop(provider, None) is not None
    
    @classmethod
    def create_provider(
        cls, 
        provider: OAuthProvider,
        client_id: str,
        client_secret: str
    ) -> IOAuthProvider:
        """
        Create a provider instance using configuration service.
        
        Args:
            provider: OAuth provider enum member to create
            client_id: Client ID (overrides config)
            client_secret: Client secret (overrides config)

        Returns:
            Instance of the requested OAuth provider
            Raises:
                ProviderNotFoundError: If provider is not registered
                ConfigurationError: If provider configuration is missing or invalid
            """
        # Check if provider is registered
        if provider not in cls._providers:
            raise ProviderNotFoundError(provider)
        
        # Validate credentials
        if not client_id or not client_secret:
            raise ConfigurationError(f"Missing credentials for provider: {provider}")
        
        # Create provider instance
        provider_class = cls._providers[provider]
        return provider_class(
            client_id=client_id,
            client_secret=client_secret
        )
    
    @classmethod
    def get_available_providers(cls) -> List[OAuthProvider]:
        """
        Get list of all registered provider names.
        
        Returns:
            List of provider names in lowercase
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_registered(cls, provider: OAuthProvider) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            provider: Provider to check
            
        Returns:
            True if provider is registered, False otherwise
        """
        return provider in cls._providers
    
    @classmethod
    def clear_registry(cls) -> None:
        """
        Clear all registered providers.
        
        Warning: This is primarily for testing purposes.
        """
        cls._providers.clear()


def auto_register_providers() -> None:
    """
    Auto-register known OAuth providers.
    
    This function should be called during application startup
    to ensure all available providers are registered.
    """
    # Import provider classes here to avoid circular imports
    from .providers.github_provider import GitHubOAuthProvider
    from .providers.gitlab_provider import GitLabOAuthProvider
    from .providers.bitbucket_provider import BitbucketOAuthProvider
    
    # Register providers
    OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
    OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
    OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)