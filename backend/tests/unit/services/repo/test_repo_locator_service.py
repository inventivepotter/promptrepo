"""
Unit tests for repo locator service

Tests the RepoLocatorService functionality including local and OAuth-based
repository locating strategies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from typing import Dict

from services.repo.repo_locator_service import RepoLocatorService, LocalRepoLocator, RepoInfo
from schemas.hosting_type_enum import HostingType
from services.config.models import HostingConfig
from services.config.config_interface import IConfig


class TestLocalRepoLocator:
    """Test the LocalRepoLocator class"""
    
    @patch('services.repo.repo_locator_service.Settings')
    def test_init_creates_directory_if_not_exists(self, mock_settings):
        """Test that LocalRepoLocator creates directory if it doesn't exist"""
        mock_settings.local_repo_path = "/test/path"
        
        with patch('pathlib.Path.exists', return_value=False) as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            
            locator = LocalRepoLocator()
            
            assert locator.base_path == Path("/test/path")
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('services.repo.repo_locator_service.Settings')
    async def test_get_repositories_returns_git_repos(self, mock_settings):
        """Test that get_repositories returns only directories with .git folder"""
        mock_settings.local_repo_path = "/test/path"
        
        # Mock directory structure
        mock_repo1 = Mock()
        mock_repo1.name = "repo1"
        mock_repo1.is_dir.return_value = True
        mock_repo1.resolve.return_value = Path("/test/path/repo1")
        
        mock_repo2 = Mock()
        mock_repo2.name = "repo2"
        mock_repo2.is_dir.return_value = True
        mock_repo2.resolve.return_value = Path("/test/path/repo2")
        
        mock_not_repo = Mock()
        mock_not_repo.name = "not_repo"
        mock_not_repo.is_dir.return_value = True
        
        mock_file = Mock()
        mock_file.is_dir.return_value = False
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.iterdir', return_value=[mock_repo1, mock_repo2, mock_not_repo, mock_file]):
            
            # Mock .git existence
            def git_exists_side_effect(path):
                if "repo1" in str(path) or "repo2" in str(path):
                    return True
                return False
            
            with patch('pathlib.Path.exists', side_effect=git_exists_side_effect):
                locator = LocalRepoLocator()
                repos = await locator.get_repositories()
                
                expected = {
                    "repo1": "/test/path/repo1",
                    "repo2": "/test/path/repo2"
                }
                assert repos == expected
    
    @patch('services.repo.repo_locator_service.Settings')
    async def test_get_repositories_empty_when_no_git_repos(self, mock_settings):
        """Test that get_repositories returns empty dict when no git repos found"""
        mock_settings.local_repo_path = "/test/path"
        
        mock_dir = Mock()
        mock_dir.is_dir.return_value = True
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.iterdir', return_value=[mock_dir]):
            
            # Mock no .git folders
            with patch('pathlib.Path.exists', return_value=False):
                locator = LocalRepoLocator()
                repos = await locator.get_repositories()
                
                assert repos == {}


