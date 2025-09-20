"""
Tests for OAuth service models.
"""

import pytest
from datetime import datetime, timedelta, UTC
from pydantic import ValidationError

from services.oauth.models import (
    OAuthToken,
    UserInfo,
    UserEmail,
    OAuthProvider,
    AuthUrlResponse,
    LoginResponse,
    OAuthError,
    ProviderNotFoundError,
    InvalidStateError,
    TokenExchangeError,
    ConfigurationError,
    OAuthState,
    ProviderConfig,
)


class TestOAuthToken:
    """Test cases for OAuthToken model."""

    def test_create_oauth_token(self):
        """Test creating a valid OAuth token."""
        token = OAuthToken(
            access_token="test_token_123",
            token_type="bearer",
            scope="user:email read:user",
            refresh_token="refresh_token_456",
            expires_in=3600,
            created_at=datetime.now(UTC)
        )
        
        assert token.access_token == "test_token_123"
        assert token.token_type == "bearer"
        assert token.scope == "user:email read:user"
        assert token.refresh_token == "refresh_token_456"
        assert token.expires_in == 3600
        assert isinstance(token.created_at, datetime)

    def test_oauth_token_defaults(self):
        """Test OAuth token with default values."""
        token = OAuthToken(access_token="test_token_123")
        
        assert token.access_token == "test_token_123"
        assert token.token_type == "bearer"
        assert token.scope is None
        assert token.refresh_token is None
        assert token.expires_in is None
        assert isinstance(token.created_at, datetime)

    def test_expires_at_property(self):
        """Test expires_at property calculation."""
        created_at = datetime.now(UTC)
        token = OAuthToken(
            access_token="test_token_123",
            expires_in=3600,
            created_at=created_at
        )
        
        expected_expires_at = created_at + timedelta(seconds=3600)
        assert token.expires_at is not None
        # Allow small difference due to test execution time
        assert abs((token.expires_at - expected_expires_at).total_seconds()) < 1

    def test_expires_at_property_without_expires_in(self):
        """Test expires_at property when expires_in is None."""
        token = OAuthToken(access_token="test_token_123")
        
        assert token.expires_at is None

    def test_is_expired_property(self):
        """Test is_expired property."""
        # Create an expired token
        created_at = datetime.now(UTC) - timedelta(seconds=7200)  # 2 hours ago
        expired_token = OAuthToken(
            access_token="expired_token",
            expires_in=3600,
            created_at=created_at
        )
        
        # Create a valid token
        valid_token = OAuthToken(
            access_token="valid_token",
            expires_in=3600,
            created_at=datetime.now(UTC)
        )
        
        # Create a token without expiration
        no_expiry_token = OAuthToken(access_token="no_expiry_token")
        
        assert expired_token.is_expired is True
        assert valid_token.is_expired is False
        assert no_expiry_token.is_expired is False


class TestUserInfo:
    """Test cases for UserInfo model."""

    def test_create_user_info(self):
        """Test creating a valid user info."""
        user_info = UserInfo(
            id="12345",
            username="testuser",
            name="Test User",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg",
            profile_url="https://example.com/profile",
            provider=OAuthProvider.GITHUB,
            raw_data={"id": 12345, "login": "testuser"}
        )
        
        assert user_info.id == "12345"
        assert user_info.username == "testuser"
        assert user_info.name == "Test User"
        assert user_info.email == "test@example.com"
        assert user_info.avatar_url == "https://example.com/avatar.jpg"
        assert user_info.profile_url == "https://example.com/profile"
        assert user_info.provider == OAuthProvider.GITHUB
        assert user_info.raw_data == {"id": 12345, "login": "testuser"}

    def test_user_info_defaults(self):
        """Test user info with default values."""
        user_info = UserInfo(
            id="12345",
            username="testuser",
            provider=OAuthProvider.GITHUB
        )
        
        assert user_info.id == "12345"
        assert user_info.username == "testuser"
        assert user_info.name is None
        assert user_info.email is None
        assert user_info.avatar_url is None
        assert user_info.profile_url is None
        assert user_info.provider == OAuthProvider.GITHUB
        assert user_info.raw_data is None


class TestUserEmail:
    """Test cases for UserEmail model."""

    def test_create_user_email(self):
        """Test creating a valid user email."""
        email = UserEmail(
            email="test@example.com",
            primary=True,
            verified=True,
            visibility="public"
        )
        
        assert email.email == "test@example.com"
        assert email.primary is True
        assert email.verified is True
        assert email.visibility == "public"

    def test_user_email_defaults(self):
        """Test user email with default values."""
        email = UserEmail(email="test@example.com")
        
        assert email.email == "test@example.com"
        assert email.primary is False
        assert email.verified is False
        assert email.visibility is None

    def test_email_validation(self):
        """Test email format validation."""
        # Valid email
        valid_email = UserEmail(email="test@example.com")
        assert valid_email.email == "test@example.com"
        
        # Invalid email (missing @)
        with pytest.raises(ValidationError):
            UserEmail(email="invalid-email")
        
        # Test email is converted to lowercase
        uppercase_email = UserEmail(email="TEST@EXAMPLE.COM")
        assert uppercase_email.email == "test@example.com"


