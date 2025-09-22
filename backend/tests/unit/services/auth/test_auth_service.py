"""
Unit tests for the AuthService
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
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
from services.git_provider.models import AuthUrlResponse, OAuthToken, UserInfo, UserEmail
from database.models.user import User


@pytest.fixture
def mock_oauth_service():
    """Mock OAuth service for testing"""
    mock = Mock()
    # Configure async methods as AsyncMock
    mock.get_authorization_url = AsyncMock()
    mock.exchange_code_for_token = AsyncMock()
    mock.get_user_info = AsyncMock()
    mock.get_user_emails = AsyncMock()
    mock.refresh_token = AsyncMock()
    mock.revoke_token = AsyncMock()
    mock.validate_token = AsyncMock()
    return mock


@pytest.fixture
def mock_db():
    """Mock database session for testing"""
    return Mock(spec=Session)


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
def auth_service(mock_oauth_service, mock_db, mock_session_service):
    """AuthService instance with mocked dependencies"""
    return AuthService(
        db=mock_db,
        git_provider_service=mock_oauth_service,
        session_service=mock_session_service
    )


@pytest.fixture
def sample_user_info():
    """Sample user info from OAuth provider"""
    from services.git_provider.models import OAuthProvider
    return UserInfo(
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
        UserEmail(email="test@example.com", primary=True, verified=True),
        UserEmail(email="test2@example.com", primary=False, verified=True)
    ]


class TestAuthServiceLogin:
    """Tests for OAuth login initiation"""

    @pytest.mark.asyncio
    async def test_initiate_oauth_login_success(self, auth_service, mock_oauth_service, mock_db):
        """Test successful OAuth login initiation"""
        # Arrange
        request = LoginRequest(provider="github", redirect_uri="http://localhost:3000/callback")
        mock_oauth_service.get_available_providers.return_value = ["github", "gitlab"]
        mock_oauth_service.cleanup_expired_states.return_value = 2
        mock_oauth_service.get_authorization_url.return_value = AuthUrlResponse(
            auth_url="https://github.com/login/oauth/authorize?client_id=test",
            provider="github",
            state="test_state"
        )

        # Act
        result = await auth_service.initiate_oauth_login(request)

        # Assert
        assert result == "https://github.com/login/oauth/authorize?client_id=test"
        mock_oauth_service.cleanup_expired_states.assert_called_once()
        mock_oauth_service.get_authorization_url.assert_called_once_with(
            provider="github",
            redirect_uri="http://localhost:3000/callback"
        )

    @pytest.mark.asyncio
    async def test_initiate_oauth_login_unsupported_provider(self, auth_service, mock_oauth_service, mock_db):
        """Test OAuth login with unsupported provider"""
        # Arrange
        request = LoginRequest(provider="unsupported", redirect_uri="http://localhost:3000/callback")
        mock_oauth_service.get_available_providers.return_value = ["github", "gitlab"]

        # Act & Assert
        with pytest.raises(AuthenticationFailedError) as exc_info:
            await auth_service.initiate_oauth_login(request)
        
        assert "OAuth provider 'unsupported' is not supported" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initiate_oauth_login_oauth_service_error(self, auth_service, mock_oauth_service, mock_db):
        """Test OAuth login when OAuth service fails"""
        # Arrange
        request = LoginRequest(provider="github", redirect_uri="http://localhost:3000/callback")
        mock_oauth_service.get_available_providers.return_value = ["github"]
        mock_oauth_service.cleanup_expired_states.return_value = 0
        mock_oauth_service.get_authorization_url.side_effect = Exception("OAuth service error")

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
        mock_oauth_service, 
        mock_db,
        sample_oauth_token,
        sample_user_info,
        sample_user_emails
    ):
        """Test successful OAuth callback handling"""
        # Arrange
        mock_oauth_service.exchange_code_for_token.return_value = sample_oauth_token
        mock_oauth_service.get_user_info.return_value = sample_user_info
        mock_oauth_service.get_user_emails.return_value = sample_user_emails

        mock_user = User(
            id="1",
            oauth_provider="github",
            username="testuser",
            name="Test User",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg",
            oauth_user_id=12345,
            html_url="https://github.com/testuser"
        )
        
        mock_session = Mock()
        mock_session.session_id = "test_session_id"

        with patch('database.daos.user.UserDAO.save_user', return_value=mock_user), \
             patch.object(auth_service.session_service, 'create_session', return_value=mock_session):

            # Act
            result = await auth_service.handle_oauth_callback(
                provider="github",
                code="test_code",
                state="test_state",
                redirect_uri="http://localhost:3000/callback"
            )

            # Assert
            assert isinstance(result, LoginResponse)
            assert result.user.username == "testuser"
            assert result.session_token == "test_session_id"
            assert result.expires_at.endswith("Z")

    @pytest.mark.asyncio
    async def test_handle_oauth_callback_token_exchange_error(
        self, 
        auth_service, 
        mock_oauth_service, 
        mock_db
    ):
        """Test OAuth callback when token exchange fails"""
        # Arrange
        mock_oauth_service.exchange_code_for_token.side_effect = Exception("Token exchange failed")

        # Act & Assert
        with pytest.raises(AuthenticationFailedError) as exc_info:
            await auth_service.handle_oauth_callback(
                provider="github",
                code="test_code",
                state="test_state",
                redirect_uri="http://localhost:3000/callback"
            )
        
        assert "Authentication failed" in str(exc_info.value)


class TestAuthServiceLogout:
    """Tests for logout functionality"""

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service, mock_oauth_service, mock_db):
        """Test successful logout"""
        # Arrange
        request = LogoutRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.username = "testuser"
        mock_session.oauth_token = "test_oauth_token"
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.oauth_provider = "github"
        mock_session.user = mock_user

        mock_oauth_service.revoke_token.return_value = True

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'delete_session', return_value=True):

            # Act
            result = await auth_service.logout(request)

            # Assert
            assert result.status == "success"
            assert result.message == "Successfully logged out"
            mock_oauth_service.revoke_token.assert_called_once_with("github", "test_oauth_token")

    @pytest.mark.asyncio
    async def test_logout_revoke_token_fails(self, auth_service, mock_oauth_service, mock_db):
        """Test logout when token revocation fails"""
        # Arrange
        request = LogoutRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.username = "testuser"
        mock_session.oauth_token = "test_oauth_token"
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.oauth_provider = "github"
        mock_session.user = mock_user

        mock_oauth_service.revoke_token.side_effect = Exception("Revoke failed")

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'delete_session', return_value=True):

            # Act
            result = await auth_service.logout(request)

            # Assert - Should still succeed even if revoke fails
            assert result.status == "success"
            assert result.message == "Successfully logged out"


class TestAuthServiceRefresh:
    """Tests for session refresh functionality"""

    @pytest.mark.asyncio
    async def test_refresh_session_success(self, auth_service, mock_oauth_service, mock_db):
        """Test successful session refresh"""
        # Arrange
        request = RefreshRequest(session_token="old_session_token")
        mock_session = Mock()
        mock_session.username = "testuser"
        mock_session.oauth_token = "test_oauth_token"
        mock_session.user_id = "test_user_id"
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.oauth_provider = "github"
        mock_session.user = mock_user

        mock_new_session = Mock()
        mock_new_session.session_id = "new_session_token"

        mock_oauth_service.validate_token.return_value = True

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'create_session', return_value=mock_new_session), \
             patch.object(auth_service.session_service, 'delete_session', return_value=True):

            # Act
            result = await auth_service.refresh_session(request)

            # Assert
            assert result.session_token == "new_session_token"
            assert result.expires_at.endswith("Z")
            mock_oauth_service.validate_token.assert_called_once_with("github", "test_oauth_token")

    @pytest.mark.asyncio
    async def test_refresh_session_not_found(self, auth_service, mock_oauth_service, mock_db):
        """Test session refresh when session is not found"""
        # Arrange
        request = RefreshRequest(session_token="invalid_session_token")

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=None):

            # Act & Assert
            with pytest.raises(SessionNotFoundError) as exc_info:
                await auth_service.refresh_session(request)
            
            assert "Invalid session token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_session_invalid_oauth_token(self, auth_service, mock_oauth_service, mock_db):
        """Test session refresh when OAuth token is invalid"""
        # Arrange
        request = RefreshRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.username = "testuser"
        mock_session.oauth_token = "invalid_oauth_token"
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.oauth_provider = "github"
        mock_session.user = mock_user

        mock_oauth_service.validate_token.return_value = False

        with patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session):

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
        mock_oauth_service, 
        mock_db,
        sample_user_info,
        sample_user_emails
    ):
        """Test successful session verification"""
        # Arrange
        request = VerifyRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.username = "testuser"
        mock_session.oauth_token = "test_oauth_token"
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.oauth_provider = "github"
        mock_session.user = mock_user

        mock_user = User(
            id="1",
            oauth_provider="github",
            username="testuser",
            name="Test User",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg",
            oauth_user_id=12345,
            html_url="https://github.com/testuser"
        )

        mock_oauth_service.validate_token.return_value = True
        mock_oauth_service.get_user_info.return_value = sample_user_info
        mock_oauth_service.get_user_emails.return_value = sample_user_emails

        with patch.object(auth_service.session_service, 'is_session_valid', return_value=True), \
             patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch('database.daos.user.UserDAO.save_user', return_value=mock_user):

            # Act
            result = await auth_service.verify_session(request)

            # Assert
            assert result.is_valid is True
            assert result.user.username == "testuser"

    @pytest.mark.asyncio
    async def test_verify_session_invalid_session(self, auth_service, mock_oauth_service, mock_db):
        """Test session verification when session is invalid"""
        # Arrange
        request = VerifyRequest(session_token="invalid_session_token")

        with patch.object(auth_service.session_service, 'is_session_valid', return_value=False):

            # Act & Assert
            with pytest.raises(SessionNotFoundError) as exc_info:
                await auth_service.verify_session(request)
            
            assert "Invalid or expired session token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_session_oauth_validation_fails_with_db_user(self, auth_service, mock_oauth_service, mock_db):
        """Test session verification when OAuth validation fails but user exists in DB"""
        # Arrange
        request = VerifyRequest(session_token="test_session_token")
        mock_session = Mock()
        mock_session.username = "testuser"
        mock_session.oauth_token = "invalid_oauth_token"
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.oauth_provider = "github"
        mock_session.user = mock_user

        mock_user = User(
            id="1",
            oauth_provider="github",
            username="testuser",
            name="Test User",
            email="test@example.com"
        )

        mock_oauth_service.validate_token.return_value = False
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user

        with patch.object(auth_service.session_service, 'is_session_valid', return_value=True), \
             patch.object(auth_service.session_service, 'get_session_by_id', return_value=mock_session), \
             patch.object(auth_service.session_service, 'delete_session'):

            # Act & Assert
            with pytest.raises(TokenValidationError) as exc_info:
                await auth_service.verify_session(request)
            
            assert "OAuth token has been revoked" in str(exc_info.value)


class TestAuthServiceUtility:
    """Tests for utility methods"""

    def test_get_available_providers(self, auth_service, mock_oauth_service):
        """Test getting available providers"""
        # Arrange
        mock_oauth_service.get_available_providers.return_value = ["github", "gitlab", "bitbucket"]

        # Act
        result = auth_service.get_available_providers()

        # Assert
        assert result == ["github", "gitlab", "bitbucket"]
        mock_oauth_service.get_available_providers.assert_called_once()

    def test_cleanup_expired_sessions(self, auth_service, mock_oauth_service, mock_db):
        """Test cleanup of expired sessions"""
        # Arrange
        mock_oauth_service.cleanup_expired_states.return_value = 5

        # Act
        result = auth_service.cleanup_expired_sessions()

        # Assert
        assert result == 5
        mock_oauth_service.cleanup_expired_states.assert_called_once()

    def test_cleanup_expired_sessions_error(self, auth_service, mock_oauth_service, mock_db):
        """Test cleanup when an error occurs"""
        # Arrange
        mock_oauth_service.cleanup_expired_states.side_effect = Exception("Cleanup failed")

        # Act
        result = auth_service.cleanup_expired_sessions()

        # Assert
        assert result == 0