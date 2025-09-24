"""
Shared fixtures and test data for OAuth service tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List, Union

from services.oauth.models import (
    OAuthToken,
    OAuthUserInfo,
    OAuthUserEmail,
    OAuthProvider,
    OAuthState,
    ProviderConfig,
)
from services.config.config_interface import IConfig


@pytest.fixture
def mock_config_service() -> Mock:
    """Mock configuration service."""
    mock_config = Mock(spec=IConfig)
    
    # Mock OAuth configurations
    oauth_configs = [
        ProviderConfig(
            provider="github",
            client_id="test_github_client_id",
            client_secret="test_github_client_secret",
            scopes=["user:email", "read:user"]
        ),
        ProviderConfig(
            provider="gitlab",
            client_id="test_gitlab_client_id",
            client_secret="test_gitlab_client_secret",
            scopes=["read_user", "read_api", "email"]
        ),
        ProviderConfig(
            provider="bitbucket",
            client_id="test_bitbucket_client_id",
            client_secret="test_bitbucket_client_secret",
            scopes=["account", "email"]
        )
    ]
    
    mock_config.get_oauth_configs.return_value = oauth_configs
    return mock_config


@pytest.fixture
def sample_oauth_token() -> OAuthToken:
    """Sample OAuth token for testing."""
    return OAuthToken(
        access_token="test_access_token_123",
        token_type="bearer",
        scope="user:email read:user",
        refresh_token="test_refresh_token_456",
        expires_in=3600,
        created_at=datetime.now(UTC)
    )


@pytest.fixture
def expired_oauth_token() -> OAuthToken:
    """Expired OAuth token for testing."""
    return OAuthToken(
        access_token="expired_access_token_789",
        token_type="bearer",
        scope="user:email read:user",
        refresh_token="expired_refresh_token_012",
        expires_in=3600,
        created_at=datetime.now(UTC) - timedelta(seconds=7200)  # 2 hours ago
    )


@pytest.fixture
def sample_user_info() -> Dict[str, Any]:
    """Sample user info data from providers."""
    return {
        "github": {
            "id": 12345,
            "login": "testuser",
            "name": "Test User",
            "email": "test@example.com",
            "avatar_url": "https://github.com/images/testavatar",
            "html_url": "https://github.com/testuser"
        },
        "gitlab": {
            "id": 12345,
            "username": "testuser",
            "name": "Test User",
            "email": "test@example.com",
            "avatar_url": "https://gitlab.com/uploads/-/system/user/avatar/12345/avatar.png",
            "web_url": "https://gitlab.com/testuser"
        },
        "bitbucket": {
            "uuid": "12345",
            "username": "testuser",
            "display_name": "Test User",
            "email": "test@example.com",
            "links": {
                "avatar": {
                    "href": "https://bitbucket.org/account/testuser/avatar/32/"
                },
                "html": {
                    "href": "https://bitbucket.org/testuser"
                }
            }
        }
    }


@pytest.fixture
def sample_user_emails() -> Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]:
    """Sample user email data from providers."""
    return {
        "github": [
            {
                "email": "primary@example.com",
                "primary": True,
                "verified": True,
                "visibility": "public"
            },
            {
                "email": "secondary@example.com",
                "primary": False,
                "verified": True,
                "visibility": "private"
            }
        ],
        "gitlab": [
            {
                "email": "primary@example.com",
                "primary": True,
                "confirmed_at": "2023-01-01T00:00:00Z"
            },
            {
                "email": "secondary@example.com",
                "primary": False,
                "confirmed_at": "2023-01-02T00:00:00Z"
            }
        ],
        "bitbucket": {
            "values": [
                {
                    "email": "primary@example.com",
                    "is_primary": True,
                    "is_confirmed": True
                },
                {
                    "email": "secondary@example.com",
                    "is_primary": False,
                    "is_confirmed": True
                }
            ]
        }
    }


@pytest.fixture
def sample_oauth_state() -> OAuthState:
    """Sample OAuth state for testing."""
    return OAuthState(
        state="test_state_12345",
        provider="github",
        redirect_uri="https://example.com/callback",
        scopes=["user:email", "read:user"],
        metadata={"user_id": "12345"}
    )


@pytest.fixture
def expired_oauth_state() -> OAuthState:
    """Expired OAuth state for testing."""
    return OAuthState(
        state="expired_state_67890",
        provider="github",
        redirect_uri="https://example.com/callback",
        scopes=["user:email", "read:user"],
        created_at=datetime.now(UTC) - timedelta(minutes=15)  # 15 minutes ago
    )


@pytest.fixture
def mock_httpx_client() -> Mock:
    """Mock httpx AsyncClient."""
    mock_client = Mock()
    mock_client.post = AsyncMock()
    mock_client.get = AsyncMock()
    mock_client.delete = AsyncMock()
    mock_client.aclose = AsyncMock()
    return mock_client


@pytest.fixture
def github_token_response() -> Dict[str, Any]:
    """GitHub token exchange response."""
    return {
        "access_token": "github_access_token_123",
        "token_type": "bearer",
        "scope": "user:email read:user"
    }


@pytest.fixture
def gitlab_token_response() -> Dict[str, Any]:
    """GitLab token exchange response."""
    return {
        "access_token": "gitlab_access_token_123",
        "token_type": "bearer",
        "refresh_token": "gitlab_refresh_token_456",
        "scope": "read_user read_api email",
        "expires_in": 7200,
        "created_at": int(datetime.utcnow().timestamp())
    }


@pytest.fixture
def bitbucket_token_response() -> Dict[str, Any]:
    """Bitbucket token exchange response."""
    return {
        "access_token": "bitbucket_access_token_123",
        "token_type": "bearer",
        "refresh_token": "bitbucket_refresh_token_456",
        "scope": "account email",
        "expires_in": 3600
    }


@pytest.fixture
def error_response() -> Dict[str, Any]:
    """OAuth error response."""
    return {
        "error": "invalid_grant",
        "error_description": "The authorization code is invalid or has expired."
    }


@pytest.fixture
def auth_code() -> str:
    """Sample authorization code."""
    return "test_auth_code_abc123"


@pytest.fixture
def redirect_uri() -> str:
    """Sample redirect URI."""
    return "https://example.com/oauth/callback"


@pytest.fixture
def test_state() -> str:
    """Sample state parameter."""
    return "test_state_xyz789"


@pytest.fixture
def scopes() -> List[str]:
    """Sample OAuth scopes."""
    return ["user:email", "read:user"]