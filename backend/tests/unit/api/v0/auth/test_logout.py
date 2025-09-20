"""
Unit tests for the logout endpoint.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import status

from api.v0.auth.logout import logout
from middlewares.rest import StandardResponse, AppException, AuthenticationException
from services.auth.models import SessionNotFoundError, AuthError


class TestLogout:
    """Tests for logout endpoint"""

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service,
        sample_logout_response
    ):
        """Test successful logout"""
        # Arrange
        token = "valid_session_token"
        mock_auth_service.logout.return_value = sample_logout_response
        
        # Act
        result = await logout(
            request=mock_request,
            token=token,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.message == "User logged out successfully"
        assert result.meta.request_id == "test_request_id"
        
        # Check response data
        assert result.data is not None
        assert result.data["status"] == "success"
        assert result.data["message"] == "Successfully logged out"
        
        # Verify service was called with correct parameters
        mock_auth_service.logout.assert_called_once()
        call_args = mock_auth_service.logout.call_args[0]
        logout_request = call_args[0]
        assert logout_request.session_token == token
        assert call_args[1] == mock_db_session

    @pytest.mark.asyncio
    async def test_logout_session_not_found(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test logout when session is not found"""
        # Arrange
        token = "invalid_session_token"
        mock_auth_service.logout.side_effect = SessionNotFoundError("Session not found")
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await logout(
                request=mock_request,
                token=token,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Session not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logout_auth_error(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test logout when auth error occurs"""
        # Arrange
        token = "session_token"
        mock_auth_service.logout.side_effect = AuthError("Auth service error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await logout(
                request=mock_request,
                token=token,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Auth service error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logout_unexpected_error(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test logout when unexpected error occurs"""
        # Arrange
        token = "session_token"
        mock_auth_service.logout.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await logout(
                request=mock_request,
                token=token,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Failed to logout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logout_empty_token(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service,
        sample_logout_response
    ):
        """Test logout with empty token string"""
        # Arrange
        token = ""
        mock_auth_service.logout.return_value = sample_logout_response
        
        # Act
        result = await logout(
            request=mock_request,
            token=token,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        # Verify service was still called - controller doesn't validate token format
        mock_auth_service.logout.assert_called_once()

    @pytest.mark.asyncio 
    async def test_logout_request_without_request_id(
        self,
        mock_db_session,
        mock_auth_service,
        sample_logout_response
    ):
        """Test logout with request that has no request_id"""
        # Arrange
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        token = "session_token"
        mock_auth_service.logout.return_value = sample_logout_response
        
        # Act
        result = await logout(
            request=request,
            token=token,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.meta.request_id is None