"""
Unit tests for the verify session endpoint.
"""
import pytest
from unittest.mock import Mock

from api.v0.auth.verify import verify_session
from api.deps import get_bearer_token
from middlewares.rest import StandardResponse, AppException, AuthenticationException
from services.auth.models import SessionNotFoundError, TokenValidationError, AuthError


class TestGetBearerToken:
    """Tests for get_bearer_token dependency"""

    @pytest.mark.asyncio
    async def test_get_bearer_token_success(self):
        """Test successful token extraction"""
        # Arrange
        authorization = "Bearer test_token_123"
        
        # Act
        result = await get_bearer_token(authorization=authorization)
        
        # Assert
        assert result == "test_token_123"

    @pytest.mark.asyncio
    async def test_get_bearer_token_missing_header(self):
        """Test token extraction when Authorization header is missing"""
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await get_bearer_token(authorization=None)
        
        assert "Unauthorized Access" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_bearer_token_invalid_format(self):
        """Test token extraction with invalid header format"""
        # Arrange
        authorization = "InvalidFormat test_token"
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await get_bearer_token(authorization=authorization)
        
        assert "Invalid authorization header format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_bearer_token_empty_header(self):
        """Test token extraction with empty header"""
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await get_bearer_token(authorization="")
        
        assert "Unauthorized Access" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_bearer_token_bearer_only(self):
        """Test token extraction with 'Bearer ' only"""
        # Arrange
        authorization = "Bearer "
        
        # Act
        result = await get_bearer_token(authorization=authorization)
        
        # Assert
        assert result == ""


    @pytest.mark.asyncio
    async def test_verify_session_success(
        self,
        mock_request,
        mock_auth_service,
        sample_verify_response
    ):
        """Test successful session verification"""
        # Arrange
        token = "valid_session_token"
        mock_auth_service.verify_session.return_value = sample_verify_response
        
        # Act
        result = await verify_session(
            request=mock_request,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.message == "Session verified successfully"
        assert result.meta.request_id == "test_request_id"
        
        # Check response data contains user
        assert result.data is not None
        # Data is serialized as dict by success_response function
        response_data = result.data
        assert isinstance(response_data, dict)
        assert response_data["oauth_username"] == "testuser"
        assert response_data["oauth_email"] == "test@example.com"
        
        # Verify service was called with correct parameters
        mock_auth_service.verify_session.assert_called_once()
        call_args = mock_auth_service.verify_session.call_args[0]
        verify_request = call_args[0]
        assert verify_request.session_token == token

    @pytest.mark.asyncio
    async def test_verify_session_not_found(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test verify when session is not found"""
        # Arrange
        token = "invalid_session_token"
        mock_auth_service.verify_session.side_effect = SessionNotFoundError("Invalid or expired session token")
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await verify_session(
                request=mock_request,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Authentication required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_session_token_validation_error(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test verify when OAuth token validation fails"""
        # Arrange
        token = "session_with_revoked_oauth_token"
        mock_auth_service.verify_session.side_effect = TokenValidationError("OAuth token has been revoked")
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await verify_session(
                request=mock_request,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_session_auth_error(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test verify when auth error occurs"""
        # Arrange
        token = "session_token"
        mock_auth_service.verify_session.side_effect = AuthError("Auth service error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await verify_session(
                request=mock_request,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Auth service error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_session_unexpected_error(
        self,
        mock_request,
        mock_auth_service
    ):
        """Test verify when unexpected error occurs"""
        # Arrange
        token = "session_token"
        mock_auth_service.verify_session.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await verify_session(
                request=mock_request,
                token=token,
                auth_service=mock_auth_service
            )
        
        assert "Failed to verify session" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_session_empty_token(
        self,
        mock_request,
        mock_auth_service,
        sample_verify_response
    ):
        """Test verify with empty token string"""
        # Arrange
        token = ""
        mock_auth_service.verify_session.return_value = sample_verify_response
        
        # Act
        result = await verify_session(
            request=mock_request,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        # Verify service was still called - controller doesn't validate token format
        mock_auth_service.verify_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_session_request_without_request_id(
        self,
        mock_auth_service,
        sample_verify_response
    ):
        """Test verify with request that has no request_id"""
        # Arrange
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        token = "session_token"
        mock_auth_service.verify_session.return_value = sample_verify_response
        
        # Act
        result = await verify_session(
            request=request,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.meta.request_id is None

    @pytest.mark.asyncio
    async def test_verify_session_user_data_format(
        self,
        mock_request,
        mock_auth_service,
        sample_verify_response
    ):
        """Test that user data format matches expected structure"""
        # Arrange
        token = "session_token"
        mock_auth_service.verify_session.return_value = sample_verify_response
        
        # Act
        result = await verify_session(
            request=mock_request,
            token=token,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert result.data is not None
        user = result.data
        assert isinstance(user, dict)
        assert 'id' in user
        assert 'oauth_username' in user
        assert 'oauth_name' in user
        assert 'oauth_email' in user
        assert 'oauth_avatar_url' in user
        assert 'oauth_user_id' in user
        assert 'oauth_profile_url' in user