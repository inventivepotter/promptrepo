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
    OAuthUserInfo,
    OAuthUserEmail,
    AuthUrlResponse,
    OAuthState,
    ProviderNotFoundError,
    InvalidStateError,
    TokenExchangeError,
    OAuthError,
)
from schemas.oauth_provider_enum import OAuthProvider
from services.oauth.providers.github_provider import GitHubOAuthProvider
from services.oauth.providers.gitlab_provider import GitLabOAuthProvider
from services.oauth.providers.bitbucket_provider import BitbucketOAuthProvider


class TestOAuthService:
    """Test cases for GitProviderService class."""

    @pytest.fixture
    def git_provider_service(self, mock_db, mock_config_service):
        """Create an OAuth service instance for testing."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        # Register providers using OAuthProvider enum
        OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
        OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
        OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        
        # Create service with new constructor signature
        service = OAuthService(db=mock_db, config_service=mock_config_service)
        return service

    def test_init(self, mock_db, mock_config_service):
        """Test GitProviderService initialization."""
        # Clear any existing providers
        OAuthProviderFactory.clear_registry()
        
        service = OAuthService(db=mock_db, config_service=mock_config_service)
        
        assert service.config_service == mock_config_service
        assert service.state_manager is not None

    @pytest.mark.asyncio
    async def test_get_authorization_url_success(self, git_provider_service, scopes):
        """Test getting authorization URL for different providers."""
        # Test GitHub provider
        auth_url_response = await git_provider_service.get_authorization_url(
            provider=OAuthProvider.GITHUB,
            scopes=scopes
        )
        
        assert isinstance(auth_url_response, AuthUrlResponse)
        assert auth_url_response.provider == OAuthProvider.GITHUB
        assert "github.com/login/oauth/authorize" in auth_url_response.auth_url
        assert "client_id=test_github_client_id" in auth_url_response.auth_url
        assert "redirect_uri=https%3A%2F%2Fexample.com%2Foauth%2Fcallback" in auth_url_response.auth_url
        assert "scope=user%3Aemail+read%3Auser" in auth_url_response.auth_url
        assert auth_url_response.state is not None
        
        # Test GitLab provider
        auth_url_response = await git_provider_service.get_authorization_url(
            provider=OAuthProvider.GITLAB,
            scopes=["read_user", "read_api", "email"]
        )
        
        assert isinstance(auth_url_response, AuthUrlResponse)
        assert auth_url_response.provider == OAuthProvider.GITLAB
        assert "gitlab.com/oauth/authorize" in auth_url_response.auth_url
        
        # Test Bitbucket provider
        auth_url_response = await git_provider_service.get_authorization_url(
            provider=OAuthProvider.BITBUCKET,
            scopes=["account", "email"]
        )
        
        assert isinstance(auth_url_response, AuthUrlResponse)
        assert auth_url_response.provider == OAuthProvider.BITBUCKET
        assert "bitbucket.org/site/oauth2/authorize" in auth_url_response.auth_url

    @pytest.mark.asyncio
    @pytest.mark.parametrize("provider,expected_error,exception_type", [
        ("", "Provider name must be a non-empty string", ValueError),
        ("unknown", "No OAuth configurations found", Exception)
    ])
    async def test_get_authorization_url_validation(self, git_provider_service, provider, expected_error, exception_type):
        """Test getting authorization URL with invalid parameters and unknown providers."""
        with pytest.raises(exception_type, match=expected_error):
            await git_provider_service.get_authorization_url(
                provider=provider,
                scopes=["user:email", "read:user"]
            )

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, git_provider_service, auth_code, redirect_uri, test_state, github_token_response):
        """Test successful token exchange."""
        # Mock the state manager to return valid state
        from database.models import OAuthState as DBOAuthState
        from datetime import datetime, UTC, timedelta
        
        mock_state = DBOAuthState(
            state_token=test_state,
            provider=OAuthProvider.GITHUB,
            redirect_uri=redirect_uri,
            scopes="user:email,read:user",
            meta_data={},
            expires_at=datetime.now(UTC) + timedelta(minutes=10)
        )
        
        with patch.object(git_provider_service.state_manager, 'validate_state', return_value=True), \
             patch.object(git_provider_service.state_manager, 'get_state_data', return_value=mock_state), \
             patch.object(git_provider_service.state_manager, 'remove_state', return_value=True), \
             patch("httpx.AsyncClient") as mock_client:
            
            # Set up mock HTTP response
            mock_response = Mock()
            mock_response.json.return_value = github_token_response
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            token = await git_provider_service.exchange_code_for_token(
                provider=OAuthProvider.GITHUB,
                code=auth_code,
                state=test_state
            )
            
            assert isinstance(token, OAuthToken)
            assert token.access_token == "github_access_token_123"
            assert token.token_type == "bearer"
            assert token.scope == "user:email read:user"
            assert isinstance(token.created_at, datetime)

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_invalid_state(self, git_provider_service, auth_code):
        """Test exchanging authorization code for token with invalid state."""
        # Test with non-existent state
        with pytest.raises(Exception, match="Invalid or expired OAuth state"):
            await git_provider_service.exchange_code_for_token(
                provider=OAuthProvider.GITHUB,
                code=auth_code,
                state="invalid_state"
            )

    # Removed test_exchange_code_for_token_redirect_uri_mismatch as redirect_uri is no longer a parameter

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_error(self, git_provider_service, auth_code, redirect_uri, test_state, error_response):
        """Test exchanging authorization code for token with error response."""
        # Mock the state manager to return valid state
        from database.models import OAuthState as DBOAuthState
        from datetime import datetime, UTC, timedelta
        
        mock_state = DBOAuthState(
            state_token=test_state,
            provider=OAuthProvider.GITHUB,
            redirect_uri=redirect_uri,
            scopes="user:email,read:user",
            meta_data={},
            expires_at=datetime.now(UTC) + timedelta(minutes=10)
        )
        
        with patch.object(git_provider_service.state_manager, 'validate_state', return_value=True), \
             patch.object(git_provider_service.state_manager, 'get_state_data', return_value=mock_state), \
             patch("httpx.AsyncClient") as mock_client:
            
            # Set up mock error response
            mock_response = Mock()
            mock_response.json.return_value = error_response
            mock_response.is_error = True
            mock_response.status_code = 400
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider with error response
            with pytest.raises(TokenExchangeError, match="Failed to exchange authorization code for access token"):
                await git_provider_service.exchange_code_for_token(
                    provider=OAuthProvider.GITHUB,
                    code=auth_code,
                    state=test_state
                )


    @pytest.mark.asyncio
    async def test_get_user_info_success(self, git_provider_service, sample_oauth_token, sample_user_info):
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
            user_info = await git_provider_service.get_user_info(
                provider=OAuthProvider.GITHUB,
                access_token=sample_oauth_token.access_token
            )
            
            assert isinstance(user_info, OAuthUserInfo)
            assert user_info.id == "12345"
            assert user_info.username == "testuser"
            assert user_info.name == "Test User"
            assert user_info.email == "test@example.com"
            assert user_info.avatar_url == "https://github.com/images/testavatar"
            assert user_info.profile_url == "https://github.com/testuser"
            assert user_info.provider == OAuthProvider.GITHUB
            assert user_info.raw_data == sample_user_info["github"]

    @pytest.mark.asyncio
    async def test_get_user_info_error(self, git_provider_service, sample_oauth_token):
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
                await git_provider_service.get_user_info(
                    provider=OAuthProvider.GITHUB,
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_get_user_emails_success(self, git_provider_service, sample_oauth_token, sample_user_emails):
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
            emails = await git_provider_service.get_user_emails(
                provider=OAuthProvider.GITHUB,
                access_token=sample_oauth_token.access_token
            )
            
            assert isinstance(emails, list)
            assert len(emails) == 2
            assert isinstance(emails[0], OAuthUserEmail)
            assert emails[0].email == "primary@example.com"
            assert emails[0].primary is True
            assert emails[0].verified is True
            
            assert isinstance(emails[1], OAuthUserEmail)
            assert emails[1].email == "secondary@example.com"
            assert emails[1].primary is False
            assert emails[1].verified is True

    @pytest.mark.asyncio
    async def test_get_user_emails_error(self, git_provider_service, sample_oauth_token):
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
                await git_provider_service.get_user_emails(
                    provider=OAuthProvider.GITHUB,
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, git_provider_service, sample_oauth_token):
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
            new_token = await git_provider_service.refresh_token(
                provider=OAuthProvider.GITHUB,
                refresh_token=sample_oauth_token.refresh_token
            )
            
            # GitHub doesn't support refresh tokens, so should return None
            assert new_token is None

    @pytest.mark.asyncio
    async def test_revoke_token_success(self, git_provider_service, sample_oauth_token):
        """Test revoking an access token."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.is_error = False
            mock_response.status_code = 204
            mock_client.return_value.delete = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            result = await git_provider_service.revoke_token(
                provider=OAuthProvider.GITHUB,
                access_token=sample_oauth_token.access_token
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_validate_token_success(self, git_provider_service, sample_oauth_token):
        """Test validating an access token."""
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            # Set up mock response
            mock_response = Mock()
            mock_response.is_error = False
            mock_response.status_code = 200
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            
            # Test GitHub provider
            is_valid = await git_provider_service.validate_token(
                provider=OAuthProvider.GITHUB,
                access_token=sample_oauth_token.access_token
            )
            
            assert is_valid is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", [
        ("exchange_code_for_token", {"code": "test_code", "state": "test_state"}),
        ("get_user_info", {"access_token": "test_token"}),
        ("get_user_emails", {"access_token": "test_token"}),
        ("refresh_token", {"refresh_token": "test_refresh_token"}),
        ("revoke_token", {"access_token": "test_token"}),
        ("validate_token", {"access_token": "test_token"})
    ])
    async def test_unknown_provider_errors(self, git_provider_service, method_name, kwargs):
        """Test that all OAuth methods raise errors for unknown providers."""
        # Create a fake provider enum value for testing - we'll use GITHUB but expect it to fail
        # because we won't have it in the available providers
        test_provider = OAuthProvider.GITHUB
        
        # For exchange_code_for_token, we need to mock state validation
        if method_name == "exchange_code_for_token":
            from database.models import OAuthState as DBOAuthState
            from datetime import datetime, UTC, timedelta
            
            mock_state = DBOAuthState(
                state_token=kwargs["state"],
                provider=test_provider,
                redirect_uri="https://example.com/callback",
                scopes="",
                meta_data={},
                expires_at=datetime.now(UTC) + timedelta(minutes=10)
            )
            
            with patch.object(git_provider_service.state_manager, 'validate_state', return_value=True), \
                 patch.object(git_provider_service.state_manager, 'get_state_data', return_value=mock_state):
                
                # Clear providers to simulate unknown provider
                OAuthProviderFactory.clear_registry()
                method = getattr(git_provider_service, method_name)
                with pytest.raises(Exception):  # Will raise ProviderNotFoundError
                    await method(provider=test_provider, **kwargs)
                
                # Re-register providers for other tests
                OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
                OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
                OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)
        else:
            # Clear providers to simulate unknown provider
            OAuthProviderFactory.clear_registry()
            method = getattr(git_provider_service, method_name)
            with pytest.raises(Exception):  # Will raise ProviderNotFoundError or AppException
                await method(provider=test_provider, **kwargs)
            
            # Re-register providers for other tests
            OAuthProviderFactory.register_provider(OAuthProvider.GITHUB, GitHubOAuthProvider)
            OAuthProviderFactory.register_provider(OAuthProvider.GITLAB, GitLabOAuthProvider)
            OAuthProviderFactory.register_provider(OAuthProvider.BITBUCKET, BitbucketOAuthProvider)

    def test_get_available_providers(self, git_provider_service):
        """Test getting available providers."""
        providers = git_provider_service.get_available_providers()
        
        assert isinstance(providers, list)
        assert OAuthProvider.GITHUB in providers
        assert OAuthProvider.GITLAB in providers
        assert OAuthProvider.BITBUCKET in providers

    def test_cleanup_expired_states(self, git_provider_service):
        """Test cleaning up expired states."""
        # Mock the cleanup method on state_manager
        with patch.object(git_provider_service.state_manager, 'cleanup_expired_states', return_value=5):
            # Clean up expired states
            removed_count = git_provider_service.cleanup_expired_states()
            assert removed_count == 5

    def test_get_provider_config(self, git_provider_service):
        """Test getting provider configuration."""
        # Test GitHub provider
        config = git_provider_service.get_provider_config(OAuthProvider.GITHUB)
        
        assert config is not None
        assert config.provider == OAuthProvider.GITHUB
        assert config.client_id == "test_github_client_id"
        assert config.redirect_url == "https://example.com/oauth/callback"
        
        # Test unknown provider - should raise exception
        # We cannot pass a non-enum value, so skip this test or use a different approach