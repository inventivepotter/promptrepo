"""
Tests for the Git service.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from services.git.git_service import GitService
from services.git.models import GitOperationResult, PullRequestResult, RepoStatus


class TestGitService:
    """Test cases for GitService."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository for testing."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repository
        import git
        repo = git.Repo.init(repo_path)
        
        # Create initial commit
        test_file = repo_path / "README.md"
        test_file.write_text("# Test Repository")
        repo.index.add([str(test_file.relative_to(repo_path))])
        repo.index.commit("Initial commit")
        
        # Set branch name to main
        repo.git.branch("-m", "main")
        
        yield repo_path
        
        # Clean up
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def git_service(self, temp_repo):
        """Create a GitService instance with a temporary repository."""
        return GitService(temp_repo)

    def test_init(self, temp_repo):
        """Test GitService initialization."""
        service = GitService(temp_repo)
        assert service.repo_path == temp_repo

    def test_checkout_new_branch(self, git_service):
        """Test creating and checking out a new branch."""
        result = git_service.checkout_new_branch("test-branch")
        
        assert isinstance(result, GitOperationResult)
        assert result.success is True
        assert "Successfully created and checked out branch" in result.message

    def test_checkout_existing_branch(self, git_service):
        """Test checking out an existing branch."""
        # Create a branch first
        git_service.checkout_new_branch("existing-branch")
        
        # Switch back to main
        git_service.switch_branch("main")
        
        # Checkout the existing branch
        result = git_service.checkout_new_branch("existing-branch")
        
        assert isinstance(result, GitOperationResult)
        assert result.success is True
        assert "Successfully checked out existing branch" in result.message

    def test_add_files_list(self, git_service):
        """Test adding existing files to staging."""
        # Create a test file
        test_file = git_service.repo_path / "test.txt"
        test_file.write_text("Test content")
        
        # Add the file using relative path
        rel_path = str(test_file.relative_to(git_service.repo_path))
        result = git_service.add_files([rel_path])
        
        assert isinstance(result, GitOperationResult)
        assert result.success is True
        assert "Successfully added 1 files" in result.message
        assert result.data is not None
        assert result.data["added_files"] == [rel_path]

    def test_add_files_dict(self, git_service):
        """Test creating and adding files to staging."""
        # Create files from dict
        files = {
            "file1.txt": "Content 1",
            "file2.txt": "Content 2"
        }
        
        result = git_service.add_files(files)
        
        assert isinstance(result, GitOperationResult)
        assert result.success is True
        assert "Successfully added 2 files" in result.message
        assert result.data is not None
        assert len(result.data["added_files"]) == 2
        
        # Check files were created
        assert (git_service.repo_path / "file1.txt").exists()
        assert (git_service.repo_path / "file2.txt").exists()

    def test_commit_changes(self, git_service):
        """Test committing changes."""
        # Create and add a file
        test_file = git_service.repo_path / "test.txt"
        test_file.write_text("Test content")
        rel_path = str(test_file.relative_to(git_service.repo_path))
        git_service.add_files([rel_path])
        
        # Commit changes
        result = git_service.commit_changes("Test commit")
        
        assert isinstance(result, GitOperationResult)
        assert result.success is True
        assert "Successfully committed" in result.message
        assert result.data is not None
        assert "commit_hash" in result.data

    def test_commit_no_changes(self, git_service):
        """Test committing when there are no changes."""
        result = git_service.commit_changes("Test commit")
        
        assert isinstance(result, GitOperationResult)
        assert result.success is False
        assert "No changes to commit" in result.message

    @patch('services.git.git_service.GitService._add_token_to_url')
    @patch('services.git.git_service.Repo')
    def test_push_branch(self, mock_repo_class, mock_add_token, git_service):
        """Test pushing a branch to remote."""
        # Mock the remote operations
        with patch.object(git_service, '_get_git_config') as mock_config:
            mock_config.return_value = None

            # Create mock repo and remote
            mock_repo = MagicMock()
            mock_repo.active_branch.name = "test-branch"
            mock_remote = MagicMock()
            mock_remote.url = "https://github.com/test/repo.git"
            
            # Mock the remote('origin') call specifically
            mock_repo.remote.return_value = mock_remote
            
            # Set up the Repo constructor to return our mock
            mock_repo_class.return_value = mock_repo
            
            result = git_service.push_branch("test-token", "test-branch")
            
            assert isinstance(result, GitOperationResult)
            assert result.success is True
            assert "Successfully pushed branch" in result.message
            # Verify that remote('origin') was called
            mock_repo.remote.assert_called_with('origin')

    @pytest.mark.asyncio
    async def test_create_pull_request(self, git_service):
        """Test creating a pull request."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock the HTTP response
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "number": 123,
                "html_url": "https://github.com/test/repo/pull/123",
                "id": 456
            }
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await git_service.create_pull_request(
                github_repo="test/repo",
                oauth_token="test-token",
                head_branch="test-branch",
                title="Test PR"
            )
            
            assert isinstance(result, PullRequestResult)
            assert result.success is True
            assert result.pr_number == 123
            assert result.pr_url == "https://github.com/test/repo/pull/123"
            assert result.pr_id == 456

    def test_get_repo_status(self, git_service):
        """Test getting repository status."""
        result = git_service.get_repo_status()
        
        assert isinstance(result, RepoStatus)
        assert result.current_branch == "main"
        assert result.is_dirty is False
        assert isinstance(result.untracked_files, list)
        assert isinstance(result.modified_files, list)
        assert isinstance(result.staged_files, list)
        assert isinstance(result.commits_ahead, int)
        assert "hash" in result.last_commit
        assert "message" in result.last_commit
        assert "author" in result.last_commit
        assert "date" in result.last_commit

    def test_switch_branch(self, git_service):
        """Test switching to an existing branch."""
        # Create a branch first
        git_service.checkout_new_branch("switch-test")
        
        # Switch back to main
        git_service.switch_branch("main")
        
        # Switch to the test branch
        result = git_service.switch_branch("switch-test")
        
        assert isinstance(result, GitOperationResult)
        assert result.success is True
        assert "Switched to branch" in result.message

    @patch('services.git.git_service.GitService._add_token_to_url')
    @patch('services.git.git_service.Repo')
    def test_pull_latest(self, mock_repo_class, mock_add_token, git_service):
        """Test pulling latest changes."""
        with patch.object(git_service, '_get_git_config') as mock_config:
            mock_config.return_value = None

            # Create mock repo and remote
            mock_repo = MagicMock()
            mock_repo.active_branch.name = "main"
            mock_remote = MagicMock()
            mock_remote.url = "https://github.com/test/repo.git"
            
            # Mock the remote('origin') call specifically
            mock_repo.remote.return_value = mock_remote
            
            # Set up the Repo constructor to return our mock
            mock_repo_class.return_value = mock_repo
            
            result = git_service.pull_latest("test-token")
            
            assert isinstance(result, GitOperationResult)
            assert result.success is True
            assert "Pulled latest changes" in result.message
            # Verify that remote('origin') was called
            mock_repo.remote.assert_called_with('origin')

    def test_add_token_to_url(self):
        """Test adding OAuth token to GitHub URL."""
        service = GitService("/tmp")
        url = "https://github.com/test/repo.git"
        token = "test-token"
        
        result = service._add_token_to_url(url, token)
        
        assert result == "https://test-token@github.com/test/repo.git"

    def test_add_token_to_non_github_url(self):
        """Test adding OAuth token to non-GitHub URL."""
        service = GitService("/tmp")
        url = "https://example.com/test/repo.git"
        token = "test-token"
        
        result = service._add_token_to_url(url, token)
        
        assert result == url  # Should remain unchanged