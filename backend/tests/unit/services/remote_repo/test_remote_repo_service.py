"""
Test suite for RemoteRepoService
Tests remote repository operations including fetching repos, branches, cloning, and PR creation
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
from pathlib import Path

from database.models.user_sessions import UserSessions
from database.models.user_repos import RepoStatus
from services.remote_repo.remote_repo_service import RemoteRepoService
from services.remote_repo.models import (
    RepositoryList,
    RepoInfo,
    RepositoryBranchesResponse,
    BranchInfo,
    PullRequestResult
)
from services.oauth.models import OAuthError
from database.models.user import User
from schemas.oauth_provider_enum import OAuthProvider


class TestRemoteRepoService:
    """Test cases for RemoteRepoService"""
    
    def setup_method(self):
        """Setup before each test"""
        self.mock_db = Mock()
        self.service = RemoteRepoService(self.mock_db)
        
        # Mock DAOs
        self.mock_user_dao = Mock()
        self.mock_user_repos_dao = Mock()
        self.service.user_dao = self.mock_user_dao
        self.service.user_repos_dao = self.mock_user_repos_dao
        
        # Create test user session
        self.test_user_session = UserSessions(
            id="session-123",
            session_id="session-123",
            user_id="user-123",
            oauth_token="test-token"
        )
        
        # Create test user
        self.test_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_username="testuser",
            oauth_profile_url="https://github.com/testuser"
        )
    
    @pytest.mark.asyncio
    async def test_get_repositories_github_success(self):
        """Test successful repository fetching for GitHub"""
        # Setup mocks
        self.mock_user_dao.get_user_by_id.return_value = self.test_user
        
        async def mock_get_repositories():
            return RepositoryList(repositories=[
                RepoInfo(
                    id="1",
                    name="test-repo",
                    full_name="testuser/test-repo",
                    clone_url="https://github.com/testuser/test-repo.git",
                    owner="testuser",
                    private=False,
                    default_branch="main"
                )
            ])
        
        with patch('services.remote_repo.remote_repo_service.GitHubRepoLocator') as mock_github:
            mock_locator = AsyncMock()
            mock_locator.get_repositories = AsyncMock(side_effect=mock_get_repositories)
            mock_github.return_value = mock_locator
            mock_github.return_value.__aenter__ = AsyncMock(return_value=mock_locator)
            mock_github.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await self.service.get_repositories(self.test_user_session)
            
            # The result should be the actual RepositoryList object, not a mock
            assert isinstance(result, RepositoryList)
            assert len(result.repositories) == 1
            assert result.repositories[0].name == "test-repo"
    
    @pytest.mark.asyncio
    async def test_get_repositories_gitlab_success(self):
        """Test successful repository fetching for GitLab"""
        # Setup user with GitLab provider
        gitlab_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.GITLAB,
            oauth_username="testuser",
            oauth_profile_url="https://gitlab.com/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = gitlab_user
        
        async def mock_get_repositories():
            return RepositoryList(repositories=[
                RepoInfo(
                    id="1",
                    name="test-repo",
                    full_name="testuser/test-repo",
                    clone_url="https://gitlab.com/testuser/test-repo.git",
                    owner="testuser",
                    private=False,
                    default_branch="main"
                )
            ])
        
        with patch('services.remote_repo.remote_repo_service.GitLabRepoLocator') as mock_gitlab:
            mock_locator = AsyncMock()
            mock_locator.get_repositories = AsyncMock(side_effect=mock_get_repositories)
            mock_gitlab.return_value = mock_locator
            mock_gitlab.return_value.__aenter__ = AsyncMock(return_value=mock_locator)
            mock_gitlab.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await self.service.get_repositories(self.test_user_session)
            
            # The result should be the actual RepositoryList object, not a mock
            assert isinstance(result, RepositoryList)
            assert len(result.repositories) == 1
            assert result.repositories[0].name == "test-repo"
    
    @pytest.mark.asyncio
    async def test_get_repositories_bitbucket_success(self):
        """Test successful repository fetching for Bitbucket"""
        # Setup user with Bitbucket provider
        bitbucket_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.BITBUCKET,
            oauth_username="testuser",
            oauth_profile_url="https://bitbucket.org/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = bitbucket_user
        
        async def mock_get_repositories():
            return RepositoryList(repositories=[
                RepoInfo(
                    id="1",
                    name="test-repo",
                    full_name="testuser/test-repo",
                    clone_url="https://bitbucket.org/testuser/test-repo.git",
                    owner="testuser",
                    private=False,
                    default_branch="main"
                )
            ])
        
        with patch('services.remote_repo.remote_repo_service.BitbucketRepoLocator') as mock_bitbucket:
            mock_locator = AsyncMock()
            mock_locator.get_repositories = AsyncMock(side_effect=mock_get_repositories)
            mock_bitbucket.return_value = mock_locator
            mock_bitbucket.return_value.__aenter__ = AsyncMock(return_value=mock_locator)
            mock_bitbucket.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await self.service.get_repositories(self.test_user_session)
            
            # The result should be the actual RepositoryList object, not a mock
            assert isinstance(result, RepositoryList)
            assert len(result.repositories) == 1
            assert result.repositories[0].name == "test-repo"
    
    @pytest.mark.asyncio
    async def test_get_repositories_user_not_found(self):
        """Test repository fetching when user is not found"""
        self.mock_user_dao.get_user_by_id.return_value = None
        
        with pytest.raises(ValueError, match="User not found for ID: user-123"):
            await self.service.get_repositories(self.test_user_session)
    
    @pytest.mark.asyncio
    async def test_get_repositories_missing_oauth_config(self):
        """Test repository fetching when OAuth config is missing"""
        # Setup user without OAuth token
        incomplete_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_username="testuser",
            oauth_profile_url="https://github.com/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = incomplete_user
        
        # Create a session without OAuth token
        incomplete_session = UserSessions(
            id="session-123",
            session_id="session-123",
            user_id="user-123",
            oauth_token=""  # Empty string instead of None
        )
        
        with pytest.raises(ValueError, match="OAuth provider and token not configured"):
            await self.service.get_repositories(incomplete_session)
    
    @pytest.mark.asyncio
    async def test_get_repositories_unsupported_provider(self):
        """Test repository fetching with unsupported provider"""
        # Setup user with unsupported provider by mocking enum value
        unsupported_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.GITHUB,  # Use valid enum
            oauth_username="testuser",
            oauth_profile_url="https://github.com/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = unsupported_user
        
        # Mock user object to return an unsupported provider string
        mock_user = Mock()
        mock_user.oauth_provider = "unsupported"  # This will trigger error
        self.mock_user_dao.get_user_by_id.return_value = mock_user
        
        with pytest.raises(OAuthError, match="Unsupported provider: unsupported"):
            await self.service.get_repositories(self.test_user_session)
    
    @pytest.mark.asyncio
    async def test_get_repositories_bitbucket_missing_username(self):
        """Test Bitbucket repository fetching without username"""
        # Setup user with Bitbucket provider but no username
        bitbucket_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.BITBUCKET,
            oauth_username="",  # Use empty string instead of None
            oauth_profile_url="https://bitbucket.org/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = bitbucket_user
        
        with pytest.raises(ValueError, match="OAuth username not configured"):
            await self.service.get_repositories(self.test_user_session)
    
    @pytest.mark.asyncio
    async def test_get_repository_branches_success(self):
        """Test successful branch fetching"""
        self.mock_user_dao.get_user_by_id.return_value = self.test_user
        
        async def mock_get_repository_branches(*args, **kwargs):
            return RepositoryBranchesResponse(
                branches=[
                    BranchInfo(name="main", is_default=True),
                    BranchInfo(name="develop", is_default=False)
                ],
                default_branch="main"
            )
        
        with patch('services.remote_repo.remote_repo_service.GitHubRepoLocator') as mock_github:
            mock_locator = AsyncMock()
            mock_locator.get_repository_branches = AsyncMock(side_effect=mock_get_repository_branches)
            mock_github.return_value = mock_locator
            mock_github.return_value.__aenter__ = AsyncMock(return_value=mock_locator)
            mock_github.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await self.service.get_repository_branches(
                self.test_user_session, "testuser", "test-repo"
            )
            
            # The result should be the actual RepositoryBranchesResponse object, not a mock
            assert isinstance(result, RepositoryBranchesResponse)
            assert len(result.branches) == 2
            assert result.branches[0].name == "main"
    
    @pytest.mark.asyncio
    async def test_get_repository_branches_user_not_found(self):
        """Test branch fetching when user is not found"""
        self.mock_user_dao.get_user_by_id.return_value = None
        
        with pytest.raises(ValueError, match="User not found for ID: user-123"):
            await self.service.get_repository_branches(
                self.test_user_session, "testuser", "test-repo"
            )
    
    def test_clone_user_repository_success(self):
        """Test successful repository cloning"""
        # Setup mock repository
        mock_repo = Mock()
        mock_repo.user_id = "user-123"
        mock_repo.repo_name = "test-repo"
        mock_repo.repo_clone_url = "https://github.com/testuser/test-repo.git"
        mock_repo.branch = "main"
        mock_repo.status = RepoStatus.PENDING
        mock_repo.local_path = None
        
        self.mock_user_repos_dao.get_repository_by_id.return_value = mock_repo
        
        # Mock GitService
        mock_git_service = Mock()
        mock_clone_result = Mock()
        mock_clone_result.success = True
        mock_clone_result.message = "Cloned successfully"
        mock_git_service.clone_repository.return_value = mock_clone_result
        
        with patch('services.remote_repo.remote_repo_service.GitService') as mock_git_class:
            mock_git_class.return_value = mock_git_service
            with patch('services.remote_repo.remote_repo_service.settings') as mock_settings:
                mock_settings.multi_user_repo_path = "/tmp/repos"
                
                result = self.service.clone_user_repository("user-123", "repo-123")
                
                assert result is True
                self.mock_user_repos_dao.update_repository_status.assert_called_with(
                    "repo-123", RepoStatus.CLONED, local_path=str(Path("/tmp/repos/user-123/test-repo"))
                )
                self.mock_db.commit.assert_called()
    
    def test_clone_user_repository_already_cloned(self):
        """Test repository cloning when already cloned"""
        # Setup mock repository as already cloned
        mock_repo = Mock()
        mock_repo.user_id = "user-123"
        mock_repo.repo_name = "test-repo"
        mock_repo.status = RepoStatus.CLONED
        mock_repo.local_path = "/tmp/repos/user-123/test-repo"
        
        self.mock_user_repos_dao.get_repository_by_id.return_value = mock_repo
        
        with patch('services.remote_repo.remote_repo_service.settings') as mock_settings:
            mock_settings.multi_user_repo_path = "/tmp/repos"
            with patch('pathlib.Path.exists', return_value=True):
                result = self.service.clone_user_repository("user-123", "repo-123")
                
                assert result is True
    
    def test_clone_user_repository_not_found(self):
        """Test repository cloning when repository is not found"""
        self.mock_user_repos_dao.get_repository_by_id.return_value = None
        
        result = self.service.clone_user_repository("user-123", "repo-123")
        
        assert result is False
    
    def test_clone_user_repository_wrong_user(self):
        """Test repository cloning when repository belongs to different user"""
        # Setup mock repository belonging to different user
        mock_repo = Mock()
        mock_repo.user_id = "other-user"
        self.mock_user_repos_dao.get_repository_by_id.return_value = mock_repo
        
        result = self.service.clone_user_repository("user-123", "repo-123")
        
        assert result is False
    
    def test_clone_user_repository_clone_failure(self):
        """Test repository cloning when clone operation fails"""
        # Setup mock repository
        mock_repo = Mock()
        mock_repo.user_id = "user-123"
        mock_repo.repo_name = "test-repo"
        mock_repo.repo_clone_url = "https://github.com/testuser/test-repo.git"
        mock_repo.branch = "main"
        mock_repo.status = RepoStatus.PENDING
        mock_repo.local_path = None
        
        self.mock_user_repos_dao.get_repository_by_id.return_value = mock_repo
        
        # Mock GitService to fail
        mock_git_service = Mock()
        mock_clone_result = Mock()
        mock_clone_result.success = False
        mock_clone_result.message = "Clone failed"
        mock_git_service.clone_repository.return_value = mock_clone_result
        
        with patch('services.remote_repo.remote_repo_service.GitService') as mock_git_class:
            mock_git_class.return_value = mock_git_service
            with patch('services.remote_repo.remote_repo_service.settings') as mock_settings:
                mock_settings.multi_user_repo_path = "/tmp/repos"
                
                result = self.service.clone_user_repository("user-123", "repo-123")
                
                assert result is False
                self.mock_user_repos_dao.update_repository_status.assert_called_with(
                    "repo-123", RepoStatus.FAILED, error_message="Clone failed"
                )
    
    def test_clone_user_repository_exception(self):
        """Test repository cloning with exception"""
        # Setup mock repository
        mock_repo = Mock()
        mock_repo.user_id = "user-123"
        mock_repo.repo_name = "test-repo"
        mock_repo.repo_clone_url = "https://github.com/testuser/test-repo.git"
        mock_repo.branch = "main"
        mock_repo.status = RepoStatus.PENDING
        mock_repo.local_path = None
        
        self.mock_user_repos_dao.get_repository_by_id.return_value = mock_repo
        
        with patch('services.remote_repo.remote_repo_service.GitService', side_effect=Exception("Test error")):
            with patch('services.remote_repo.remote_repo_service.settings') as mock_settings:
                mock_settings.multi_user_repo_path = "/tmp/repos"
                
                result = self.service.clone_user_repository("user-123", "repo-123")
                
                assert result is False
                self.mock_user_repos_dao.update_repository_status.assert_called_with(
                    "repo-123", RepoStatus.FAILED, error_message="Test error"
                )
    
    @pytest.mark.asyncio
    async def test_create_pull_request_if_not_exists_success(self):
        """Test successful pull request creation when it doesn't exist"""
        self.mock_user_dao.get_user_by_id.return_value = self.test_user
        
        # Mock that no existing PR is found
        async def mock_check_existing_pr(*args, **kwargs):
            return PullRequestResult(
                success=False,
                error="No existing PR found"
            )
        
        # Mock successful PR creation
        async def mock_create_pr(*args, **kwargs):
            return PullRequestResult(
                success=True,
                pr_number=123,
                pr_url="https://github.com/testuser/test-repo/pull/123",
                pr_id=123
            )
        
        with patch('services.remote_repo.remote_repo_service.GitHubRepoLocator') as mock_github:
            mock_locator = AsyncMock()
            mock_locator.check_existing_pull_request = AsyncMock(side_effect=mock_check_existing_pr)
            mock_locator.create_pull_request = AsyncMock(side_effect=mock_create_pr)
            mock_github.return_value = mock_locator
            mock_github.return_value.__aenter__ = AsyncMock(return_value=mock_locator)
            mock_github.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await self.service.create_pull_request_if_not_exists(
                self.test_user_session,
                owner="testuser",
                repo="test-repo",
                head_branch="feature-branch",
                title="Test PR",
                body="Test description"
            )
            
            # The result should be the actual PullRequestResult object, not a mock
            assert isinstance(result, PullRequestResult)
            assert result.success is True
            assert result.pr_number == 123
            assert result.pr_url == "https://github.com/testuser/test-repo/pull/123"
    
    @pytest.mark.asyncio
    async def test_create_pull_request_if_not_exists_already_exists(self):
        """Test pull request creation when it already exists"""
        self.mock_user_dao.get_user_by_id.return_value = self.test_user
        
        # Mock that existing PR is found
        async def mock_check_existing_pr(*args, **kwargs):
            return PullRequestResult(
                success=True,
                pr_number=123,
                pr_url="https://github.com/testuser/test-repo/pull/123",
                pr_id=123
            )
        
        with patch('services.remote_repo.remote_repo_service.GitHubRepoLocator') as mock_github:
            mock_locator = AsyncMock()
            mock_locator.check_existing_pull_request = AsyncMock(side_effect=mock_check_existing_pr)
            mock_github.return_value = mock_locator
            mock_github.return_value.__aenter__ = AsyncMock(return_value=mock_locator)
            mock_github.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await self.service.create_pull_request_if_not_exists(
                self.test_user_session,
                owner="testuser",
                repo="test-repo",
                head_branch="feature-branch",
                title="Test PR"
            )
            
            # The result should be the actual PullRequestResult object, not a mock
            assert isinstance(result, PullRequestResult)
            assert result.success is True
            assert result.pr_number == 123
            assert result.pr_url == "https://github.com/testuser/test-repo/pull/123"
    
    @pytest.mark.asyncio
    async def test_create_pull_request_user_not_found(self):
        """Test pull request creation when user is not found"""
        self.mock_user_dao.get_user_by_id.return_value = None
        
        with pytest.raises(ValueError, match="User not found for ID: user-123"):
            await self.service.create_pull_request_if_not_exists(
                self.test_user_session,
                owner="testuser",
                repo="test-repo",
                head_branch="feature-branch",
                title="Test PR"
            )
    
    @pytest.mark.asyncio
    async def test_create_pull_request_missing_oauth_config(self):
        """Test pull request creation when OAuth config is missing"""
        # Setup user without OAuth token
        incomplete_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_username="testuser",
            oauth_profile_url="https://github.com/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = incomplete_user
        
        # Create a session without OAuth token
        incomplete_session = UserSessions(
            id="session-123",
            session_id="session-123",
            user_id="user-123",
            oauth_token=""  # Empty string instead of None
        )
        
        with pytest.raises(ValueError, match="OAuth provider and token not configured"):
            await self.service.create_pull_request_if_not_exists(
                incomplete_session,
                owner="testuser",
                repo="test-repo",
                head_branch="feature-branch",
                title="Test PR"
            )
    
    @pytest.mark.asyncio
    async def test_create_pull_request_unsupported_provider(self):
        """Test pull request creation with unsupported provider"""
        # Setup user with unsupported provider by mocking enum value
        unsupported_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.GITHUB,  # Use valid enum
            oauth_username="testuser",
            oauth_profile_url="https://github.com/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = unsupported_user
        
        # Mock user object to return an unsupported provider string
        mock_user = Mock()
        mock_user.oauth_provider = "unsupported"  # This will trigger error
        self.mock_user_dao.get_user_by_id.return_value = mock_user
        
        with pytest.raises(OAuthError, match="Unsupported provider: unsupported"):
            await self.service.create_pull_request_if_not_exists(
                self.test_user_session,
                owner="testuser",
                repo="test-repo",
                head_branch="feature-branch",
                title="Test PR"
            )
    
    @pytest.mark.asyncio
    async def test_create_pull_request_bitbucket_missing_username(self):
        """Test Bitbucket pull request creation without username"""
        # Setup user with Bitbucket provider but no username
        bitbucket_user = User(
            id="user-123",
            oauth_provider=OAuthProvider.BITBUCKET,
            oauth_username="",  # Use empty string instead of None
            oauth_profile_url="https://bitbucket.org/testuser"
        )
        self.mock_user_dao.get_user_by_id.return_value = bitbucket_user
        
        with pytest.raises(ValueError, match="OAuth username not configured"):
            await self.service.create_pull_request_if_not_exists(
                self.test_user_session,
                owner="testuser",
                repo="test-repo",
                head_branch="feature-branch",
                title="Test PR"
            )