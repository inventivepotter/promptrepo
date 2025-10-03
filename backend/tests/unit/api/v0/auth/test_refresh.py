"""
Unit tests for the refresh session endpoint.
"""
import pytest
from unittest.mock import Mock
from fastapi import Response

from api.v0.auth.refresh import refresh_session
from middlewares.rest import StandardResponse, AppException, AuthenticationException
from services.auth.models import SessionNotFoundError, TokenValidationError, AuthError


class TestRefreshSession:
    """Tests for refresh session endpoint"""

    @pytest.mark.asyncio
    async def test_refresh_session_success(
        self,
        mock_request,
        mock_auth_service,
        sample_refresh_response
    ):
        """Test successful session refresh"""
        # Arrange
        token = "valid_session_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.return_value = sample_refresh_response
        
        # Act
        result = await refresh_session(
            request=mock_request,
            response=mock_response,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.message == "Session refreshed successfully"
        assert result.meta.request_id == "test_request_id"
        
        # Check response data is None (standardized response)
        assert result.data is None
        
        # Verify service was called with correct parameters
        mock_auth_service.refresh_session.assert_called_once()
        call_args = mock_auth_service.refresh_session.call_args[0]
        refresh_request = call_args[0]
        assert refresh_request.session_token == token

    @pytest.mark.asyncio
    async def test_refresh_session_not_found(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test refresh when session is not found"""
        # Arrange
        token = "invalid_session_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.side_effect = SessionNotFoundError("Invalid session token")
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await refresh_session(
                request=mock_request,
                response=mock_response,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Authentication required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_session_token_validation_error(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test refresh when OAuth token validation fails"""
        # Arrange
        token = "session_with_invalid_oauth_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.side_effect = TokenValidationError("Invalid OAuth token")
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await refresh_session(
                request=mock_request,
                response=mock_response,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_session_auth_error(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test refresh when auth error occurs"""
        # Arrange
        token = "session_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.side_effect = AuthError("Auth service error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await refresh_session(
                request=mock_request,
                response=mock_response,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Auth service error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_session_unexpected_error(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test refresh when unexpected error occurs"""
        # Arrange
        token = "session_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await refresh_session(
                request=mock_request,
                response=mock_response,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Failed to refresh session" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_session_empty_token(
        self,
        mock_request,
        mock_auth_service,
        sample_refresh_response
    ):
        """Test refresh with empty token string"""
        # Arrange
        token = ""
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.return_value = sample_refresh_response
        
        # Act
        result = await refresh_session(
            request=mock_request,
            response=mock_response,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        # Verify service was still called - controller doesn't validate token format
        mock_auth_service.refresh_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_session_request_without_request_id(
        self,
        mock_auth_service,
        sample_refresh_response
    ):
        """Test refresh with request that has no request_id"""
        # Arrange
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        token = "session_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.return_value = sample_refresh_response
        
        # Act
        result = await refresh_session(
            request=request,
            response=mock_response,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.meta.request_id is None

    @pytest.mark.asyncio
    async def test_refresh_session_response_data_format(
        self,
        mock_request,
        mock_auth_service,
        sample_refresh_response
    ):
        """Test that response data format matches expected structure"""
        # Arrange
        token = "session_token"
        mock_response = Mock(spec=Response)
        mock_auth_service.refresh_session.return_value = sample_refresh_response
        
        # Act
        result = await refresh_session(
            request=mock_request,
            response=mock_response,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        # Response data should be None for standardized response
        assert result.data is None