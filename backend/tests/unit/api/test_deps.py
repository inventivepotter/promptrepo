"""
Tests for API dependencies in backend/api/deps.py
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status, Request
from sqlmodel import Session

from api.deps import (
    get_current_user,
    get_optional_user,
    get_bearer_token,
    get_session_cookie,
    INDIVIDUAL_USER_ID,
    CurrentUserDep,
    OptionalUserDep
)
from middlewares.rest import AuthenticationException
from services.config.config_service import ConfigService
from schemas.hosting_type_enum import HostingType
from services.auth.session_service import SessionService
from database.models.user_sessions import UserSessions


class TestBearerTokenDependency:
    """Test cases for get_bearer_token dependency"""

    @pytest.mark.asyncio
    async def test_get_bearer_token_success(self):
        """Test successful extraction of Bearer token"""
        authorization = "Bearer test-token-123"
        result = await get_bearer_token(authorization)
        assert result == "test-token-123"

    @pytest.mark.asyncio
    async def test_get_bearer_token_missing_header(self):
        """Test error when authorization header is missing"""
        with pytest.raises(AuthenticationException) as exc_info:
            _ = await get_bearer_token(None)
        
        assert "Unauthorized Access" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_bearer_token_invalid_format(self):
        """Test error when authorization header format is invalid"""
        authorization = "Token test-token-123"
        with pytest.raises(AuthenticationException) as exc_info:
            _ = await get_bearer_token(authorization)
        
        assert "Invalid authorization header format" in str(exc_info.value)


class TestSessionCookieDependency:
    """Test cases for get_session_cookie dependency"""

    @patch('api.deps.get_session_from_cookie')
    @pytest.mark.asyncio
    async def test_get_session_cookie_success(self, mock_get_session):
        """Test successful extraction of session from cookie"""
        mock_get_session.return_value = "test-session-123"
        mock_request = Mock(spec=Request)
        
        result = await get_session_cookie(mock_request)
        
        assert result == "test-session-123"
        mock_get_session.assert_called_once_with(mock_request)

    @patch('api.deps.get_session_from_cookie')
    @pytest.mark.asyncio
    async def test_get_session_cookie_missing(self, mock_get_session):
        """Test error when session cookie is missing"""
        mock_get_session.return_value = None
        mock_request = Mock(spec=Request)
        
        with pytest.raises(AuthenticationException) as exc_info:
            _ = await get_session_cookie(mock_request)
        
        assert "Unauthorized Access" in str(exc_info.value)


class TestAuthenticationDependencies:
    """Test cases for authentication dependencies"""

    @pytest.fixture
    def mock_session_service(self):
        """Mock SessionService"""
        service = Mock(spec=SessionService)
        return service

    @pytest.fixture
    def mock_config_service(self):
        """Mock ConfigService"""
        service = Mock(spec=ConfigService)
        service.get_hosting_config = Mock()
        return service

    @pytest.fixture
    def mock_user_session(self):
        """Mock UserSessions object"""
        session = Mock(spec=UserSessions)
        session.user_id = "test-user-123"
        session.session_id = "test-session-123"
        session.oauth_token = "test-oauth-token"
        return session

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI Request"""
        request = Mock(spec=Request)
        request.cookies = {}
        return request

    class TestGetCurrentUser:
        """Test cases for get_current_user dependency"""

        @pytest.mark.asyncio
        async def test_individual_hosting_type(self, mock_config_service, mock_session_service):
            """Test that INDIVIDUAL hosting type returns INDIVIDUAL_USER_ID"""
            # Setup mock to return INDIVIDUAL hosting type
            mock_config = Mock()
            mock_config.type = HostingType.INDIVIDUAL
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_current_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                session_id="any-session-id"
            )
            
            assert result == INDIVIDUAL_USER_ID

        @pytest.mark.asyncio
        async def test_invalid_session(self, mock_config_service, mock_session_service):
            """Test error when session is invalid"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = None
            
            with pytest.raises(AuthenticationException) as exc_info:
                await get_current_user(
                    session_service=mock_session_service,
                    config_service=mock_config_service,
                    session_id="test-session-id"
                )
            
            assert "Authentication Required" in str(exc_info.value)
            mock_session_service.is_session_valid.assert_called_once_with("test-session-id")

        @pytest.mark.asyncio
        async def test_successful_authentication(self, mock_config_service, mock_session_service, mock_user_session):
            """Test successful authentication returns user_id"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_session_service.is_session_valid.return_value = mock_user_session
            
            result = await get_current_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                session_id="test-session-id"
            )
            
            assert result == "test-user-123"
            mock_session_service.is_session_valid.assert_called_once_with("test-session-id")

        @pytest.mark.asyncio
        async def test_hosting_config_exception(self, mock_config_service, mock_session_service, mock_user_session):
            """Test that authentication continues when hosting config fails"""
            # Setup mocks to raise exception on get_hosting_config
            mock_config_service.get_hosting_config.side_effect = Exception("Config error")
            mock_session_service.is_session_valid.return_value = mock_user_session
            
            result = await get_current_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                session_id="test-session-id"
            )
            
            assert result == "test-user-123"

    class TestGetOptionalUser:
        """Test cases for get_optional_user dependency"""

        @pytest.mark.asyncio
        async def test_individual_hosting_type(self, mock_config_service, mock_session_service, mock_request):
            """Test that INDIVIDUAL hosting type returns INDIVIDUAL_USER_ID"""
            # Setup mock to return INDIVIDUAL hosting type
            mock_config = Mock()
            mock_config.type = HostingType.INDIVIDUAL
            mock_config_service.get_hosting_config.return_value = mock_config
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                request=mock_request
            )
            
            assert result == INDIVIDUAL_USER_ID

        @patch('api.deps.get_session_from_cookie')
        @pytest.mark.asyncio
        async def test_missing_session_cookie_returns_none(self, mock_get_session, mock_config_service, mock_session_service, mock_request):
            """Test that missing session cookie returns None"""
            # Setup mock to return ORGANIZATION hosting type
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_get_session.return_value = None
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                request=mock_request
            )
            
            assert result is None

        @patch('api.deps.get_session_from_cookie')
        @pytest.mark.asyncio
        async def test_invalid_session_returns_none(self, mock_get_session, mock_config_service, mock_session_service, mock_request):
            """Test that invalid session returns None"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_get_session.return_value = "test-session-id"
            mock_session_service.is_session_valid.return_value = None
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                request=mock_request
            )
            
            assert result is None

        @patch('api.deps.get_session_from_cookie')
        @pytest.mark.asyncio
        async def test_session_not_found_returns_none(self, mock_get_session, mock_config_service, mock_session_service, mock_request):
            """Test that session not found returns None"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_get_session.return_value = "test-session-id"
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = None
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                request=mock_request
            )
            
            assert result is None

        @patch('api.deps.get_session_from_cookie')
        @pytest.mark.asyncio
        async def test_successful_authentication_returns_user_id(self, mock_get_session, mock_config_service, mock_session_service, mock_user_session, mock_request):
            """Test that successful authentication returns user_id"""
            # Setup mocks
            mock_config = Mock()
            mock_config.type = HostingType.ORGANIZATION
            mock_config_service.get_hosting_config.return_value = mock_config
            mock_get_session.return_value = "test-session-id"
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = mock_user_session
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                request=mock_request
            )
            
            assert result == "test-user-123"

        @patch('api.deps.get_session_from_cookie')
        @pytest.mark.asyncio
        async def test_hosting_config_exception_continues(self, mock_get_session, mock_config_service, mock_session_service, mock_user_session, mock_request):
            """Test that authentication continues when hosting config fails"""
            # Setup mocks to raise exception on get_hosting_config
            mock_config_service.get_hosting_config.side_effect = Exception("Config error")
            mock_get_session.return_value = "test-session-id"
            mock_session_service.is_session_valid.return_value = True
            mock_session_service.get_session_by_id.return_value = mock_user_session
            
            result = await get_optional_user(
                session_service=mock_session_service,
                config_service=mock_config_service,
                request=mock_request
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