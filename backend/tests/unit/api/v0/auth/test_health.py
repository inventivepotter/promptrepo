"""
Unit tests for the auth health check endpoint.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import status
from sqlmodel import Session

from api.v0.auth.health import auth_health_check
from middlewares.rest import StandardResponse, AppException


class TestAuthHealthCheck:
    """Tests for auth health check endpoint"""

    @pytest.mark.asyncio
    async def test_auth_health_check_success(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test successful health check"""
        # Arrange
        mock_auth_service.cleanup_expired_sessions.return_value = 3
        
        with patch('api.v0.auth.health.select') as mock_select, \
             patch.object(mock_db_session, 'exec') as mock_exec:
            # Mock the database count query
            mock_exec.return_value.one.return_value = 10
            
            # Act
            result = await auth_health_check(
                request=mock_request,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
            
            # Assert
            assert isinstance(result, StandardResponse)
            assert result.status == "success"
            assert result.message == "Authentication service is healthy"
            assert result.meta.request_id == "test_request_id"
            
            # Check health data
            assert result.data is not None
            health_data = result.data
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "authentication"
            assert health_data["active_sessions"] == 10
            assert health_data["expired_sessions_cleaned"] == 3
            assert health_data["pending_oauth_states"] == 0
            assert len(health_data["endpoints"]) == 5
            
            # Verify service calls
            mock_auth_service.cleanup_expired_sessions.assert_called_once()

    @pytest.mark.asyncio
    async def test_auth_health_check_auth_service_error(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test health check when auth service cleanup fails"""
        # Arrange
        mock_auth_service.cleanup_expired_sessions.side_effect = Exception("Service error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await auth_health_check(
                request=mock_request,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
        
        assert "Health check failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_health_check_database_error(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test health check when database query fails"""
        # Arrange
        mock_auth_service.cleanup_expired_sessions.return_value = 2
        
        with patch('api.v0.auth.health.select') as mock_select, \
             patch.object(mock_db_session, 'exec') as mock_exec:
            # Mock database error
            mock_exec.side_effect = Exception("Database error")
            
            # Act & Assert
            with pytest.raises(AppException) as exc_info:
                await auth_health_check(
                    request=mock_request,
                    db=mock_db_session,
                    auth_service=mock_auth_service
                )
            
            assert "Health check failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_health_check_request_without_request_id(
        self,
        mock_db_session,
        mock_auth_service
    ):
        """Test health check with request that has no request_id"""
        # Arrange
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        
        mock_auth_service.cleanup_expired_sessions.return_value = 1
        
        with patch('api.v0.auth.health.select') as mock_select, \
             patch.object(mock_db_session, 'exec') as mock_exec:
            mock_exec.return_value.one.return_value = 5
            
            # Act
            result = await auth_health_check(
                request=request,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
            
            # Assert
            assert isinstance(result, StandardResponse)
            assert result.status == "success"
            assert result.meta.request_id is None

    @pytest.mark.asyncio
    async def test_auth_health_check_zero_sessions(
        self,
        mock_request,
        mock_db_session,
        mock_auth_service
    ):
        """Test health check with zero active sessions"""
        # Arrange
        mock_auth_service.cleanup_expired_sessions.return_value = 0
        
        with patch('api.v0.auth.health.select') as mock_select, \
             patch.object(mock_db_session, 'exec') as mock_exec:
            mock_exec.return_value.one.return_value = 0
            
            # Act
            result = await auth_health_check(
                request=mock_request,
                db=mock_db_session,
                auth_service=mock_auth_service
            )
            
            # Assert
            assert isinstance(result, StandardResponse)
            assert result.status == "success"
            assert result.data is not None
            assert result.data["active_sessions"] == 0
            assert result.data["expired_sessions_cleaned"] == 0