"""
Tests for OAuth service.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from services.oauth.oauth_service import OAuthService
from services.oauth.oauth_factory import OAuthProviderFactory
from services.oauth.models import (
    OAuthToken,
    UserInfo,
    UserEmail,
    OAuthProvider,
    AuthUrlResponse,
    OAuthState,
    ProviderNotFoundError,
    InvalidStateError,
    TokenExchangeError,
    OAuthError,
)
from services.oauth.providers.github_provider import GitHubOAuthProvider
from services.oauth.providers.gitlab_provider import GitLabOAuthProvider
from services.oauth.providers.bitbucket_provider import BitbucketOAuthProvider


class TestOAuthService:
    """Test cases for OAuthService class."""

    @pytest.fixture
    def oauth_service(self, mock_config_service):
        """Create an OAuth service instance for testing."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        # Register providers
        OAuthProviderFactory.register_provider("github", GitHubOAuthProvider)
        OAuthProviderFactory.register_provider("gitlab", GitLabOAuthProvider)
        OAuthProviderFactory.register_provider("bitbucket", BitbucketOAuthProvider)
        
        # Create service with auto_register=False to avoid re-registering
        service = OAuthService(mock_config_service, auto_register=False)
        return service

    def test_init(self, mock_config_service):
        """Test OAuthService initialization."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        service = OAuthService(mock_config_service, auto_register=False)
        
        assert service.config_service == mock_config_service
        assert service.state_manager is not None

    @pytest.mark.asyncio
    async def test_get_authorization_url_success(self, oauth_service, redirect_uri, scopes):
        """Test getting authorization URL for different providers."""
        # Test GitHub provider
        auth_url_response = await oauth_service.get_authorization_url(
            provider="github",
            redirect_uri=redirect_uri,
            scopes=scopes
        )
        
        assert isinstance(auth_url_response, AuthUrlResponse)
        assert auth_url_response.provider == "github"
        assert "github.com/login/oauth/authorize" in auth_url_response.auth_url
        assert "client_id=test_github_client_id" in auth_url_response.auth_url
        assert "redirect_uri=https%3A%2F%2Fexample.com%2Foauth%2Fcallback" in auth_url_response.auth_url
        assert "scope=user%3Aemail+read%3Auser" in auth_url_response.auth_url
        assert auth_url_response.state is not None
        
        # Test GitLab provider
        auth_url_response = await oauth_service.get_authorization_url(
            provider="gitlab",
            redirect_uri=redirect_uri,
            scopes=["read_user", "read_api", "email"]
        )
        
        assert isinstance(auth_url_response, AuthUrlResponse)
        assert auth_url_response.provider == "gitlab"
        assert "gitlab.com/oauth/authorize" in auth_url_response.auth_url
        
        # Test Bitbucket provider
        auth_url_response = await oauth_service.get_authorization_url(
            provider="bitbucket",
            redirect_uri=redirect_uri,
            scopes=["account", "email"]
        )
        
        assert isinstance(auth_url_response, AuthUrlResponse)
        assert auth_url_response.provider == "bitbucket"
        assert "bitbucket.org/site/oauth2/authorize" in auth_url_response.auth_url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("provider,redirect_uri,expected_error,exception_type", [
        ("", "https://example.com/callback", "Provider name must be a non-empty string", ValueError),
        ("github", "", "Redirect URI must be a non-empty string", ValueError),
        ("unknown", "https://example.com/callback", "OAuth provider not found: unknown", ProviderNotFoundError)
    ])
    async def test_get_authorization_url_validation(self, oauth_service, provider, redirect_uri, expected_error, exception_type):
        """Test getting authorization URL with invalid parameters and unknown providers."""
        with pytest.raises(exception_type, match=expected_error):
            await oauth_service.get_authorization_url(
                provider=provider,
                redirect_uri=redirect_uri,
                scopes=["user:email", "read:user"]
            )

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, oauth_service, auth_code, redirect_uri, test_state, github_token_response):
        """Test successful token exchange."""
        # Store state first
        oauth_service.state_manager.store_state(
            state=test_state,
            provider="github",
            redirect_uri=redirect_uri
        )
        
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.json.return_value = github_token_response
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            token = await oauth_service.exchange_code_for_token(
                provider="github",
                code=auth_code,
                redirect_uri=redirect_uri,
                state=test_state
            )
            
            assert isinstance(token, OAuthToken)
            assert token.access_token == "github_access_token_123"
            assert token.token_type == "bearer"
            assert token.scope == "user:email read:user"
            assert isinstance(token.created_at, datetime)

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_invalid_state(self, oauth_service, auth_code, redirect_uri):
        """Test exchanging authorization code for token with invalid state."""
        # Test with non-existent state
        with pytest.raises(InvalidStateError, match="Invalid or expired OAuth state"):
            await oauth_service.exchange_code_for_token(
                provider="github",
                code=auth_code,
                redirect_uri=redirect_uri,
                state="invalid_state"
            )

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_redirect_uri_mismatch(self, oauth_service, auth_code, test_state):
        """Test exchanging authorization code for token with redirect URI mismatch."""
        # Store state with different redirect URI
        oauth_service.state_manager.store_state(
            state=test_state,
            provider="github",
            redirect_uri="https://different.example.com/callback"
        )
        
        # Test with different redirect URI
        with pytest.raises(InvalidStateError, match="Redirect URI mismatch"):
            await oauth_service.exchange_code_for_token(
                provider="github",
                code=auth_code,
                redirect_uri="https://example.com/callback",
                state=test_state
            )

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_error(self, oauth_service, auth_code, redirect_uri, test_state, error_response):
        """Test exchanging authorization code for token with error response."""
        # Store state first
        oauth_service.state_manager.store_state(
            state=test_state,
            provider="github",
            redirect_uri=redirect_uri
        )
        
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock error response
            mock_response = Mock()
            mock_response.json.return_value = error_response
            mock_response.is_error = True
            mock_response.status_code = 400
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider with error response
            with pytest.raises(TokenExchangeError, match="Failed to exchange authorization code for access token"):
                await oauth_service.exchange_code_for_token(
                    provider="github",
                    code=auth_code,
                    redirect_uri=redirect_uri,
                    state=test_state
                )


    @pytest.mark.asyncio
    async def test_get_user_info_success(self, oauth_service, sample_oauth_token, sample_user_info):
        """Test getting user info."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.json.return_value = sample_user_info["github"]
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            user_info = await oauth_service.get_user_info(
                provider="github",
                access_token=sample_oauth_token.access_token
            )
            
            assert isinstance(user_info, UserInfo)
            assert user_info.id == "12345"
            assert user_info.username == "testuser"
            assert user_info.name == "Test User"
            assert user_info.email == "test@example.com"
            assert user_info.avatar_url == "https://github.com/images/testavatar"
            assert user_info.profile_url == "https://github.com/testuser"
            assert user_info.provider == OAuthProvider.GITHUB
            assert user_info.raw_data == sample_user_info["github"]

    @pytest.mark.asyncio
    async def test_get_user_info_error(self, oauth_service, sample_oauth_token):
        """Test getting user info with error response."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock error response
            mock_response = Mock()
            mock_response.is_error = True
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider with error response
            with pytest.raises(OAuthError, match="Failed to get user info"):
                await oauth_service.get_user_info(
                    provider="github",
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_get_user_emails_success(self, oauth_service, sample_oauth_token, sample_user_emails):
        """Test getting user emails."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.json.return_value = sample_user_emails["github"]
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            emails = await oauth_service.get_user_emails(
                provider="github",
                access_token=sample_oauth_token.access_token
            )
            
            assert isinstance(emails, list)
            assert len(emails) == 2
            assert isinstance(emails[0], UserEmail)
            assert emails[0].email == "primary@example.com"
            assert emails[0].primary is True
            assert emails[0].verified is True
            
            assert isinstance(emails[1], UserEmail)
            assert emails[1].email == "secondary@example.com"
            assert emails[1].primary is False
            assert emails[1].verified is True

    @pytest.mark.asyncio
    async def test_get_user_emails_error(self, oauth_service, sample_oauth_token):
        """Test getting user emails with error response."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock error response
            mock_response = Mock()
            mock_response.is_error = True
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider with error response
            with pytest.raises(OAuthError, match="Failed to get user emails"):
                await oauth_service.get_user_emails(
                    provider="github",
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, oauth_service, sample_oauth_token):
        """Test refreshing an access token."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "new_github_access_token_456",
                "token_type": "bearer",
                "scope": "user:email read:user",
                "expires_in": 3600
            }
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            new_token = await oauth_service.refresh_token(
                provider="github",
                refresh_token=sample_oauth_token.refresh_token
            )
            
            # GitHub doesn't support refresh tokens, so should return None
            assert new_token is None

    @pytest.mark.asyncio
    async def test_revoke_token_success(self, oauth_service, sample_oauth_token):
        """Test revoking an access token."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.is_error = False
            mock_response.status_code = 204
            mock_client.return_value.delete = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            result = await oauth_service.revoke_token(
                provider="github",
                access_token=sample_oauth_token.access_token
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_validate_token_success(self, oauth_service, sample_oauth_token):
        """Test validating an access token."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            is_valid = await oauth_service.validate_token(
                provider="github",
                access_token=sample_oauth_token.access_token
            )
            
            assert is_valid is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", [
        ("exchange_code_for_token", {"code": "test_code", "redirect_uri": "https://example.com/callback", "state": "test_state"}),
        ("get_user_info", {"access_token": "test_token"}),
        ("get_user_emails", {"access_token": "test_token"}),
        ("refresh_token", {"refresh_token": "test_refresh_token"}),
        ("revoke_token", {"access_token": "test_token"}),
        ("validate_token", {"access_token": "test_token"})
    ])
    async def test_unknown_provider_errors(self, oauth_service, method_name, kwargs):
        """Test that all OAuth methods raise ProviderNotFoundError for unknown providers."""
        # For exchange_code_for_token, we need to store a state first
        if method_name == "exchange_code_for_token":
            oauth_service.state_manager.store_state(
                state=kwargs["state"],
                provider="unknown",
                redirect_uri=kwargs["redirect_uri"]
            )
        
        method = getattr(oauth_service, method_name)
        with pytest.raises(ProviderNotFoundError, match="OAuth provider not found: unknown"):
            await method(provider="unknown", **kwargs)

    def test_get_available_providers(self, oauth_service):
        """Test getting available providers."""
        providers = oauth_service.get_available_providers()
        
        assert isinstance(providers, list)
        assert "github" in providers
        assert "gitlab" in providers
        assert "bitbucket" in providers

    def test_cleanup_expired_states(self, oauth_service, sample_oauth_state, expired_oauth_state):
        """Test cleaning up expired states."""
        # Store valid state
        oauth_service.state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Store expired state (manually set created_at)
        oauth_service.state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Verify both states exist
        assert len(oauth_service.state_manager._states) == 2
        
        # Clean up expired states
        removed_count = oauth_service.cleanup_expired_states()
        assert removed_count == 1
        assert sample_oauth_state.state in oauth_service.state_manager._states
        assert expired_oauth_state.state not in oauth_service.state_manager._states

    def test_get_provider_config(self, oauth_service):
        """Test getting provider configuration."""
        # Test GitHub provider
        config = oauth_service.get_provider_config("github")
        
        assert config is not None
        assert config["provider"] == "github"
        assert config["client_id"] == "test_github_client_id"
        assert "scopes" in config
        
        # Test unknown provider
        config = oauth_service.get_provider_config("unknown")
        assert config is None