class TestOAuthState:
    """Test cases for OAuthState model."""

    def test_create_oauth_state(self):
        """Test creating a valid OAuth state."""
        state = OAuthState(
            state="test_state_123",
            provider="github",
            redirect_uri="https://example.com/callback",
            scopes=["user:email", "read:user"],
            metadata={"user_id": "12345"}
        )
        
        assert state.state == "test_state_123"
        assert state.provider == "github"
        assert state.redirect_uri == "https://example.com/callback"
        assert state.scopes == ["user:email", "read:user"]
        assert state.metadata == {"user_id": "12345"}
        assert isinstance(state.created_at, datetime)

    def test_oauth_state_defaults(self):
        """Test OAuth state with default values."""
        state = OAuthState(
            state="test_state_123",
            provider="github",
            redirect_uri="https://example.com/callback"
        )
        
        assert state.state == "test_state_123"
        assert state.provider == "github"
        assert state.redirect_uri == "https://example.com/callback"
        assert state.scopes == []
        assert state.metadata is None
        assert isinstance(state.created_at, datetime)

    def test_is_expired_property(self):
        """Test is_expired property."""
        # Create an expired state (15 minutes ago)
        created_at = datetime.now(UTC) - timedelta(minutes=15)
        expired_state = OAuthState(
            state="expired_state",
            provider="github",
            redirect_uri="https://example.com/callback",
            created_at=created_at
        )
        
        # Create a valid state (5 minutes ago)
        valid_state = OAuthState(
            state="valid_state",
            provider="github",
            redirect_uri="https://example.com/callback",
            created_at=datetime.now(UTC) - timedelta(minutes=5)
        )
        
        assert expired_state.is_expired is True
        assert valid_state.is_expired is False


class TestProviderConfig:
    """Test cases for ProviderConfig model."""

    def test_create_provider_config(self):
        """Test creating a valid provider config."""
        config = ProviderConfig(
            provider="github",
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes=["user:email", "read:user"],
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user",
            emails_url="https://api.github.com/user/emails"
        )
        
        assert config.provider == "github"
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.scopes == ["user:email", "read:user"]
        assert config.auth_url == "https://github.com/login/oauth/authorize"
        assert config.token_url == "https://github.com/login/oauth/access_token"
        assert config.user_info_url == "https://api.github.com/user"
        assert config.emails_url == "https://api.github.com/user/emails"

    def test_provider_config_defaults(self):
        """Test provider config with default values."""
        config = ProviderConfig(
            provider="github",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        assert config.provider == "github"
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.scopes == []
        assert config.auth_url is None
        assert config.token_url is None
        assert config.user_info_url is None
        assert config.emails_url is None

    def test_credentials_validation(self):
        """Test credentials validation."""
        # Valid credentials
        valid_config = ProviderConfig(
            provider="github",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        assert valid_config.client_id == "test_client_id"
        assert valid_config.client_secret == "test_client_secret"
        
        # Empty client_id
        with pytest.raises(ValidationError):
            ProviderConfig(
                provider="github",
                client_id="",
                client_secret="test_client_secret"
            )
        
        # Empty client_secret
        with pytest.raises(ValidationError):
            ProviderConfig(
                provider="github",
                client_id="test_client_id",
                client_secret=""
            )
        
        # Whitespace-only client_id
        with pytest.raises(ValidationError):
            ProviderConfig(
                provider="github",
                client_id="   ",
                client_secret="test_client_secret"
            )


class TestAuthUrlResponse:
    """Test cases for AuthUrlResponse model."""

    def test_create_auth_url_response(self):
        """Test creating a valid auth URL response."""
        response = AuthUrlResponse(
            auth_url="https://github.com/login/oauth/authorize?client_id=test",
            provider="github",
            state="test_state_123"
        )
        
        assert response.auth_url == "https://github.com/login/oauth/authorize?client_id=test"
        assert response.provider == "github"
        assert response.state == "test_state_123"


class TestLoginResponse:
    """Test cases for LoginResponse model."""

    def test_create_login_response(self):
        """Test creating a valid login response."""
        user_info = UserInfo(
            id="12345",
            username="testuser",
            provider=OAuthProvider.GITHUB
        )
        
        response = LoginResponse(
            user=user_info,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            provider="github"
        )
        
        assert response.user == user_info
        assert response.access_token == "test_access_token"
        assert response.refresh_token == "test_refresh_token"
        assert isinstance(response.expires_at, datetime)
        assert response.provider == "github"

    def test_login_response_defaults(self):
        """Test login response with default values."""
        user_info = UserInfo(
            id="12345",
            username="testuser",
            provider=OAuthProvider.GITHUB
        )
        
        response = LoginResponse(
            user=user_info,
            access_token="test_access_token",
            provider="github"
        )
        
        assert response.user == user_info
        assert response.access_token == "test_access_token"
        assert response.refresh_token is None
        assert response.expires_at is None
        assert response.provider == "github"


class TestOAuthErrors:
    """Test cases for OAuth error classes."""

    def test_oauth_error(self):
        """Test base OAuth error."""
        error = OAuthError("Test error message", "github")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.provider == "github"

    def test_oauth_error_without_provider(self):
        """Test OAuth error without provider."""
        error = OAuthError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.provider is None

    def test_provider_not_found_error(self):
        """Test ProviderNotFoundError."""
        error = ProviderNotFoundError("unknown_provider")
        
        assert str(error) == "OAuth provider not found: unknown_provider"
        assert error.provider == "unknown_provider"

    def test_invalid_state_error(self):
        """Test InvalidStateError."""
        error = InvalidStateError("invalid_state", "github")
        
        assert str(error) == "Invalid or expired OAuth state: invalid_state"
        assert error.provider == "github"

    def test_token_exchange_error(self):
        """Test TokenExchangeError."""
        error = TokenExchangeError("Token exchange failed", "github", "invalid_code")
        
        assert str(error) == "Token exchange failed"
        assert error.message == "Token exchange failed"
        assert error.provider == "github"
        assert error.error_code == "invalid_code"

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid configuration", "github")
        
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"
        assert error.provider == "github"