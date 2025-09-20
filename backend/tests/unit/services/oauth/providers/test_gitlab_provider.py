"""
Tests for GitLab OAuth provider.
"""

import pytest
from urllib.parse import quote_plus
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from services.oauth.providers.gitlab_provider import GitLabOAuthProvider
from services.oauth.models import (
    OAuthToken,
    UserInfo,
    UserEmail,
    OAuthProvider,
    TokenExchangeError,
    OAuthError,
)


class TestGitLabOAuthProvider:
    """Test cases for GitLabOAuthProvider class."""

    @pytest.fixture
    def gitlab_provider(self):
        """Create a GitLab OAuth provider instance for testing."""
        return GitLabOAuthProvider(
            client_id="test_gitlab_client_id",
            client_secret="test_gitlab_client_secret"
        )

    def test_init(self):
        """Test GitLabOAuthProvider initialization."""
        provider = GitLabOAuthProvider(
            client_id="test_gitlab_client_id",
            client_secret="test_gitlab_client_secret"
        )
        
        assert provider.client_id == "test_gitlab_client_id"
        assert provider.client_secret == "test_gitlab_client_secret"
        assert hasattr(provider, 'http_client')
        
        # Check class constants
        assert GitLabOAuthProvider.AUTHORIZE_URL == "https://gitlab.com/oauth/authorize"
        assert GitLabOAuthProvider.TOKEN_URL == "https://gitlab.com/oauth/token"
        assert GitLabOAuthProvider.API_BASE_URL == "https://gitlab.com/api/v4"

    @pytest.mark.parametrize("client_id,client_secret", [
        ("", "test_gitlab_client_secret"),
        ("test_gitlab_client_id", ""),
        (None, "test_gitlab_client_secret"),
        ("test_gitlab_client_id", None)
    ])
    def test_init_invalid_credentials(self, client_id, client_secret):
        """Test GitLabOAuthProvider initialization with invalid credentials."""
        with pytest.raises(ValueError, match="GitLab client_id and client_secret are required"):
            GitLabOAuthProvider(client_id=client_id, client_secret=client_secret)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scopes,expected_scope", [
        (["read_user", "read_api", "email"], "read_user+read_api+email"),
        ([], "read_user")  # Default scope
    ])
    async def test_generate_auth_url(self, gitlab_provider, redirect_uri, scopes, expected_scope, test_state):
        """Test generating authorization URL with different scope scenarios."""
        auth_url, state = await gitlab_provider.generate_auth_url(
            scopes=scopes,
            redirect_uri=redirect_uri,
            state=test_state
        )
        
        assert isinstance(auth_url, str)
        assert isinstance(state, str)
        assert state == test_state
        
        # Verify URL components
        assert "gitlab.com/oauth/authorize" in auth_url
        assert "client_id=test_gitlab_client_id" in auth_url
        assert f"redirect_uri={quote_plus(redirect_uri)}" in auth_url
        assert f"scope={expected_scope}" in auth_url
        assert f"state={test_state}" in auth_url
        assert "response_type=code" in auth_url

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, gitlab_provider, auth_code, redirect_uri, test_state, gitlab_token_response):
        """Test successful token exchange."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = gitlab_token_response
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            
            token = await gitlab_provider.exchange_code_for_token(
                code=auth_code,
                redirect_uri=redirect_uri,
                state=test_state
            )
            
            assert isinstance(token, OAuthToken)
            assert token.access_token == "gitlab_access_token_123"
            assert token.token_type == "bearer"
            assert token.scope == "read_user read_api email"
            assert isinstance(token.created_at, datetime)
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://gitlab.com/oauth/token"
            assert call_args[1]["data"]["client_id"] == "test_gitlab_client_id"
            assert call_args[1]["data"]["client_secret"] == "test_gitlab_client_secret"
            assert call_args[1]["data"]["code"] == auth_code
            assert call_args[1]["data"]["redirect_uri"] == redirect_uri
            assert call_args[1]["data"]["grant_type"] == "authorization_code"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,response_data,expected_error", [
        (400, {"error": "bad_request"}, "Failed to exchange authorization code for access token"),
        (400, {"error": "invalid_grant", "error_description": "The provided authorization grant is invalid, expired, revoked, does not match the redirection URI used in the authorization request, or was issued to another client."}, 
         "GitLab OAuth error: The provided authorization grant is invalid")
    ])
    async def test_exchange_code_for_token_errors(self, gitlab_provider, auth_code, redirect_uri, test_state, 
                                                  status_code, response_data, expected_error):
        """Test token exchange with various error responses."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = response_data
            mock_response.status_code = status_code
            mock_client.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(TokenExchangeError, match=expected_error):
                await gitlab_provider.exchange_code_for_token(
                    code=auth_code,
                    redirect_uri=redirect_uri,
                    state=test_state
                )

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, gitlab_provider, sample_oauth_token, sample_user_info):
        """Test successful user info retrieval."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_user_info["gitlab"]
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            user_info = await gitlab_provider.get_user_info(
                access_token=sample_oauth_token.access_token
            )
            
            assert isinstance(user_info, UserInfo)
            assert user_info.id == "12345"
            assert user_info.username == "testuser"
            assert user_info.name == "Test User"
            assert user_info.email == "test@example.com"
            assert user_info.avatar_url == "https://gitlab.com/uploads/-/system/user/avatar/12345/avatar.png"
            assert user_info.profile_url == "https://gitlab.com/testuser"
            assert user_info.provider == OAuthProvider.GITLAB
            assert user_info.raw_data == sample_user_info["gitlab"]
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://gitlab.com/api/v4/user"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_get_user_info_error(self, gitlab_provider, sample_oauth_token):
        """Test user info retrieval with error response."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(OAuthError, match="Invalid or expired GitLab access token"):
                await gitlab_provider.get_user_info(
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_get_user_emails_success(self, gitlab_provider, sample_oauth_token, sample_user_emails):
        """Test successful user emails retrieval."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_user_emails["gitlab"]
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            emails = await gitlab_provider.get_user_emails(
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
            assert call_args[0][0] == "https://gitlab.com/api/v4/user/emails"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_get_user_emails_error(self, gitlab_provider, sample_oauth_token):
        """Test user emails retrieval with error response."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(OAuthError, match="Invalid or expired GitLab access token"):
                await gitlab_provider.get_user_emails(
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, gitlab_provider, sample_oauth_token):
        """Test successful token refresh."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "new_gitlab_access_token_456",
                "token_type": "bearer",
                "scope": "read_user read_api email",
                "expires_in": 7200,
                "refresh_token": "new_gitlab_refresh_token_789"
            }
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            
            new_token = await gitlab_provider.refresh_token(
                refresh_token=sample_oauth_token.refresh_token
            )
            
            assert isinstance(new_token, OAuthToken)
            assert new_token.access_token == "new_gitlab_access_token_456"
            assert new_token.token_type == "bearer"
            assert new_token.scope == "read_user read_api email"
            assert new_token.refresh_token == "new_gitlab_refresh_token_789"
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://gitlab.com/oauth/token"
            assert call_args[1]["data"]["client_id"] == "test_gitlab_client_id"
            assert call_args[1]["data"]["client_secret"] == "test_gitlab_client_secret"
            assert call_args[1]["data"]["refresh_token"] == sample_oauth_token.refresh_token
            assert call_args[1]["data"]["grant_type"] == "refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_token_error(self, gitlab_provider, sample_oauth_token):
        """Test token refresh with error response."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "error": "invalid_grant",
                "error_description": "The refresh token is invalid or expired."
            }
            mock_response.status_code = 400
            mock_client.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(TokenExchangeError, match="GitLab OAuth error: The refresh token is invalid or expired"):
                await gitlab_provider.refresh_token(
                    refresh_token=sample_oauth_token.refresh_token
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_result", [
        (200, True),  # Success
        (400, False)  # Error
    ])
    async def test_revoke_token(self, gitlab_provider, sample_oauth_token, status_code, expected_result):
        """Test token revocation with different responses."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await gitlab_provider.revoke_token(
                access_token=sample_oauth_token.access_token
            )
            
            assert result is expected_result
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://gitlab.com/oauth/revoke"
            assert call_args[1]["data"]["client_id"] == "test_gitlab_client_id"
            assert call_args[1]["data"]["client_secret"] == "test_gitlab_client_secret"
            assert call_args[1]["data"]["token"] == sample_oauth_token.access_token

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_result", [
        (200, True),   # Valid token
        (401, False)   # Invalid token
    ])
    async def test_validate_token(self, gitlab_provider, sample_oauth_token, status_code, expected_result):
        """Test token validation with different responses."""
        with patch.object(gitlab_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_client.get = AsyncMock(return_value=mock_response)
            
            is_valid = await gitlab_provider.validate_token(
                access_token=sample_oauth_token.access_token
            )
            
            assert is_valid is expected_result
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://gitlab.com/api/v4/user"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_context_manager(self, gitlab_provider):
        """Test async context manager functionality."""
        with patch.object(gitlab_provider.http_client, 'aclose', new_callable=AsyncMock) as mock_close:
            async with gitlab_provider as provider:
                assert provider is gitlab_provider
            
            # Verify aclose was called
            mock_close.assert_called_once()