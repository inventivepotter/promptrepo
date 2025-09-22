"""
OAuth Provider Factory

This module implements a factory pattern with registry for creating
OAuth provider instances. It allows for dynamic registration and
instantiation of OAuth providers.
"""

from typing import Dict, Type, List, Optional
from .git_provider_interface import IOAuthProvider
from .models import ProviderNotFoundError, ConfigurationError
from services.config.config_interface import IConfig


class OAuthProviderFactory:
    """
    Factory for creating OAuth provider instances.
    
    Uses a registry pattern to allow dynamic registration of
    OAuth providers without modifying the factory code.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[IOAuthProvider]] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[IOAuthProvider]) -> None:
        """
        Register a new OAuth provider class.
        
        Args:
            name: Provider name (e.g., 'github', 'gitlab')
            provider_class: Provider class implementing IOAuthProvider
            
        Raises:
            ValueError: If provider name is empty or provider class is invalid
        """
        if not name or not isinstance(name, str):
            raise ValueError("Provider name must be a non-empty string")
        
        # Check if it's actually a class first
        try:
            if not issubclass(provider_class, IOAuthProvider):
                raise ValueError("Provider class must implement IOAuthProvider interface")
        except TypeError:
            raise ValueError("Provider class must implement IOAuthProvider interface")
        
        # Store in lowercase for case-insensitive matching
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def unregister_provider(cls, name: str) -> bool:
        """
        Unregister an OAuth provider.
        
        Args:
            name: Provider name to unregister
            
        Returns:
            True if provider was unregistered, False if not found
        """
        return cls._providers.pop(name.lower(), None) is not None
    
    @classmethod
    def create_provider(
        cls, 
        provider_name: str, 
        config_service: IConfig,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ) -> IOAuthProvider:
        """
        Create a provider instance using configuration service.
        
        Args:
            provider_name: Name of the provider to create
            config_service: Configuration service instance
            client_id: Optional client ID (overrides config)
            client_secret: Optional client secret (overrides config)
            
        Returns:
            Instance of the requested OAuth provider
            
        Raises:
            ProviderNotFoundError: If provider is not registered
            ConfigurationError: If provider configuration is missing or invalid
        """
        provider_name = provider_name.lower()
        
        # Check if provider is registered
        if provider_name not in cls._providers:
            raise ProviderNotFoundError(provider_name)
        
        # Get provider configuration
        if client_id and client_secret:
            # Use provided credentials
            provider_client_id = client_id
            provider_client_secret = client_secret
        else:
            # Get from config service
            oauth_configs = config_service.get_oauth_configs()
            if not oauth_configs:
                raise ConfigurationError("No OAuth configurations found")
            
            # Find matching provider config
            provider_config = None
            for config in oauth_configs:
                if config.provider.lower() == provider_name:
                    provider_config = config
                    break
            
            if not provider_config:
                raise ConfigurationError(f"No configuration found for provider: {provider_name}")
            
            provider_client_id = provider_config.client_id
            provider_client_secret = provider_config.client_secret
        
        # Validate credentials
        if not provider_client_id or not provider_client_secret:
            raise ConfigurationError(f"Missing credentials for provider: {provider_name}")
        
        # Create provider instance
        provider_class = cls._providers[provider_name]
        return provider_class(
            client_id=provider_client_id,
            client_secret=provider_client_secret
        )
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of all registered provider names.
        
        Returns:
            List of provider names in lowercase
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_registered(cls, provider_name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            provider_name: Provider name to check
            
        Returns:
            True if provider is registered, False otherwise
        """
        return provider_name.lower() in cls._providers
    
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
    OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
    OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
    OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)