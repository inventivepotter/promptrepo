"""
Pytest fixtures for repos API route tests.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import Request
from sqlmodel import Session

from services.local_repo.local_repo_service import LocalRepoService


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
def mock_local_repo_service():
    """Mock LocalRepoService for testing controllers"""
    service = Mock(spec=LocalRepoService)
    service.get_latest_base_branch_content = AsyncMock()
    return service


@pytest.fixture
def mock_user_session():
    """Mock user session with OAuth token"""
    session = Mock()
    session.oauth_token = "test_oauth_token"  # noqa: S105
    return session


@pytest.fixture
def sample_get_latest_response():
    """Sample successful response from get_latest_base_branch_content"""
    return {
        "success": True,
        "message": "Successfully fetched latest content from test-repo"
    }