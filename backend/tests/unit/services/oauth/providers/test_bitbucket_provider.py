"""
Tests for Bitbucket OAuth provider.
"""

import pytest
from urllib.parse import quote_plus
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from services.oauth.providers.bitbucket_provider import BitbucketOAuthProvider
from services.oauth.models import (
    OAuthToken,
    OAuthUserInfo,
    OAuthUserEmail,
    OAuthProvider,
    TokenExchangeError,
    OAuthError,
)


class TestBitbucketOAuthProvider:
    """Test cases for BitbucketOAuthProvider class."""

    @pytest.fixture
    def bitbucket_provider(self):
        """Create a Bitbucket OAuth provider instance for testing."""
        return BitbucketOAuthProvider(
            client_id="test_bitbucket_client_id",
            client_secret="test_bitbucket_client_secret"
        )

    def test_init(self):
        """Test BitbucketOAuthProvider initialization."""
        provider = BitbucketOAuthProvider(
            client_id="test_bitbucket_client_id",
            client_secret="test_bitbucket_client_secret"
        )
        
        assert provider.client_id == "test_bitbucket_client_id"
        assert provider.client_secret == "test_bitbucket_client_secret"
        assert hasattr(provider, 'http_client')
        
        # Check class constants
        assert BitbucketOAuthProvider.AUTHORIZE_URL == "https://bitbucket.org/site/oauth2/authorize"
        assert BitbucketOAuthProvider.TOKEN_URL == "https://bitbucket.org/site/oauth2/access_token"
        assert BitbucketOAuthProvider.API_BASE_URL == "https://api.bitbucket.org/2.0"

    @pytest.mark.parametrize("client_id,client_secret", [
        ("", "test_bitbucket_client_secret"),
        ("test_bitbucket_client_id", ""),
        (None, "test_bitbucket_client_secret"),
        ("test_bitbucket_client_id", None)
    ])
    def test_init_invalid_credentials(self, client_id, client_secret):
        """Test BitbucketOAuthProvider initialization with invalid credentials."""
        with pytest.raises(ValueError, match="Bitbucket client_id and client_secret are required"):
            BitbucketOAuthProvider(client_id=client_id, client_secret=client_secret)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scopes,expected_scope", [
        (["user:email", "read:user"], "user%3Aemail+read%3Auser"),
        ([], "account")  # Default scope
    ])
    async def test_generate_auth_url(self, bitbucket_provider, redirect_uri, scopes, expected_scope, test_state):
        """Test generating authorization URL with different scope scenarios."""
        auth_url, state = await bitbucket_provider.generate_auth_url(
            scopes=scopes,
            redirect_uri=redirect_uri,
            state=test_state
        )
        
        assert isinstance(auth_url, str)
        assert isinstance(state, str)
        assert state == test_state
        
        # Verify URL components
        assert "bitbucket.org/site/oauth2/authorize" in auth_url
        assert "client_id=test_bitbucket_client_id" in auth_url
        assert f"redirect_uri={quote_plus(redirect_uri)}" in auth_url
        assert f"scope={expected_scope}" in auth_url
        assert f"state={test_state}" in auth_url
        assert "response_type=code" in auth_url

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, bitbucket_provider, auth_code, redirect_uri, test_state, bitbucket_token_response):
        """Test successful token exchange."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = bitbucket_token_response
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            
            token = await bitbucket_provider.exchange_code_for_token(
                code=auth_code,
                redirect_uri=redirect_uri,
                state=test_state
            )
            
            assert isinstance(token, OAuthToken)
            assert token.access_token == "bitbucket_access_token_123"
            assert token.token_type == "bearer"
            assert token.scope == "account email"
            assert isinstance(token.created_at, datetime)
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://bitbucket.org/site/oauth2/access_token"
            assert call_args[1]["data"]["client_id"] == "test_bitbucket_client_id"
            assert call_args[1]["data"]["client_secret"] == "test_bitbucket_client_secret"
            assert call_args[1]["data"]["code"] == auth_code
            assert call_args[1]["data"]["redirect_uri"] == redirect_uri
            assert call_args[1]["data"]["grant_type"] == "authorization_code"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,response_data,expected_error", [
        (400, {"error": "bad_request"}, "Failed to exchange authorization code for access token"),
        (400, {"error": "invalid_grant", "error_description": "The authorization code is invalid or has expired."}, 
         "Bitbucket OAuth error: The authorization code is invalid or has expired")
    ])
    async def test_exchange_code_for_token_errors(self, bitbucket_provider, auth_code, redirect_uri, test_state, 
                                                  status_code, response_data, expected_error):
        """Test token exchange with various error responses."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = response_data
            mock_response.status_code = status_code
            mock_client.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(TokenExchangeError, match=expected_error):
                await bitbucket_provider.exchange_code_for_token(
                    code=auth_code,
                    redirect_uri=redirect_uri,
                    state=test_state
                )

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, bitbucket_provider, sample_oauth_token, sample_user_info):
        """Test successful user info retrieval."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_user_info["bitbucket"]
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            user_info = await bitbucket_provider.get_user_info(
                access_token=sample_oauth_token.access_token
            )
            
            assert isinstance(user_info, OAuthUserInfo)
            assert user_info.id == "12345"
            assert user_info.username == "testuser"
            assert user_info.name == "Test User"
            assert user_info.email == "test@example.com"
            assert user_info.avatar_url == "https://bitbucket.org/account/testuser/avatar/32/"
            assert user_info.profile_url == "https://bitbucket.org/testuser"
            assert user_info.provider == OAuthProvider.BITBUCKET
            assert user_info.raw_data == sample_user_info["bitbucket"]
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.bitbucket.org/2.0/user"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_get_user_info_error(self, bitbucket_provider, sample_oauth_token):
        """Test user info retrieval with error response."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(OAuthError, match="Invalid or expired Bitbucket access token"):
                await bitbucket_provider.get_user_info(
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_get_user_emails_success(self, bitbucket_provider, sample_oauth_token, sample_user_emails):
        """Test successful user emails retrieval."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_user_emails["bitbucket"]
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            emails = await bitbucket_provider.get_user_emails(
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
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.bitbucket.org/2.0/user/emails"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_get_user_emails_error(self, bitbucket_provider, sample_oauth_token):
        """Test user emails retrieval with error response."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(OAuthError, match="Invalid or expired Bitbucket access token"):
                await bitbucket_provider.get_user_emails(
                    access_token=sample_oauth_token.access_token
                )

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, bitbucket_provider, sample_oauth_token):
        """Test successful token refresh."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "new_bitbucket_access_token_456",
                "token_type": "bearer",
                "scope": "account email",
                "expires_in": 3600,
                "refresh_token": "new_bitbucket_refresh_token_789"
            }
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            
            new_token = await bitbucket_provider.refresh_token(
                refresh_token=sample_oauth_token.refresh_token
            )
            
            assert isinstance(new_token, OAuthToken)
            assert new_token.access_token == "new_bitbucket_access_token_456"
            assert new_token.token_type == "bearer"
            assert new_token.scope == "account email"
            assert new_token.refresh_token == "new_bitbucket_refresh_token_789"
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://bitbucket.org/site/oauth2/access_token"
            assert call_args[1]["data"]["client_id"] == "test_bitbucket_client_id"
            assert call_args[1]["data"]["client_secret"] == "test_bitbucket_client_secret"
            assert call_args[1]["data"]["refresh_token"] == sample_oauth_token.refresh_token
            assert call_args[1]["data"]["grant_type"] == "refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_token_error(self, bitbucket_provider, sample_oauth_token):
        """Test token refresh with error response."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "error": "invalid_grant",
                "error_description": "The refresh token is invalid or expired."
            }
            mock_response.status_code = 400
            mock_client.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(TokenExchangeError, match="Bitbucket OAuth error: The refresh token is invalid or expired"):
                await bitbucket_provider.refresh_token(
                    refresh_token=sample_oauth_token.refresh_token
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_result", [
        (204, True),  # Success
        (400, False)  # Error
    ])
    async def test_revoke_token(self, bitbucket_provider, sample_oauth_token, status_code, expected_result):
        """Test token revocation with different responses."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await bitbucket_provider.revoke_token(
                access_token=sample_oauth_token.access_token
            )
            
            assert result is expected_result
            
            # Verify the request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://bitbucket.org/site/oauth2/revoke"
            assert call_args[1]["data"]["token"] == sample_oauth_token.access_token
            assert "Authorization" in call_args[1]["headers"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code,expected_result", [
        (200, True),   # Valid token
        (401, False)   # Invalid token
    ])
    async def test_validate_token(self, bitbucket_provider, sample_oauth_token, status_code, expected_result):
        """Test token validation with different responses."""
        with patch.object(bitbucket_provider, 'http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_client.get = AsyncMock(return_value=mock_response)
            
            is_valid = await bitbucket_provider.validate_token(
                access_token=sample_oauth_token.access_token
            )
            
            assert is_valid is expected_result
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.bitbucket.org/2.0/user"
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {sample_oauth_token.access_token}"

    @pytest.mark.asyncio
    async def test_context_manager(self, bitbucket_provider):
        """Test async context manager functionality."""
        with patch.object(bitbucket_provider.http_client, 'aclose', new_callable=AsyncMock) as mock_close:
            async with bitbucket_provider as provider:
                assert provider is bitbucket_provider
            
            # Verify aclose was called
            mock_close.assert_called_once()