class TestRepoLocatorService:
    """Test the RepoLocatorService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config_service = Mock(spec=IConfig)
        self.mock_git_provider_service = AsyncMock()
        self.service = RepoLocatorService(
            config_service=self.mock_config_service,
            git_provider_service=self.mock_git_provider_service
        )
    
    @patch('services.repo.repo_locator_service.LocalRepoLocator')
    async def test_get_repositories_individual_hosting(self, mock_local_locator_class):
        """Test get_repositories with individual hosting type"""
        # Setup hosting config
        hosting_config = HostingConfig(type=HostingType.INDIVIDUAL)
        self.mock_config_service.get_hosting_config.return_value = hosting_config
        
        # Setup mock locator
        mock_locator = AsyncMock()
        mock_locator.get_repositories.return_value = {"repo1": "/path/to/repo1"}
        mock_local_locator_class.return_value = mock_locator
        
        # Call method
        result = await self.service.get_repositories()
        
        # Verify
        assert result == {"repo1": "/path/to/repo1"}
        self.mock_config_service.get_hosting_config.assert_called_once()
        mock_local_locator_class.assert_called_once()
        mock_locator.get_repositories.assert_called_once()
        self.mock_git_provider_service.get_user_repositories.assert_not_called()
    
    async def test_get_repositories_organization_hosting_success(self):
        """Test get_repositories with organization hosting type and valid oauth"""
        # Setup hosting config
        hosting_config = HostingConfig(type=HostingType.ORGANIZATION)
        self.mock_config_service.get_hosting_config.return_value = hosting_config
        
        # Setup mock git provider service
        expected_repos = {"org-repo1": "https://github.com/org/repo1.git"}
        self.mock_git_provider_service.get_user_repositories.return_value = expected_repos
        
        # Call method
        result = await self.service.get_repositories(
            oauth_provider="github",
            username="testuser",
            oauth_token="test-token"
        )
        
        # Verify
        assert result == expected_repos
        self.mock_config_service.get_hosting_config.assert_called_once()
        self.mock_git_provider_service.get_user_repositories.assert_called_once_with(
            "github", "test-token"
        )
    
    async def test_get_repositories_organization_hosting_missing_oauth_provider(self):
        """Test get_repositories with organization hosting but missing oauth provider"""
        # Setup hosting config
        hosting_config = HostingConfig(type=HostingType.ORGANIZATION)
        self.mock_config_service.get_hosting_config.return_value = hosting_config
        
        # Call method and expect ValueError
        with pytest.raises(ValueError, match="OAuth provider and token are required"):
            await self.service.get_repositories(oauth_token="test-token")
    
    async def test_get_repositories_organization_hosting_missing_oauth_token(self):
        """Test get_repositories with organization hosting but missing oauth token"""
        # Setup hosting config
        hosting_config = HostingConfig(type=HostingType.ORGANIZATION)
        self.mock_config_service.get_hosting_config.return_value = hosting_config
        
        # Call method and expect ValueError
        with pytest.raises(ValueError, match="OAuth provider and token are required"):
            await self.service.get_repositories(oauth_provider="github")
    
    async def test_get_repositories_unsupported_hosting_type(self):
        """Test get_repositories with unsupported hosting type"""
        # Setup hosting config with mocked invalid type by patching the type attribute
        hosting_config = HostingConfig(type=HostingType.INDIVIDUAL)
        # Mock the type to be something invalid
        with patch.object(hosting_config, 'type', "INVALID_TYPE"):
            self.mock_config_service.get_hosting_config.return_value = hosting_config
            
            # Call method and expect ValueError
            with pytest.raises(ValueError, match="Unsupported hosting type"):
                await self.service.get_repositories()
    
    async def test_get_repositories_organization_hosting_with_all_params(self):
        """Test get_repositories with organization hosting and all parameters"""
        # Setup hosting config
        hosting_config = HostingConfig(type=HostingType.ORGANIZATION)
        self.mock_config_service.get_hosting_config.return_value = hosting_config
        
        # Setup mock git provider service
        expected_repos = {
            "user-repo1": "https://github.com/user/repo1.git",
            "user-repo2": "https://github.com/user/repo2.git"
        }
        self.mock_git_provider_service.get_user_repositories.return_value = expected_repos
        
        # Call method with all parameters
        result = await self.service.get_repositories(
            oauth_provider="gitlab",
            username="testuser",
            oauth_token="gitlab-token"
        )
        
        # Verify
        assert result == expected_repos
        self.mock_config_service.get_hosting_config.assert_called_once()
        self.mock_git_provider_service.get_user_repositories.assert_called_once_with(
            "gitlab", "gitlab-token"
        )


class TestRepoInfo:
    """Test the RepoInfo model"""
    
    def test_repo_info_minimal_fields(self):
        """Test RepoInfo with minimal required fields"""
        repo_info = RepoInfo(
            name="test-repo",
            full_name="user/test-repo",
            clone_url="https://github.com/user/test-repo.git",
            owner="user"
        )
        
        assert repo_info.name == "test-repo"
        assert repo_info.full_name == "user/test-repo"
        assert repo_info.clone_url == "https://github.com/user/test-repo.git"
        assert repo_info.owner == "user"
        assert repo_info.private is False
        assert repo_info.default_branch == "main"
        assert repo_info.language is None
        assert repo_info.size == 0
        assert repo_info.updated_at is None
    
    def test_repo_info_all_fields(self):
        """Test RepoInfo with all fields"""
        repo_info = RepoInfo(
            name="test-repo",
            full_name="user/test-repo",
            clone_url="https://github.com/user/test-repo.git",
            owner="user",
            private=True,
            default_branch="develop",
            language="Python",
            size=1024,
            updated_at="2023-01-01T00:00:00Z"
        )
        
        assert repo_info.name == "test-repo"
        assert repo_info.full_name == "user/test-repo"
        assert repo_info.clone_url == "https://github.com/user/test-repo.git"
        assert repo_info.owner == "user"
        assert repo_info.private is True
        assert repo_info.default_branch == "develop"
        assert repo_info.language == "Python"
        assert repo_info.size == 1024
        assert repo_info.updated_at == "2023-01-01T00:00:00Z"