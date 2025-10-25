"""
Tests for the LocalRepoService
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.git_service import GitService
from services.config.models import RepoConfig


class TestLocalRepoService:
    """Test cases for LocalRepoService."""

    @pytest.fixture
    def mock_config_service(self):
        """Mock configuration service for testing"""
        mock = Mock()
        mock.get_base_branch_for_repo.return_value = "main"
        mock.get_repo_url_for_repo.return_value = "https://github.com/test/repo.git"
        mock.get_hosting_config.return_value = Mock()
        mock.get_hosting_config.return_value.type = "individual"
        return mock

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing"""
        return Mock()

    @pytest.fixture
    def local_repo_service(self, mock_config_service, mock_db_session):
        """LocalRepoService instance with mocked dependencies"""
        service = LocalRepoService(
            config_service=mock_config_service,
            db=mock_db_session,
            remote_repo_service=None
        )
        return service

    @pytest.fixture
    def temp_repo_path(self):
        """Create a temporary repository path for testing"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "test-repo"
        repo_path.mkdir()
        
        # Create a .git directory to simulate a git repo
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        
        yield repo_path
        
        # Clean up
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_success(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test successful get_latest_base_branch_content"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.return_value = "main"
                    mock_git_service.switch_branch.return_value = Mock(success=True)
                    mock_git_service.pull_latest.return_value = Mock(success=True)
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=oauth_token
                    )
                    
                    # Assert
                    assert result["success"] is True
                    assert "Successfully fetched latest content" in result["message"]
                    
                    # Verify service calls
                    mock_config_service.get_base_branch_for_repo.assert_called_once_with(user_id, repo_name)
                    mock_git_service.get_current_branch.assert_called_once()
                    mock_git_service.switch_branch.assert_not_called()  # Already on main branch
                    mock_git_service.pull_latest.assert_called_once_with(
                        oauth_token=oauth_token,
                        branch_name="main",
                        force=True
                    )

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_switch_branch(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test get_latest_base_branch_content when switching branches"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.return_value = "feature-branch"  # Not on main
                    mock_git_service.switch_branch.return_value = Mock(success=True)
                    mock_git_service.pull_latest.return_value = Mock(success=True)
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=oauth_token
                    )
                    
                    # Assert
                    assert result["success"] is True
                    assert "Successfully fetched latest content" in result["message"]
                    
                    # Verify service calls
                    mock_config_service.get_base_branch_for_repo.assert_called_once_with(user_id, repo_name)
                    mock_git_service.get_current_branch.assert_called_once()
                    mock_git_service.switch_branch.assert_called_once_with("main")
                    mock_git_service.pull_latest.assert_called_once_with(
                        oauth_token=oauth_token,
                        branch_name="main",
                        force=True
                    )

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_repo_not_found(
        self,
        local_repo_service,
        mock_config_service
    ):
        """Test get_latest_base_branch_content when repository doesn't exist"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "nonexistent-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to a non-existent directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=Path("/nonexistent")):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                
                # Act
                result = await local_repo_service.get_latest_base_branch_content(
                    user_id=user_id,
                    repo_name=repo_name,
                    oauth_token=oauth_token
                )
                
                # Assert
                assert result["success"] is False
                assert "Repository nonexistent-repo not found" in result["message"]

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_cannot_get_current_branch(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test get_latest_base_branch_content when current branch cannot be determined"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.return_value = None  # Cannot determine branch
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=oauth_token
                    )
                    
                    # Assert
                    assert result["success"] is False
                    assert "Could not determine current branch" in result["message"]

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_switch_branch_fails(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test get_latest_base_branch_content when switching branch fails"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.return_value = "feature-branch"  # Not on main
                    mock_git_service.switch_branch.return_value = Mock(
                        success=False,
                        message="Failed to switch branch"
                    )
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=oauth_token
                    )
                    
                    # Assert
                    assert result["success"] is False
                    assert "Failed to switch to base branch" in result["message"]

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_pull_fails(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test get_latest_base_branch_content when pull fails"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.return_value = "main"
                    mock_git_service.pull_latest.return_value = Mock(
                        success=False,
                        message="Pull failed"
                    )
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=oauth_token
                    )
                    
                    # Assert
                    assert result["success"] is False
                    assert "Failed to pull latest changes" in result["message"]

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_without_oauth_token(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test get_latest_base_branch_content without OAuth token"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.return_value = "main"
                    mock_git_service.switch_branch.return_value = Mock(success=True)
                    mock_git_service.pull_latest.return_value = Mock(success=True)
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=None
                    )
                    
                    # Assert
                    assert result["success"] is True
                    assert "Successfully fetched latest content" in result["message"]
                    
                    # Verify pull_latest was called with None OAuth token
                    mock_git_service.pull_latest.assert_called_once_with(
                        oauth_token=None,
                        branch_name="main",
                        force=True
                    )

    @pytest.mark.asyncio
    async def test_get_latest_base_branch_content_exception(
        self,
        local_repo_service,
        mock_config_service,
        temp_repo_path
    ):
        """Test get_latest_base_branch_content when an exception occurs"""
        # Arrange
        user_id = "test_user_id"
        repo_name = "test-repo"
        oauth_token = "test_oauth_token"
        
        # Mock the repo path to use our temp directory
        with patch.object(local_repo_service, '_get_repo_base_path', return_value=temp_repo_path.parent):
            with patch.object(local_repo_service, 'config_service', mock_config_service):
                # Mock GitService to raise an exception
                with patch('services.local_repo.local_repo_service.GitService') as mock_git_service_class:
                    mock_git_service = Mock(spec=GitService)
                    mock_git_service.get_current_branch.side_effect = Exception("Git error")
                    mock_git_service_class.return_value = mock_git_service
                    
                    # Act
                    result = await local_repo_service.get_latest_base_branch_content(
                        user_id=user_id,
                        repo_name=repo_name,
                        oauth_token=oauth_token
                    )
                    
                    # Assert
                    assert result["success"] is False
                    assert "Error: Git error" in result["message"]