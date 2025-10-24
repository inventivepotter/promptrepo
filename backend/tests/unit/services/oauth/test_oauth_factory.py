"""
Tests for OAuth provider factory.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Optional

from services.oauth.oauth_factory import OAuthProviderFactory, auto_register_providers
from services.oauth.models import ProviderNotFoundError, ConfigurationError
from services.oauth.providers.github_provider import GitHubOAuthProvider
from services.oauth.providers.gitlab_provider import GitLabOAuthProvider
from services.oauth.providers.bitbucket_provider import BitbucketOAuthProvider
from services.config.config_interface import IConfig
from schemas.oauth_provider_enum import OAuthProvider


class TestOAuthProviderFactory:
    """Test cases for OAuthProviderFactory class."""

    def test_register_provider(self):
        """Test registering a provider."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        assert OAuthProvider.GITHUB in OAuthProviderFactory._providers
        assert OAuthProviderFactory._providers[OAuthProvider.GITHUB] == GitHubOAuthProvider
        
        # Register GitLab provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
        assert OAuthProvider.GITLAB in OAuthProviderFactory._providers
        assert OAuthProviderFactory._providers[OAuthProvider.GITLAB] == GitLabOAuthProvider
        
        # Register Bitbucket provider
        OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        assert OAuthProvider.BITBUCKET in OAuthProviderFactory._providers
        assert OAuthProviderFactory._providers[OAuthProvider.BITBUCKET] == BitbucketOAuthProvider
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_register_provider_validation(self):
        """Test provider registration validation."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Test with None provider name
        with pytest.raises(ValueError, match="Provider name must be a non-empty string"):
            OAuthProviderFactory.register_provider(None, GitHubOAuthProvider)  # type: ignore
        
        # Test with invalid provider class
        with pytest.raises(ValueError, match="Provider class must implement IOAuthProvider interface"):
            OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, "not_a_class")  # type: ignore
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_unregister_provider(self):
        """Test unregistering a provider."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        assert OAuthProvider.GITHUB in OAuthProviderFactory._providers
        
        # Unregister GitHub provider
        result = OAuthProviderFactory.unregister_provider(OAuthProvider.GITHUB)
        assert result is True
        assert OAuthProvider.GITHUB not in OAuthProviderFactory._providers
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider(self):
        """Test creating a provider instance."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register providers
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
        OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        
        # Create GitHub provider with explicit credentials
        github_provider = OAuthProviderFactory.create_provider(
            OAuthProvider.GITHUB,
            client_id="test_github_client_id",
            client_secret="test_github_client_secret"
        )
        assert isinstance(github_provider, GitHubOAuthProvider)
        assert github_provider.client_id == "test_github_client_id"
        assert github_provider.client_secret == "test_github_client_secret"
        
        # Create GitLab provider with explicit credentials
        gitlab_provider = OAuthProviderFactory.create_provider(
            OAuthProvider.GITLAB,
            client_id="test_gitlab_client_id",
            client_secret="test_gitlab_client_secret"
        )
        assert isinstance(gitlab_provider, GitLabOAuthProvider)
        assert gitlab_provider.client_id == "test_gitlab_client_id"
        assert gitlab_provider.client_secret == "test_gitlab_client_secret"
        
        # Create Bitbucket provider with explicit credentials
        bitbucket_provider = OAuthProviderFactory.create_provider(
            OAuthProvider.BITBUCKET,
            client_id="test_bitbucket_client_id",
            client_secret="test_bitbucket_client_secret"
        )
        assert isinstance(bitbucket_provider, BitbucketOAuthProvider)
        assert bitbucket_provider.client_id == "test_bitbucket_client_id"
        assert bitbucket_provider.client_secret == "test_bitbucket_client_secret"
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_with_credentials(self):
        """Test creating a provider with explicit credentials."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        
        # Create GitHub provider with explicit credentials
        github_provider = OAuthProviderFactory.create_provider(
            OAuthProvider.GITHUB,
            client_id="explicit_client_id",
            client_secret="explicit_client_secret"
        )
        assert isinstance(github_provider, GitHubOAuthProvider)
        assert github_provider.client_id == "explicit_client_id"
        assert github_provider.client_secret == "explicit_client_secret"
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_not_registered(self):
        """Test creating a provider that hasn't been registered."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Try to create a provider that hasn't been registered (use GITHUB but don't register it)
        with pytest.raises(ProviderNotFoundError):
            OAuthProviderFactory.create_provider(
                OAuthProvider.GITHUB,
                client_id="test",
                client_secret="test"
            )
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_no_config(self):
        """Test creating a provider with no configuration."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        
        # Try to create GitHub provider with missing credentials
        with pytest.raises(ConfigurationError):
            OAuthProviderFactory.create_provider(
                OAuthProvider.GITHUB,
                client_id="",
                client_secret=""
            )
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_invalid_config(self):
        """Test creating a provider with invalid configuration."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        
        # Try to create GitHub provider with invalid config (empty client_id)
        with pytest.raises(ConfigurationError):
            OAuthProviderFactory.create_provider(
                OAuthProvider.GITHUB,
                client_id="",
                client_secret="test_github_client_secret"
            )
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_is_provider_registered(self):
        """Test checking if a provider is registered."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Initially no providers registered
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITHUB) is False
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITLAB) is False
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.BITBUCKET) is False
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITHUB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITLAB) is False
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.BITBUCKET) is False
        
        # Register GitLab provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITHUB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITLAB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.BITBUCKET) is False
        
        # Register Bitbucket provider
        OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITHUB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITLAB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.BITBUCKET) is True
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_get_available_providers(self):
        """Test getting all available providers."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Initially no providers registered
        available_providers = OAuthProviderFactory.get_available_providers()
        assert available_providers == []
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        available_providers = OAuthProviderFactory.get_available_providers()
        assert available_providers == [OAuthProvider.GITHUB]
        
        # Register GitLab provider
        OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
        available_providers = OAuthProviderFactory.get_available_providers()
        assert set(available_providers) == {OAuthProvider.GITHUB, OAuthProvider.GITLAB}
        
        # Register Bitbucket provider
        OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        available_providers = OAuthProviderFactory.get_available_providers()
        assert set(available_providers) == {OAuthProvider.GITHUB, OAuthProvider.GITLAB, OAuthProvider.BITBUCKET}
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_clear_registry(self):
        """Test clearing the provider registry."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register providers
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
        OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        
        # Verify providers are registered
        assert len(OAuthProviderFactory._providers) == 3
        
        # Clear registry
        OAuthProviderFactory.clear_registry()
        assert OAuthProviderFactory._providers == {}


class TestAutoRegisterProviders:
    """Test cases for auto_register_providers function."""

    def test_auto_register_providers(self):
        """Test auto-registering providers."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Auto-register providers
        auto_register_providers()
        
        # Verify all providers were registered
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITHUB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.GITLAB) is True
        assert OAuthProviderFactory.is_provider_registered(OAuthProvider.BITBUCKET) is True
        
        # Verify the correct provider classes are registered
        assert OAuthProviderFactory._providers[OAuthProvider.GITHUB] == GitHubOAuthProvider
        assert OAuthProviderFactory._providers[OAuthProvider.GITLAB] == GitLabOAuthProvider
        assert OAuthProviderFactory._providers[OAuthProvider.BITBUCKET] == BitbucketOAuthProvider
        
        # Clean up
        OAuthProviderFactory.clear_registry()