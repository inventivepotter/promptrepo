"""
Tests for GitHub OAuth endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database.core import get_session
from models.user import User
from services.oauth.models import (
    UserInfo,
    UserEmail,
    OAuthToken,
    AuthUrlResponse,
    OAuthProvider
)
from api.deps import get_oauth_service, get_auth_service
from services.oauth.oauth_service import OAuthService
from services.auth.auth_service import AuthService

# Create a test database engine
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a test database session
def get_test_session():
    with Session(engine) as session:
        yield session

# Override the database session dependency
app.dependency_overrides[get_session] = get_test_session

# Create test client
client = TestClient(app)

# Mock OAuth service
mock_oauth_service = Mock(spec=OAuthService)
mock_oauth_service.get_authorization_url = AsyncMock(return_value=AuthUrlResponse(
    provider="github",
    auth_url="https://github.com/login/oauth/authorize?client_id=test_client_id&redirect_uri=http://localhost:8080/api/v0/auth/callback/github&state=test_state",
    state="test_state"
))
mock_oauth_service.exchange_code_for_token = AsyncMock(return_value=OAuthToken(
    access_token="test_access_token",
    token_type="bearer",
    scope="user:email",
    expires_in=3600
))
mock_oauth_service.get_user_info = AsyncMock(return_value=UserInfo(
    provider=OAuthProvider.GITHUB,
    id="12345",
    username="testuser",
    name="Test User",
    email="test@example.com",
    avatar_url="https://avatars.githubusercontent.com/u/12345",
    profile_url="https://github.com/testuser"
))
mock_oauth_service.get_user_emails = AsyncMock(return_value=[
    UserEmail(
        email="test@example.com",
        primary=True,
        verified=True
    )
])
mock_oauth_service.cleanup_expired_states = Mock()
mock_oauth_service.get_available_providers = Mock(return_value=["github"])

# Create mock auth service and set up the callback response
from services.auth.models import LoginResponse

mock_user = User(
    id="1",
    username="testuser",
    name="Test User",
    email="test@example.com",
    avatar_url="https://avatars.githubusercontent.com/u/12345",
    github_id=12345,
    html_url="https://github.com/testuser"
)

mock_auth_service = Mock(spec=AuthService)
mock_auth_service.initiate_oauth_login = AsyncMock(return_value="https://github.com/login/oauth/authorize?client_id=test_client_id&redirect_uri=http://localhost:8080/api/v0/auth/callback/github&state=test_state")
mock_auth_service.handle_oauth_callback = AsyncMock(return_value=LoginResponse(
    user=mock_user,
    session_token="test_session_token",
    expires_at="2024-01-01T00:00:00Z"
))

# Override the dependencies
app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
app.dependency_overrides[get_auth_service] = lambda: mock_auth_service


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """
    Create test database tables before each test and drop them after.
    """
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def test_github_login_endpoint():
    """
    Test the GitHub login endpoint.
    """
    response = client.get(
        "/api/v0/auth/login/github/",
        params={"redirect_uri": "http://localhost:8080/api/v0/auth/callback/github"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "authUrl" in data["data"]
    assert "github.com/login/oauth/authorize" in data["data"]["authUrl"]
    assert "test_state" in data["data"]["authUrl"]
    
    # Verify the auth service was called correctly
    mock_auth_service.initiate_oauth_login.assert_called_once()


def test_github_login_endpoint_missing_redirect_uri():
    """
    Test the GitHub login endpoint with missing redirect_uri parameter.
    """
    response = client.get("/api/v0/auth/login/github/")
    
    assert response.status_code == 422  # Validation error


def test_github_callback_endpoint():
    """
    Test the GitHub callback endpoint.
    """
    response = client.get(
        "/api/v0/auth/callback/github/",
        params={
            "code": "test_code",
            "state": "test_state",
            "redirect_uri": "http://localhost:8080/api/v0/auth/callback/github"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "user" in data["data"]
    assert "sessionToken" in data["data"]
    assert "expiresAt" in data["data"]
    
    user_data = data["data"]["user"]
    assert user_data["username"] == "testuser"
    assert user_data["name"] == "Test User"
    assert user_data["email"] == "test@example.com"
    assert user_data["github_id"] == 12345
    
    # Verify the auth service was called correctly
    mock_auth_service.handle_oauth_callback.assert_called_once()


def test_github_callback_endpoint_missing_code():
    """
    Test the GitHub callback endpoint with missing code parameter.
    """
    response = client.get(
        "/api/v0/auth/callback/github/",
        params={
            "state": "test_state",
            "redirect_uri": "http://localhost:8080/api/v0/auth/callback/github"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_github_callback_endpoint_missing_state():
    """
    Test the GitHub callback endpoint with missing state parameter.
    """
    response = client.get(
        "/api/v0/auth/callback/github/",
        params={
            "code": "test_code",
            "redirect_uri": "http://localhost:8080/api/v0/auth/callback/github"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_github_callback_endpoint_missing_redirect_uri():
    """
    Test the GitHub callback endpoint with missing redirect_uri parameter.
    """
    response = client.get(
        "/api/v0/auth/callback/github/",
        params={
            "code": "test_code",
            "state": "test_state"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_github_callback_endpoint_token_exchange_error():
    """
    Test the GitHub callback endpoint when token exchange fails.
    """
    from services.auth.models import AuthenticationFailedError
    
    # Create a new mock auth service for this test
    error_mock_auth_service = Mock(spec=AuthService)
    error_mock_auth_service.handle_oauth_callback = AsyncMock(
        side_effect=AuthenticationFailedError("Failed to exchange code for token")
    )
    
    # Temporarily override the service
    original_override = app.dependency_overrides[get_auth_service]
    app.dependency_overrides[get_auth_service] = lambda: error_mock_auth_service
    
    try:
        response = client.get(
            "/api/v0/auth/callback/github/",
            params={
                "code": "test_code",
                "state": "test_state",
                "redirect_uri": "http://localhost:8080/api/v0/auth/callback/github"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"
        assert "Failed to exchange code for token" in data["detail"]
    finally:
        # Restore original override
        app.dependency_overrides[get_auth_service] = original_override


def test_github_callback_endpoint_user_info_error():
    """
    Test the GitHub callback endpoint when getting user info fails.
    """
    # Create a new mock auth service for this test
    error_mock_auth_service = Mock(spec=AuthService)
    error_mock_auth_service.handle_oauth_callback = AsyncMock(
        side_effect=Exception("Failed to get user info")
    )
    
    # Temporarily override the service
    original_override = app.dependency_overrides[get_auth_service]
    app.dependency_overrides[get_auth_service] = lambda: error_mock_auth_service
    
    try:
        response = client.get(
            "/api/v0/auth/callback/github/",
            params={
                "code": "test_code",
                "state": "test_state",
                "redirect_uri": "http://localhost:8080/api/v0/auth/callback/github"
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert "Authentication failed due to server error" in data["title"]
    finally:
        # Restore original override
        app.dependency_overrides[get_auth_service] = original_override