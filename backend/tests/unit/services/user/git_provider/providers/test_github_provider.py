"""
Tests for GitHub OAuth provider.
"""

import pytest
from urllib.parse import quote_plus
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from services.git_provider.providers.github_provider import GitHubOAuthProvider
from services.git_provider.models import (
    OAuthToken,
    UserInfo,
    UserEmail,
    OAuthProvider,
    TokenExchangeError,
    OAuthError,
)


class TestGitHubOAuthProvider:
    """Test cases for GitHubOAuthProvider class."""

    @pytest.fixture
    def github_provider(self):
        """Create a GitHub OAuth provider instance for testing."""
        return GitHubOAuthProvider(
            client_id="test_github_client_id",
            client_secret="test_github_client_secret"
        )

    def test_init(self):
        """Test GitHubOAuthProvider initialization."""
        provider = GitHubOAuthProvider(
            client_id="test_github_client_id",
            client_secret="test_github_client_secret"
        )
        
        assert provider.client_id == "test_github_client_id"
        assert provider.client_secret == "test_github_client_secret"
        assert hasattr(provider, 'http_client')
        
        # Check class constants
        assert GitHubOAuthProvider.AUTHORIZE_URL == "https://github.com/login/oauth/authorize"
        assert GitHubOAuthProvider.TOKEN_URL == "https://github.com/login/oauth/access_token"
        assert GitHubOAuthProvider.API_BASE_URL == "https://api.github.com"

    @pytest.mark.parametrize("client_id,client_secret", [
        ("", "test_github_client_secret"),
        ("test_github_client_id", ""),
        (None, "test_github_client_secret"),
        ("test_github_client_id", None)
    ])
    def test_init_invalid_credentials(self, client_id, client_secret):
        """Test GitHubOAuthProvider initialization with invalid credentials."""
        with pytest.raises(ValueError, match="GitHub client_id and client_secret are required"):
            GitHubOAuthProvider(client_id=client_id, client_secret=client_secret)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scopes,expected_scope", [
        (["user:email", "read:user"], "user%3Aemail+read%3Auser"),
        ([], "user%3Aemail+read%3Auser")  # Default scopes
    ])
    async def test_generate_auth_url(self, github_provider, redirect_uri, scopes, expected_scope, test_state):
        """Test generating authorization URL with different scope scenarios."""
        auth_url, state = await github_provider.generate_auth_url(
            scopes=scopes,
            redirect_uri=redirect_uri,
            state=test_state
        )
        
        assert isinstance(auth_url, str)
        assert isinstance(state, str)
        assert state == test_state
        
        # Verify URL components
        assert "github.com/login/oauth/authorize" in auth_url
        assert "client_id=test_github_client_id" in auth_url
        assert f"redirect_uri={quote_plus(redirect_uri)}" in auth_url
        assert f"scope={expected_scope}" in auth_url
        assert f"state={test_state}" in auth_url
        assert "allow_signup=true" in auth_url

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, github_provider, auth_code, redirect_uri, test_state, github_token_response):
        """Test successful token exchange."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = github_token_response
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            
            token = await github_provider.exchange_code_for_token(
                code=auth_code,
                redirect_uri=redirect_uri,
                state=test_state
            )
            
            assert isinstance(token, OAuthToken)
            assert token.access_token == "github_access_token_123"
            assert token.token_type == "bearer"
            assert token.scope == "user:email read:user"
            assert isinstance(token.created_at, datetime)
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://github.com/login/oauth/access_token"
            assert call_args[1]["data"]["client_id"] == "test_github_client_id"
            assert call_args[1]["data"]["client_secret"] == "test_github_client_secret"
            assert call_args[1]["data"]["code"] == auth_code
            assert call_args[1]["data"]["redirect_uri"] == redirect_uri
            assert call_args[1]["headers"]["Accept"] == "application/json"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,response_data,expected_error", [
        (400, {"error": "bad_request"}, "Failed to exchange authorization code for access token"),
        (200, {"error": "bad_verification_code", "error_description": "The code passed is incorrect or expired."}, 
         "GitHub OAuth error: The code passed is incorrect or expired.")
    ])
    async def test_exchange_code_for_token_errors(self, github_provider, auth_code, redirect_uri, test_state, 
                                                  status_code, response_data, expected_error):
        """Test token exchange with various error responses."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = response_data
            mock_response.status_code = status_code
            mock_client.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(TokenExchangeError, match=expected_error):
                await github_provider.exchange_code_for_token(
                    code=auth_code,
                    redirect_uri=redirect_uri,
                    state=test_state
                )

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, github_provider, sample_oauth_token, sample_user_info):
        """Test successful user info retrieval."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_user_info["github"]
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            user_info = await github_provider.get_user_info(
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
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.github.com/user"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_get_user_info_error(self, github_provider, sample_oauth_token):
        """Test user info retrieval with error response."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(OAuthError, match="Invalid or expired GitHub access token"):
                await github_provider.get_user_info(
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_get_user_emails_success(self, github_provider, sample_oauth_token, sample_user_emails):
        """Test successful user emails retrieval."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_user_emails["github"]
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            emails = await github_provider.get_user_emails(
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
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.github.com/user/emails"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_get_user_emails_error(self, github_provider, sample_oauth_token):
        """Test user emails retrieval with error response."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 403
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(OAuthError, match="Insufficient permissions to access user emails. Required scope: user:email"):
                await github_provider.get_user_emails(
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_refresh_token(self, github_provider, sample_oauth_token):
        """Test refreshing an access token."""
        # GitHub doesn't support token refresh, so this should return None
        new_token = await github_provider.refresh_token(
            refresh_token=sample_oauth_token.refresh_token
        )
        
        assert new_token is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_result", [
        (204, True),  # Success
        (404, False)  # Error
    ])
    async def test_revoke_token(self, github_provider, sample_oauth_token, status_code, expected_result):
        """Test token revocation with different responses."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_client.delete = AsyncMock(return_value=mock_response)
            
            result = await github_provider.revoke_token(
                access_token=sample_oauth_token.access_token
            )
            
            assert result is expected_result
            
            # Verify the request was made correctly
            mock_client.delete.assert_called_once()
            call_args = mock_client.delete.call_args
            assert call_args[0][0] == f"https://api.github.com/applications/{github_provider.client_id}/token"
            assert "Authorization" in call_args[1]["headers"]
            assert call_args[1]["params"]["access_token"] == sample_oauth_token.access_token

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_result", [
        (200, True),   # Valid token
        (401, False)   # Invalid token
    ])
    async def test_validate_token(self, github_provider, sample_oauth_token, status_code, expected_result):
        """Test token validation with different responses."""
        with patch.object(github_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_client.get = AsyncMock(return_value=mock_response)
            
            is_valid = await github_provider.validate_token(
                access_token=sample_oauth_token.access_token
            )
            
            assert is_valid is expected_result
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.github.com/user"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_context_manager(self, github_provider):
        """Test async context manager functionality."""
        with patch.object(github_provider.http_client, 'aclose', new_callable=AsyncMock) as mock_close:
            async with github_provider as provider:
                assert provider is github_provider
            
            # Verify aclose was called
            mock_close.assert_called_once()