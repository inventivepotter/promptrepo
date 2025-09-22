"""
Pytest fixtures for authentication API route tests.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import Request
from sqlmodel import Session

from services.auth.auth_service import AuthService
from services.auth.models import (
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    VerifyResponse
)
from database.models.user import User


@pytest.fixture
def mock_request():
    """Mock FastAPI request object with request_id"""
    request = Mock(spec=Request)
    request.state = Mock()
    request.state.request_id = "test_request_id"
    return request


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def mock_auth_service():
    """Mock AuthService for testing controllers"""
    service = Mock(spec=AuthService)
    service.cleanup_expired_sessions = Mock(return_value=5)
    service.initiate_oauth_login = AsyncMock(return_value="https://github.com/login/oauth/authorize?client_id=test")
    service.handle_oauth_callback = AsyncMock()
    service.logout = AsyncMock()
    service.refresh_session = AsyncMock()
    service.verify_session = AsyncMock()
    return service


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return User(
        id="1",
        username="testuser",
        name="Test User",
        email="test@example.com",
        avatar_url="https://example.com/avatar.jpg",
        github_id=12345,
        html_url="https://github.com/testuser"
    )


@pytest.fixture
def sample_login_response(sample_user):
    """Sample LoginResponse for testing"""
    return LoginResponse(
        user=sample_user,
        session_token="test_session_token",
        expires_at="2024-01-01T12:00:00Z"
    )


@pytest.fixture
def sample_logout_response():
    """Sample LogoutResponse for testing"""
    return LogoutResponse(
        status="success",
        message="Successfully logged out"
    )


@pytest.fixture
def sample_refresh_response():
    """Sample RefreshResponse for testing"""
    return RefreshResponse(
        session_token="new_session_token",
        expires_at="2024-01-01T12:00:00Z"
    )


@pytest.fixture
def sample_verify_response(sample_user):
    """Sample VerifyResponse for testing"""
    return VerifyResponse(
        user=sample_user,
        is_valid=True
    )