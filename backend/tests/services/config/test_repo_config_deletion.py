"""
Test suite for repository configuration deletion.
Verifies that repos are deleted when removed from configuration.
"""
import pytest
from unittest.mock import Mock, MagicMock
from services.config.strategies.organization import OrganizationConfig
from services.config.models import RepoConfig
from database.models import UserRepos, RepoStatus


class TestRepoConfigDeletion:
    """Test repository configuration deletion functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def mock_user_repos_dao(self):
        """Create mock UserReposDAO."""
        return Mock()

    @pytest.fixture
    def org_config(self):
        """Create OrganizationConfig instance."""
        return OrganizationConfig()

    def test_set_repo_configs_deletes_removed_repos(
        self, org_config, mock_db, monkeypatch
    ):
        """Test that repos not in new config list are deleted."""
        user_id = "test-user"
        
        # Mock existing repos in database
        existing_repo_1 = UserRepos(
            id="repo-1",
            user_id=user_id,
            repo_clone_url="https://github.com/user/repo1",
            repo_name="user/repo1",
            branch="main",
            status=RepoStatus.CLONED
        )
        existing_repo_2 = UserRepos(
            id="repo-2",
            user_id=user_id,
            repo_clone_url="https://github.com/user/repo2",
            repo_name="user/repo2",
            branch="main",
            status=RepoStatus.CLONED
        )
        
        # Mock UserReposDAO
        mock_dao = Mock()
        mock_dao.get_user_repositories.return_value = [existing_repo_1, existing_repo_2]
        mock_dao.get_repository_by_url.return_value = existing_repo_1
        mock_dao.delete_repository.return_value = True
        
        # Patch UserReposDAO instantiation
        def mock_dao_init(db):
            return mock_dao
        
        monkeypatch.setattr(
            "services.config.strategies.organization.UserReposDAO",
            mock_dao_init
        )
        
        # New config only includes repo1 (repo2 should be deleted)
        new_configs = [
            RepoConfig(
                id="repo-1",
                repo_name="user/repo1",
                repo_url="https://github.com/user/repo1",
                base_branch="main"
            )
        ]
        
        # Execute
        result = org_config.set_repo_configs(
            db=mock_db,
            user_id=user_id,
            repo_configs=new_configs
        )
        
        # Verify repo2 was deleted
        mock_dao.delete_repository.assert_called_once_with("repo-2")
        
        # Verify result contains only repo1
        assert len(result) == 1
        assert result[0].repo_url == "https://github.com/user/repo1"

    def test_set_repo_configs_empty_list_deletes_all(
        self, org_config, mock_db, monkeypatch
    ):
        """Test that empty config list deletes all repos."""
        user_id = "test-user"
        
        # Mock existing repos
        existing_repo_1 = UserRepos(
            id="repo-1",
            user_id=user_id,
            repo_clone_url="https://github.com/user/repo1",
            repo_name="user/repo1",
            branch="main",
            status=RepoStatus.CLONED
        )
        existing_repo_2 = UserRepos(
            id="repo-2",
            user_id=user_id,
            repo_clone_url="https://github.com/user/repo2",
            repo_name="user/repo2",
            branch="main",
            status=RepoStatus.CLONED
        )
        
        # Mock UserReposDAO
        mock_dao = Mock()
        mock_dao.get_user_repositories.return_value = [existing_repo_1, existing_repo_2]
        mock_dao.delete_repository.return_value = True
        
        # Patch UserReposDAO
        def mock_dao_init(db):
            return mock_dao
        
        monkeypatch.setattr(
            "services.config.strategies.organization.UserReposDAO",
            mock_dao_init
        )
        
        # Execute with empty list
        result = org_config.set_repo_configs(
            db=mock_db,
            user_id=user_id,
            repo_configs=[]
        )
        
        # Verify both repos were deleted
        assert mock_dao.delete_repository.call_count == 2
        mock_dao.delete_repository.assert_any_call("repo-1")
        mock_dao.delete_repository.assert_any_call("repo-2")
        
        # Verify empty result
        assert result == []

    def test_set_repo_configs_keeps_existing_repos(
        self, org_config, mock_db, monkeypatch
    ):
        """Test that existing repos in new config are kept."""
        user_id = "test-user"
        
        # Mock existing repo
        existing_repo = UserRepos(
            id="repo-1",
            user_id=user_id,
            repo_clone_url="https://github.com/user/repo1",
            repo_name="user/repo1",
            branch="main",
            status=RepoStatus.CLONED
        )
        
        # Mock UserReposDAO
        mock_dao = Mock()
        mock_dao.get_user_repositories.return_value = [existing_repo]
        mock_dao.get_repository_by_url.return_value = existing_repo
        mock_dao.delete_repository.return_value = True
        
        # Patch UserReposDAO
        def mock_dao_init(db):
            return mock_dao
        
        monkeypatch.setattr(
            "services.config.strategies.organization.UserReposDAO",
            mock_dao_init
        )
        
        # New config includes the existing repo
        new_configs = [
            RepoConfig(
                id="repo-1",
                repo_name="user/repo1",
                repo_url="https://github.com/user/repo1",
                base_branch="main"
            )
        ]
        
        # Execute
        result = org_config.set_repo_configs(
            db=mock_db,
            user_id=user_id,
            repo_configs=new_configs
        )
        
        # Verify no deletions occurred
        mock_dao.delete_repository.assert_not_called()
        
        # Verify repo was kept
        assert len(result) == 1
        assert result[0].repo_url == "https://github.com/user/repo1"