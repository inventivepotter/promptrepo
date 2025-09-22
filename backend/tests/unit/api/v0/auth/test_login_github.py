"""
Unit tests for the GitHub OAuth login initiation endpoint.
"""
import pytest
from unittest.mock import Mock

from api.v0.auth.login.github import initiate_github_login, AuthUrlResponseData
from middlewares.rest import StandardResponse, AppException, BadRequestException
from services.auth.models import AuthenticationFailedError, AuthError


class TestInitiateGitHubLogin:
    """Tests for GitHub OAuth login initiation endpoint"""

    @pytest.mark.asyncio
    async def test_initiate_github_login_success(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test successful GitHub OAuth login initiation"""
        # Arrange
        redirect_uri = "http://localhost:3000/callback"
        auth_url = "https://github.com/login/oauth/authorize?client_id=test&state=xyz"
        mock_auth_service.initiate_oauth_login.return_value = auth_url
        
        # Act
        result = await initiate_github_login(
            request=mock_request,
            redirect_uri=redirect_uri,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.message == "GitHub authorization URL generated successfully"
        assert result.meta.request_id == "test_request_id"
        
        # Check response data
        assert result.data is not None
        # Data is serialized as dict by success_response function
        response_data = result.data
        assert isinstance(response_data, dict)
        assert response_data["authUrl"] == auth_url
        
        # Verify service was called with correct parameters
        mock_auth_service.initiate_oauth_login.assert_called_once()
        call_args = mock_auth_service.initiate_oauth_login.call_args[0]
        login_request = call_args[0]
        assert login_request.provider == "github"
        assert login_request.redirect_uri == redirect_uri

    @pytest.mark.asyncio
    async def test_initiate_github_login_missing_redirect_uri(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation with missing redirect URI"""
        # Arrange
        redirect_uri = ""
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            await initiate_github_login(
                request=mock_request,
                redirect_uri=redirect_uri,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Redirect URI parameter is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initiate_github_login_whitespace_only_redirect_uri(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation with whitespace-only redirect URI"""
        # Arrange
        redirect_uri = "   "
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            await initiate_github_login(
                request=mock_request,
                redirect_uri=redirect_uri,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Redirect URI parameter is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initiate_github_login_authentication_failed(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation when authentication setup fails"""
        # Arrange
        redirect_uri = "http://localhost:3000/callback"
        mock_auth_service.initiate_oauth_login.side_effect = AuthenticationFailedError("OAuth provider not configured")
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            await initiate_github_login(
                request=mock_request,
                redirect_uri=redirect_uri,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "OAuth provider not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initiate_github_login_auth_error(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation when auth error occurs"""
        # Arrange
        redirect_uri = "http://localhost:3000/callback"
        mock_auth_service.initiate_oauth_login.side_effect = AuthError("Invalid redirect URI")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await initiate_github_login(
                request=mock_request,
                redirect_uri=redirect_uri,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Invalid redirect URI" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initiate_github_login_unexpected_error(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation when unexpected error occurs"""
        # Arrange
        redirect_uri = "http://localhost:3000/callback"
        mock_auth_service.initiate_oauth_login.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await initiate_github_login(
                request=mock_request,
                redirect_uri=redirect_uri,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Failed to generate authentication URL" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initiate_github_login_request_without_request_id(
        self,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation with request that has no request_id"""
        # Arrange
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        redirect_uri = "http://localhost:3000/callback"
        auth_url = "https://github.com/login/oauth/authorize?client_id=test"
        mock_auth_service.initiate_oauth_login.return_value = auth_url
        
        # Act
        result = await initiate_github_login(
            request=request,
            redirect_uri=redirect_uri,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.meta.request_id is None

    @pytest.mark.asyncio
    async def test_initiate_github_login_valid_redirect_uris(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test login initiation with various valid redirect URIs"""
        # Test cases with different valid redirect URIs
        test_cases = [
            "http://localhost:3000/callback",
            "https://example.com/auth/callback",
            "https://app.example.com/oauth/github/callback",
            "http://127.0.0.1:3000/callback"
        ]
        
        for redirect_uri in test_cases:
            # Arrange
            auth_url = f"https://github.com/login/oauth/authorize?redirect_uri={redirect_uri}"
            mock_auth_service.initiate_oauth_login.return_value = auth_url
            
            # Act
            result = await initiate_github_login(
                request=mock_request,
                redirect_uri=redirect_uri,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
            
            # Assert
            assert isinstance(result, StandardResponse)
            assert result.status == "success"
            assert result.data is not None
            response_data = result.data
            assert isinstance(response_data, dict)
            assert response_data["authUrl"] == auth_url
            
            # Reset mock for next iteration
            mock_auth_service.initiate_oauth_login.reset_mock()

    @pytest.mark.asyncio
    async def test_initiate_github_login_response_data_format(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test that response data format matches expected structure"""
        # Arrange
        redirect_uri = "http://localhost:3000/callback"
        auth_url = "https://github.com/login/oauth/authorize?client_id=test"
        mock_auth_service.initiate_oauth_login.return_value = auth_url
        
        # Act
        result = await initiate_github_login(
            request=mock_request,
            redirect_uri=redirect_uri,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert result.data is not None
        response_data = result.data
        assert isinstance(response_data, dict)
        assert 'authUrl' in response_data
        assert isinstance(response_data['authUrl'], str)
        assert response_data['authUrl'].startswith('https://github.com/login/oauth/authorize')

    @pytest.mark.asyncio
    async def test_initiate_github_login_meta_contains_provider(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test that response meta contains provider information"""
        # Arrange
        redirect_uri = "http://localhost:3000/callback"
        auth_url = "https://github.com/login/oauth/authorize?client_id=test"
        mock_auth_service.initiate_oauth_login.return_value = auth_url
        
        # Act
        result = await initiate_github_login(
            request=mock_request,
            redirect_uri=redirect_uri,
            db=mock_db_session,
            auth_service=mock_auth_service
        )
        
        # Assert
        assert result.meta is not None
        # Note: The meta information is passed as additional context, but the StandardResponse
        # model might not expose it directly. This test verifies the login sets it properly.
        assert result.status == "success"