"""
Unit tests for the AuthService
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, UTC
from sqlmodel import Session

from services.auth.auth_service import AuthService
from services.auth.models import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    VerifyRequest,
    AuthenticationFailedError,
    SessionNotFoundError,
    TokenValidationError
)
from services.oauth.models import AuthUrlResponse, OAuthToken, OAuthUserInfo, OAuthUserEmail
from services.config.models import OAuthConfig
from database.models.user import User
from schemas.oauth_provider_enum import OAuthProvider


@pytest.fixture
def mock_db():
    """Mock database session for testing"""
    return Mock(spec=Session)


@pytest.fixture
def mock_config_service():
    """Mock configuration service for testing"""
    mock = Mock()
    oauth_configs = [
        OAuthConfig(
            provider=OAuthProvider.GITHUB,
            client_id="test_github_client_id",
            client_secret="test_github_client_secret",
            redirect_url="https://example.com/oauth/callback"
        ),
        OAuthConfig(
            provider=OAuthProvider.GITLAB,
            client_id="test_gitlab_client_id",
            client_secret="test_gitlab_client_secret",
            redirect_url="https://example.com/oauth/callback"
        )
    ]
    mock.get_oauth_configs.return_value = oauth_configs
    return mock


@pytest.fixture
def mock_session_service():
    """Mock SessionService for testing"""
    mock = Mock()
    mock.create_session = Mock()
    mock.get_session_by_id = Mock()
    mock.is_session_valid = Mock()
    mock.delete_session = Mock()
    return mock


@pytest.fixture
def auth_service(mock_db, mock_config_service, mock_session_service):
    """AuthService instance with mocked dependencies"""
    service = AuthService(
        db=mock_db,
        config_service=mock_config_service,
        session_service=mock_session_service
    )
    return service


@pytest.fixture
def sample_user_info():
    """Sample user info from OAuth provider"""
    from schemas.oauth_provider_enum import OAuthProvider
    return OAuthUserInfo(
        id="12345",
        username="testuser",
        name="Test User",
        email="test@example.com",
        avatar_url="https://example.com/avatar.jpg",
        profile_url="https://github.com/testuser",
        provider=OAuthProvider.GITHUB
    )


@pytest.fixture
def sample_oauth_token():
    """Sample OAuth token response"""
    return OAuthToken(
        access_token="test_access_token",
        token_type="bearer",
        scope="user:email",
        expires_in=3600
    )


@pytest.fixture
def sample_user_emails():
    """Sample user emails from OAuth provider"""
    return [
        OAuthUserEmail(email="test@example.com", primary=True, verified=True),
        OAuthUserEmail(email="test2@example.com", primary=False, verified=True)
    ]


class TestAuthServiceLogin:
    """Tests for OAuth login initiation"""

    @pytest.mark.asyncio
    async def test_initiate_oauth_login_success(self, auth_service, mock_db):
        """Test successful OAuth login initiation"""
        # Arrange
        request = LoginRequest(provider=OAuthProvider.GITHUB, promptrepo_redirect_url=None)
        
        with patch.object(auth_service.oauth_service, 'get_available_providers', return_value=[OAuthProvider.GITHUB, OAuthProvider.GITLAB]), \
             patch.object(auth_service.oauth_service, 'cleanup_expired_states', return_value=2), \
             patch.object(auth_service.oauth_service, 'get_authorization_url', new_callable=AsyncMock) as mock_get_auth_url:
            
            mock_get_auth_url.return_value = AuthUrlResponse(
                auth_url="https://github.com/login/oauth/authorize?client_id=test",
                provider=OAuthProvider.GITHUB,
                state="test_state"
            )

            # Act
            result = await auth_service.initiate_oauth_login(request)

            # Assert
            assert result == "https://github.com/login/oauth/authorize?client_id=test"
            mock_get_auth_url.assert_called_once_with(
                provider=OAuthProvider.GITHUB,
                promptrepo_redirect_url=None
            )

    @pytest.mark.asyncio
    async def test_initiate_oauth_login_unsupported_provider(self, auth_service, mock_db):
        """Test OAuth login with unsupported provider"""
        # Arrange
        request = LoginRequest(provider=OAuthProvider.BITBUCKET, promptrepo_redirect_url=None)  # Use a provider that's not in the available list
        
        with patch.object(auth_service.oauth_service, 'get_available_providers', return_value=[OAuthProvider.GITHUB, OAuthProvider.GITLAB]):
            # Act & Assert
            with pytest.raises(AuthenticationFailedError) as exc_info:
                await auth_service.initiate_oauth_login(request)
            
            # The error message should indicate the provider is not supported
            assert "not supported" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_initiate_oauth_login_oauth_service_error(self, auth_service, mock_db):
        """Test OAuth login when OAuth service fails"""
        # Arrange
        request = LoginRequest(provider=OAuthProvider.GITHUB, promptrepo_redirect_url=None)
        
        with patch.object(auth_service.oauth_service, 'get_available_providers', return_value=[OAuthProvider.GITHUB]), \
             patch.object(auth_service.oauth_service, 'cleanup_expired_states', return_value=0), \
             patch.object(auth_service.oauth_service, 'get_authorization_url', new_callable=AsyncMock, side_effect=Exception("OAuth service error")):

            # Act & Assert
            with pytest.raises(AuthenticationFailedError) as exc_info:
                await auth_service.initiate_oauth_login(request)
            
            assert "Failed to generate authentication URL" in str(exc_info.value)


class TestAuthServiceCallback:
    """Tests for OAuth callback handling"""

    @pytest.mark.asyncio
    async def test_handle_oauth_callback_success(
        self,
        auth_service,
        mock_db,
        sample_oauth_token,
        sample_user_info,
        sample_user_emails
    ):
        """Test successful OAuth callback handling"""
        # Arrange
        mock_user = User(
            id="1",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_username="testuser",
            oauth_name="Test User",
            oauth_email="test@example.com",
            oauth_avatar_url="https://example.com/avatar.jpg",
            oauth_user_id="12345",
            oauth_profile_url="https://github.com/testuser"
        )
        
        mock_session = Mock()
        mock_session.session_id = "test_session_id"
        
        mock_state_metadata = Mock()
        mock_state_metadata.get.return_value = None

        with patch.object(auth_service.oauth_service.state_manager, 'get_state_metadata', return_value={}), \
             patch.object(auth_service.oauth_service, 'exchange_code_for_token', new_callable=AsyncMock, return_value=sample_oauth_token), \
             patch.object(auth_service.oauth_service, 'get_user_info', new_callable=AsyncMock, return_value=sample_user_info), \
             patch.object(auth_service.oauth_service, 'get_user_emails', new_callable=AsyncMock, return_value=sample_user_emails), \
             patch('services.auth.auth_service.UserDAO') as mock_user_dao_class, \
             patch.object(auth_service.session_service, 'create_session', return_value=mock_session):
            
            mock_user_dao = Mock()
            mock_user_dao.save_user.return_value = mock_user
            mock_user_dao_class.return_value = mock_user_dao

            # Act
            result = await auth_service.handle_oauth_callback(
                provider=OAuthProvider.GITHUB,
                code="test_code",
                state="test_state"
            )

            # Assert
            assert isinstance(result, LoginResponse)
            assert result.user.oauth_username == "testuser"
            assert result.session_token == "test_session_id"
            assert result.expires_at.endswith("Z")

    @pytest.mark.asyncio
    async def test_handle_oauth_callback_token_exchange_error(
        self,
        auth_service,
        mock_db
    ):
        """Test OAuth callback when token exchange fails"""
        # Arrange
        with patch.object(auth_service.oauth_service.state_manager, 'get_state_metadata', return_value={}), \
             patch.object(auth_service.oauth_service, 'exchange_code_for_token', new_callable=AsyncMock, side_effect=Exception("Token exchange failed")):

            # Act & Assert
            with pytest.raises(AuthenticationFailedError) as exc_info:
                await auth_service.handle_oauth_callback(
                    provider=OAuthProvider.GITHUB,
                    code="test_code",
                    state="test_state"
                )
            
            assert "Authentication failed" in str(exc_info.value)


class TestAuthServiceLogout:
    """Tests for logout functionality"""

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service, mock_db):
        """Test successful logout"""
        # Arrange
        request = LogoutRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.oauth_token = "test_oauth_token"
        mock_user = Mock()
        mock_user.oauth_username = "testuser"
        mock_user.oauth_provider = OAuthProvider.GITHUB
        mock_session.user = mock_user

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'delete_session', return_value=True), \
             patch.object(auth_service.oauth_service, 'revoke_token', new_callable=AsyncMock, return_value=True):

            # Act
            result = await auth_service.logout(request)

            # Assert
            assert result.status == "success"
            assert result.message == "Successfully logged out"

    @pytest.mark.asyncio
    async def test_logout_revoke_token_fails(self, auth_service, mock_db):
        """Test logout when token revocation fails"""
        # Arrange
        request = LogoutRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.oauth_token = "test_oauth_token"
        mock_user = Mock()
        mock_user.oauth_username = "testuser"
        mock_user.oauth_provider = OAuthProvider.GITHUB
        mock_session.user = mock_user

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'delete_session', return_value=True), \
             patch.object(auth_service.oauth_service, 'revoke_token', new_callable=AsyncMock, side_effect=Exception("Revoke failed")):

            # Act
            result = await auth_service.logout(request)

            # Assert - Should still succeed even if revoke fails
            assert result.status == "success"
            assert result.message == "Successfully logged out"


class TestAuthServiceRefresh:
    """Tests for session refresh functionality"""

    @pytest.mark.asyncio
    async def test_refresh_session_success(self, auth_service, mock_db):
        """Test successful session refresh"""
        # Arrange
        request = RefreshRequest(session_token="old_session_token")
        mock_session = Mock()
        mock_session.oauth_token = "test_oauth_token"
        mock_session.user_id = "test_user_id"
        mock_user = Mock()
        mock_user.oauth_username = "testuser"
        mock_user.oauth_provider = OAuthProvider.GITHUB
        mock_session.user = mock_user

        mock_new_session = Mock()
        mock_new_session.session_id = "new_session_token"

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'create_session', return_value=mock_new_session), \
             patch.object(auth_service.session_service, 'delete_session', return_value=True), \
             patch.object(auth_service.oauth_service, 'validate_token', new_callable=AsyncMock, return_value=True):

            # Act
            result = await auth_service.refresh_session(request)

            # Assert
            assert result.session_token == "new_session_token"
            assert result.expires_at.endswith("Z")

    @pytest.mark.asyncio
    async def test_refresh_session_not_found(self, auth_service, mock_db):
        """Test session refresh when session is not found"""
        # Arrange
        request = RefreshRequest(session_token="invalid_session_token")

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=None):

            # Act & Assert
            with pytest.raises(SessionNotFoundError) as exc_info:
                await auth_service.refresh_session(request)
            
            assert "Invalid session token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_session_invalid_oauth_token(self, auth_service, mock_db):
        """Test session refresh when OAuth token is invalid"""
        # Arrange
        request = RefreshRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.oauth_token = "invalid_oauth_token"
        mock_user = Mock()
        mock_user.oauth_username = "testuser"
        mock_user.oauth_provider = OAuthProvider.GITHUB
        mock_session.user = mock_user

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.oauth_service, 'validate_token', new_callable=AsyncMock, return_value=False):

            # Act & Assert
            with pytest.raises(TokenValidationError) as exc_info:
                await auth_service.refresh_session(request)
            
            assert "Invalid OAuth token" in str(exc_info.value)


class TestAuthServiceVerify:
    """Tests for session verification functionality"""

    @pytest.mark.asyncio
    async def test_verify_session_success(
        self,
        auth_service,
        mock_db
    ):
        """Test successful session verification"""
        # Arrange
        request = VerifyRequest(session_token="test_session_token")
        
        mock_user = User(
            id="1",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_username="testuser",
            oauth_name="Test User",
            oauth_email="test@example.com",
            oauth_avatar_url="https://example.com/avatar.jpg",
            oauth_user_id="12345",
            oauth_profile_url="https://github.com/testuser"
        )
        
        mock_session = Mock()
        mock_session.user = mock_user

        with patch.object(auth_service.session_service, 'is_session_valid', return_value=mock_session):

            # Act
            result = await auth_service.verify_session(request)

            # Assert
            assert result.is_valid is True
            assert result.user.oauth_username == "testuser"

    @pytest.mark.asyncio
    async def test_verify_session_invalid_session(self, auth_service, mock_db):
        """Test session verification when session is invalid"""
        # Arrange
        request = VerifyRequest(session_token="invalid_session_token")

        with patch.object(auth_service.session_service, 'is_session_valid', return_value=None):

            # Act & Assert
            with pytest.raises(SessionNotFoundError) as exc_info:
                await auth_service.verify_session(request)
            
            assert "Invalid or expired session token" in str(exc_info.value)


class TestAuthServiceUtility:
    """Tests for utility methods"""

    def test_get_available_providers(self, auth_service):
        """Test getting available providers"""
        # Arrange
        with patch.object(auth_service.oauth_service, 'get_available_providers', return_value=[OAuthProvider.GITHUB, OAuthProvider.GITLAB, OAuthProvider.BITBUCKET]):

            # Act
            result = auth_service.get_available_providers()

            # Assert
            assert result == [OAuthProvider.GITHUB, OAuthProvider.GITLAB, OAuthProvider.BITBUCKET]