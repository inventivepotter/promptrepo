"""
Tests for API dependencies in backend/api/deps.py
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from sqlmodel import Session

from api.deps import (
    get_current_user,
    get_optional_user,
    get_bearer_token,
    INDIVIDUAL_USER_ID,
    CurrentUserDep,
    OptionalUserDep
)
from middlewares.rest import AuthenticationException
from services.config.config_service import ConfigService
from services.config.models import HostingType
from services.auth.session_service import SessionService


class TestBearerTokenDependency:
    """Test cases for get_bearer_token dependency"""

    async def test_get_bearer_token_success(self):
        """Test successful extraction of Bearer token"""
        authorization = "Bearer test-token-123"
        result = await get_bearer_token(authorization)
        assert result == "test-token-123"

    async def test_get_bearer_token_missing_header(self):
        """Test error when authorization header is missing"""
        with pytest.raises(AuthenticationException) as exc_info:
            _ = await get_bearer_token(None)
        
        assert "Authorization header required" in str(exc_info.value)

    async def test_get_bearer_token_invalid_format(self):
        """Test error when authorization header format is invalid"""
        authorization = "Token test-token-123"
        with pytest.raises(AuthenticationException) as exc_info:
            _ = await get_bearer_token(authorization)
        
        assert "Invalid authorization header format" in str(exc_info.value)


class TestAuthenticationDependencies:
    """Test cases for authentication dependencies"""

    @pytest.fixture
    def mock_session_service(self):
        """Mock SessionService"""
        service = Mock(spec=SessionService)
        service.is_session_valid = Mock(return_value=True)
        service.get_session_by_id = Mock()
        return service

    @pytest.fixture
    def mock_config_service(self):
        """Mock ConfigService"""
        service = Mock(spec=ConfigService)
        service.get_hosting_config = Mock()
        return service

    @pytest.fixture
    def mock_user_session(self):
        """Mock user session"""
        session = Mock()
        session.user_id = "test-user-123"
        return session

    class TestGetCurrentUser:
        """Test cases for get_current_user dependency"""

        async def test_individual_hosting_type(self, mock_config_service):
            """Test that INDIVIDUAL hosting type returns INDIVIDUAL_USER_ID"""
            # Setup mock to return INDIVIDUAL hosting type
            mock_config = Mock()
            mock_config.type = HostingType.INDIVIDUAL
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_current_user(
                session_service=Mock(),
                config_service=mock_config_service,
                authorization=None
            )
            
            assert result == INDIVIDUAL_USER_ID

        async def test_missing_authorization_header(self, mock_config_service):
            """Test error when authorization header is missing for non-INDIVIDUAL hosting"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    session_service=Mock(),
                    config_service=mock_config_service,
                    authorization=None
                )
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Authorization header required" in exc_info.value.detail

        async def test_invalid_authorization_format(self, mock_config_service):
            """Test error when authorization format is invalid"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    session_service=Mock(),
                    config_service=mock_config_service,
                    authorization="Token test-token"
                )
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid authorization header format" in exc_info.value.detail

        async def test_empty_token(self, mock_config_service):
            """Test error when token is empty"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    session_service=Mock(),
                    config_service=mock_config_service,
                    authorization="Bearer "
                )
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Token cannot be empty" in exc_info.value.detail

        async def test_invalid_session(self, mock_config_service, mock_session_service):
            """Test error when session is invalid"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    session_service=mock_session_service,
                    config_service=mock_config_service,
                    authorization="Bearer test-token"
                )
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid or expired session token" in exc_info.value.detail

        async def test_session_not_found(self, mock_config_service, mock_session_service):
            """Test error when session is not found"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    session_service=mock_session_service,
                    config_service=mock_config_service,
                    authorization="Bearer test-token"
                )
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Session not found" in exc_info.value.detail

        async def test_successful_authentication(self, mock_config_service, mock_session_service, mock_user_session):
            """Test successful authentication returns user_id"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = mock_user_session
            
            result = await get_current_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                authorization="Bearer test-token"
            )
            
            assert result == "test-user-123"

        async def test_hosting_config_exception(self, mock_config_service, mock_session_service, mock_user_session):
            """Test that authentication continues when hosting config fails"""
            # Setup mocks to raise exception on get_hosting_config
            mock_config_service.get_hosting_config.side_effect = Exception("Config error")
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = mock_user_session
            
            result = await get_current_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                authorization="Bearer test-token"
            )
            
            assert result == "test-user-123"

    class TestGetOptionalUser:
        """Test cases for get_optional_user dependency"""

        async def test_individual_hosting_type(self, mock_config_service):
            """Test that INDIVIDUAL hosting type returns INDIVIDUAL_USER_ID"""
            # Setup mock to return INDIVIDUAL hosting type
            mock_config = Mock()
            mock_config.type = HostingType.INDIVIDUAL
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_optional_user(
                session_service=Mock(),
                config_service=mock_config_service,
                authorization=None
            )
            
            assert result == INDIVIDUAL_USER_ID

        async def test_missing_authorization_returns_none(self, mock_config_service):
            """Test that missing authorization returns None"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_optional_user(
                session_service=Mock(),
                config_service=mock_config_service,
                authorization=None
            )
            
            assert result is None

        async def test_invalid_authorization_format_returns_none(self, mock_config_service):
            """Test that invalid authorization format returns None"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_optional_user(
                session_service=Mock(),
                config_service=mock_config_service,
                authorization="Token test-token"
            )
            
            assert result is None

        async def test_empty_token_returns_none(self, mock_config_service):
            """Test that empty token returns None"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_optional_user(
                session_service=Mock(),
                config_service=mock_config_service,
                authorization="Bearer "
            )
            
            assert result is None

        async def test_invalid_session_returns_none(self, mock_config_service, mock_session_service):
            """Test that invalid session returns None"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = False
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                authorization="Bearer test-token"
            )
            
            assert result is None

        async def test_session_not_found_returns_none(self, mock_config_service, mock_session_service):
            """Test that session not found returns None"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = None
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                authorization="Bearer test-token"
            )
            
            assert result is None

        async def test_successful_authentication_returns_user_id(self, mock_config_service, mock_session_service, mock_user_session):
            """Test that successful authentication returns user_id"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = mock_user_session
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                authorization="Bearer test-token"
            )
            
            assert result == "test-user-123"

        async def test_hosting_config_exception_continues(self, mock_config_service, mock_session_service, mock_user_session):
            """Test that authentication continues when hosting config fails"""
            # Setup mocks to raise exception on get_hosting_config
            mock_config_service.get_hosting_config.side_effect = Exception("Config error")
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = mock_user_session
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                authorization="Bearer test-token"
            )
            
            assert result == "test-user-123"


class TestTypeAliases:
    """Test cases for type aliases"""

    def test_current_user_dep_alias(self):
        """Test that CurrentUserDep is properly typed"""
        # This is a compile-time check, so we just verify the alias exists
        assert CurrentUserDep is not None
        # The type should be Annotated[str, Depends(get_current_user)]

    def test_optional_user_dep_alias(self):
        """Test that OptionalUserDep is properly typed"""
        # This is a compile-time check, so we just verify the alias exists
        assert OptionalUserDep is not None
        # The type should be Annotated[Optional[str], Depends(get_optional_user)]