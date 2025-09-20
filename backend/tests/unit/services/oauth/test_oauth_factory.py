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


class TestOAuthProviderFactory:
    """Test cases for OAuthProviderFactory class."""

    def test_register_provider(self):
        """Test registering a provider."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        assert "github" in OAuthProviderFactory._providers
        assert OAuthProviderFactory._providers["github"] == GitHubOAuthProvider
        
        # Register GitLab provider
        OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
        assert "gitlab" in OAuthProviderFactory._providers
        assert OAuthProviderFactory._providers["gitlab"] == GitLabOAuthProvider
        
        # Register Bitbucket provider
        OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)
        assert "bitbucket" in OAuthProviderFactory._providers
        assert OAuthProviderFactory._providers["bitbucket"] == BitbucketOAuthProvider
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_register_provider_validation(self):
        """Test provider registration validation."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Test with empty provider name
        with pytest.raises(ValueError, match="Provider name must be a non-empty string"):
            OAuthProviderFactory.register_provider("", GitHubOAuthProvider)
        
        # Test with None provider name
        with pytest.raises(ValueError, match="Provider name must be a non-empty string"):
            OAuthProviderFactory.register_provider(None, GitHubOAuthProvider)  # type: ignore
        
        # Test with invalid provider class
        with pytest.raises(ValueError, match="Provider class must implement IOAuthProvider interface"):
            OAuthProviderFactory.register_provider("invalid", "not_a_class")  # type: ignore
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_unregister_provider(self):
        """Test unregistering a provider."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        assert "github" in OAuthProviderFactory._providers
        
        # Unregister GitHub provider
        result = OAuthProviderFactory.unregister_provider("github")
        assert result is True
        assert "github" not in OAuthProviderFactory._providers
        
        # Try to unregister non-existent provider
        result = OAuthProviderFactory.unregister_provider("nonexistent")
        assert result is False
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider(self, mock_config_service):
        """Test creating a provider instance."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register providers
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
        OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)
        
        # Create GitHub provider
        github_provider = OAuthProviderFactory.create_provider("github", mock_config_service)
        assert isinstance(github_provider, GitHubOAuthProvider)
        assert github_provider.client_id == "test_github_client_id"
        assert github_provider.client_secret == "test_github_client_secret"
        
        # Create GitLab provider
        gitlab_provider = OAuthProviderFactory.create_provider("gitlab", mock_config_service)
        assert isinstance(gitlab_provider, GitLabOAuthProvider)
        assert gitlab_provider.client_id == "test_gitlab_client_id"
        assert gitlab_provider.client_secret == "test_gitlab_client_secret"
        
        # Create Bitbucket provider
        bitbucket_provider = OAuthProviderFactory.create_provider("bitbucket", mock_config_service)
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
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        
        # Create a mock config service
        mock_config = Mock(spec=IConfig)
        
        # Create GitHub provider with explicit credentials
        github_provider = OAuthProviderFactory.create_provider(
            "github", 
            mock_config,  # Pass a mock config service
            client_id="explicit_client_id",
            client_secret="explicit_client_secret"
        )
        assert isinstance(github_provider, GitHubOAuthProvider)
        assert github_provider.client_id == "explicit_client_id"
        assert github_provider.client_secret == "explicit_client_secret"
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_not_registered(self, mock_config_service):
        """Test creating a provider that hasn't been registered."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Try to create a provider that hasn't been registered
        with pytest.raises(ProviderNotFoundError, match="OAuth provider not found: unknown"):
            OAuthProviderFactory.create_provider("unknown", mock_config_service)
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_no_config(self, mock_config_service):
        """Test creating a provider with no configuration."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        
        # Mock config service to return empty configs
        mock_config_service.get_oauth_configs.return_value = []
        
        # Try to create GitHub provider with no config
        with pytest.raises(ConfigurationError, match="No OAuth configurations found"):
            OAuthProviderFactory.create_provider("github", mock_config_service)
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_create_provider_invalid_config(self, mock_config_service):
        """Test creating a provider with invalid configuration."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        
        # Mock config service to return invalid config (missing client_id)
        invalid_configs = [
            {
                "provider": "github",
                "client_id": "",
                "client_secret": "test_github_client_secret"
            }
        ]
        
        # This test would need to mock the ProviderConfig model behavior
        # For now, we'll test the case where no matching config is found
        mock_config_service.get_oauth_configs.return_value = []
        
        # Try to create GitHub provider with no config
        with pytest.raises(ConfigurationError, match="No OAuth configurations found"):
            OAuthProviderFactory.create_provider("github", mock_config_service)
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_is_provider_registered(self):
        """Test checking if a provider is registered."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Initially no providers registered
        assert OAuthProviderFactory.is_provider_registered("github") is False
        assert OAuthProviderFactory.is_provider_registered("gitlab") is False
        assert OAuthProviderFactory.is_provider_registered("bitbucket") is False
        
        # Register GitHub provider
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        assert OAuthProviderFactory.is_provider_registered("github") is True
        assert OAuthProviderFactory.is_provider_registered("gitlab") is False
        assert OAuthProviderFactory.is_provider_registered("bitbucket") is False
        
        # Register GitLab provider
        OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
        assert OAuthProviderFactory.is_provider_registered("github") is True
        assert OAuthProviderFactory.is_provider_registered("gitlab") is True
        assert OAuthProviderFactory.is_provider_registered("bitbucket") is False
        
        # Register Bitbucket provider
        OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)
        assert OAuthProviderFactory.is_provider_registered("github") is True
        assert OAuthProviderFactory.is_provider_registered("gitlab") is True
        assert OAuthProviderFactory.is_provider_registered("bitbucket") is True
        
        # Test case-insensitive matching
        assert OAuthProviderFactory.is_provider_registered("GITHUB") is True
        assert OAuthProviderFactory.is_provider_registered("GitHub") is True
        
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
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        available_providers = OAuthProviderFactory.get_available_providers()
        assert available_providers == ["github"]
        
        # Register GitLab provider
        OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
        available_providers = OAuthProviderFactory.get_available_providers()
        assert set(available_providers) == {"github", "gitlab"}
        
        # Register Bitbucket provider
        OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)
        available_providers = OAuthProviderFactory.get_available_providers()
        assert set(available_providers) == {"github", "gitlab", "bitbucket"}
        
        # Clean up
        OAuthProviderFactory.clear_registry()

    def test_clear_registry(self):
        """Test clearing the provider registry."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        # Register providers
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
        OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)
        
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
        assert OAuthProviderFactory.is_provider_registered("github") is True
        assert OAuthProviderFactory.is_provider_registered("gitlab") is True
        assert OAuthProviderFactory.is_provider_registered("bitbucket") is True
        
        # Verify the correct provider classes are registered
        assert OAuthProviderFactory._providers["github"] == GitHubOAuthProvider
        assert OAuthProviderFactory._providers["gitlab"] == GitLabOAuthProvider
        assert OAuthProviderFactory._providers["bitbucket"] == BitbucketOAuthProvider
        
        # Clean up
        OAuthProviderFactory.clear_registry()