"""
Unit tests for the get_latest repository endpoint.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import status

from api.v0.repos.get_latest import get_latest_prompt
from middlewares.rest import StandardResponse, AppException, NotFoundException


class TestGetLatestPrompt:
    """Tests for get_latest prompt endpoint"""

    @pytest.mark.asyncio
    async def test_get_latest_prompt_success(
        self,
        mock_request,
        mock_local_repo_service,
        mock_user_session,
        sample_get_latest_response
    ):
        """Test successful get_latest prompt"""
        # Arrange
        repo_name = "test-repo"
        user_id = "test_user_id"
        
        mock_local_repo_service.get_latest_base_branch_content.return_value = sample_get_latest_response
        
        # Act
        result = await get_latest_prompt(
            request=mock_request,
            user_id=user_id,
            local_repo_service=mock_local_repo_service,
            user_session=mock_user_session,
            repo_name=repo_name
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.message == "Latest prompts fetched successfully"
        assert result.meta.request_id == "test_request_id"
        assert result.data == sample_get_latest_response
        
        # Verify service call
        mock_local_repo_service.get_latest_base_branch_content.assert_called_once_with(
            user_id=user_id,
            repo_name=repo_name,
            oauth_token="test_oauth_token"
        )

    @pytest.mark.asyncio
    async def test_get_latest_prompt_service_failure(
        self,
        mock_request,
        mock_local_repo_service,
        mock_user_session
    ):
        """Test get_latest prompt when service returns failure"""
        # Arrange
        repo_name = "test-repo"
        user_id = "test_user_id"
        
        failure_response = {
            "success": False,
            "message": "Repository not found"
        }
        mock_local_repo_service.get_latest_base_branch_content.return_value = failure_response
        
        # Act
        result = await get_latest_prompt(
            request=mock_request,
            user_id=user_id,
            local_repo_service=mock_local_repo_service,
            user_session=mock_user_session,
            repo_name=repo_name
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.message == "Latest prompts fetched successfully"
        assert result.data == failure_response

    @pytest.mark.asyncio
    async def test_get_latest_prompt_service_exception(
        self,
        mock_request,
        mock_local_repo_service,
        mock_user_session
    ):
        """Test get_latest prompt when service raises an exception"""
        # Arrange
        repo_name = "test-repo"
        user_id = "test_user_id"
        
        mock_local_repo_service.get_latest_base_branch_content.side_effect = Exception("Service error")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await get_latest_prompt(
                request=mock_request,
                user_id=user_id,
                local_repo_service=mock_local_repo_service,
                user_session=mock_user_session,
                repo_name=repo_name
            )
        
        assert "Failed to fetch latest prompts" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_latest_prompt_without_request_id(
        self,
        mock_local_repo_service,
        mock_user_session,
        sample_get_latest_response
    ):
        """Test get_latest prompt with request that has no request_id"""
        # Arrange
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        
        repo_name = "test-repo"
        user_id = "test_user_id"
        
        mock_local_repo_service.get_latest_base_branch_content.return_value = sample_get_latest_response
        
        # Act
        result = await get_latest_prompt(
            request=request,
            user_id=user_id,
            local_repo_service=mock_local_repo_service,
            user_session=mock_user_session,
            repo_name=repo_name
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.meta.request_id is None

    @pytest.mark.asyncio
    async def test_get_latest_prompt_without_oauth_token(
        self,
        mock_request,
        mock_local_repo_service,
        sample_get_latest_response
    ):
        """Test get_latest prompt when user session has no OAuth token"""
        # Arrange
        repo_name = "test-repo"
        user_id = "test_user_id"
        
        # Mock session without OAuth token
        session_without_token = Mock()
        session_without_token.oauth_token = None
        
        mock_local_repo_service.get_latest_base_branch_content.return_value = sample_get_latest_response
        
        # Act
        result = await get_latest_prompt(
            request=mock_request,
            user_id=user_id,
            local_repo_service=mock_local_repo_service,
            user_session=session_without_token,
            repo_name=repo_name
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        
        # Verify service call with None OAuth token
        mock_local_repo_service.get_latest_base_branch_content.assert_called_once_with(
            user_id=user_id,
            repo_name=repo_name,
            oauth_token=None
        )