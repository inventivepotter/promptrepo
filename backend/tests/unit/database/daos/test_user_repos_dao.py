"""
Unit tests for the UserReposDAO.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session
from datetime import datetime, UTC, timedelta

from database.daos.user.user_repos_dao import UserReposDAO
from database.models import UserRepos, RepoStatus
from database.models.user import User
from schemas.oauth_provider_enum import OAuthProvider


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Fixture to create a sample user for testing."""
    user = User(
        id=str(uuid4()),
        oauth_provider=OAuthProvider.GITHUB,
        oauth_username="testuser",
        oauth_email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_repos_dao(db_session: Session) -> UserReposDAO:
    """Fixture to create a UserReposDAO instance."""
    return UserReposDAO(db_session)


@pytest.fixture
def sample_repo_data(sample_user: User) -> dict:
    """Fixture to provide sample repository data."""
    return {
        "user_id": sample_user.id,
        "repo_clone_url": "https://github.com/testuser/repo1.git",
        "repo_name": "testuser/repo1",
        "branch": "main"
    }


def test_add_repository_success(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test successfully adding a new repository."""
    repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Verify the repository was created
    assert repo.id is not None
    assert repo.user_id == sample_repo_data["user_id"]
    assert repo.repo_clone_url == sample_repo_data["repo_clone_url"]
    assert repo.repo_name == sample_repo_data["repo_name"]
    assert repo.branch == sample_repo_data["branch"]
    assert repo.status == RepoStatus.PENDING
    assert isinstance(repo.created_at, datetime)
    assert isinstance(repo.updated_at, datetime)
    assert repo.local_path is None
    assert repo.last_clone_attempt is None
    assert repo.clone_error_message is None


def test_add_repository_already_exists(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test adding a repository that already exists for the user."""
    # Add the repository first time
    user_repos_dao.add_repository(**sample_repo_data)
    
    # Try to add the same repository again
    with pytest.raises(ValueError) as exc_info:
        user_repos_dao.add_repository(**sample_repo_data)
    
    assert "already exists" in str(exc_info.value)


def test_get_repository_by_id_found(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test retrieving a repository by ID when found."""
    # Create a repository first
    created_repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Retrieve the repository by ID
    retrieved_repo = user_repos_dao.get_repository_by_id(created_repo.id)
    
    # Verify the repository was retrieved correctly
    assert retrieved_repo is not None
    assert retrieved_repo.id == created_repo.id
    assert retrieved_repo.repo_name == created_repo.repo_name


def test_get_repository_by_id_not_found(user_repos_dao: UserReposDAO):
    """Test retrieving a repository by ID when not found."""
    non_existent_id = str(uuid4())
    retrieved_repo = user_repos_dao.get_repository_by_id(non_existent_id)
    
    assert retrieved_repo is None


def test_get_repository_by_url_found(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test retrieving a repository by user ID and clone URL when found."""
    # Create a repository first
    created_repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Retrieve the repository by URL
    retrieved_repo = user_repos_dao.get_repository_by_url(
        sample_repo_data["user_id"],
        sample_repo_data["repo_clone_url"]
    )
    
    # Verify the repository was retrieved correctly
    assert retrieved_repo is not None
    assert retrieved_repo.id == created_repo.id
    assert retrieved_repo.repo_clone_url == created_repo.repo_clone_url


def test_get_repository_by_url_not_found(user_repos_dao: UserReposDAO, sample_user: User):
    """Test retrieving a repository by user ID and clone URL when not found."""
    non_existent_url = "https://github.com/testuser/nonexistent.git"
    retrieved_repo = user_repos_dao.get_repository_by_url(sample_user.id, non_existent_url)
    
    assert retrieved_repo is None


def test_get_user_repositories(user_repos_dao: UserReposDAO, sample_repo_data: dict, sample_user: User):
    """Test retrieving all repositories for a user."""
    # Add multiple repositories for the user
    repo1 = user_repos_dao.add_repository(**sample_repo_data)
    
    repo2_data = sample_repo_data.copy()
    repo2_data["repo_clone_url"] = "https://github.com/testuser/repo2.git"
    repo2_data["repo_name"] = "testuser/repo2"
    repo2 = user_repos_dao.add_repository(**repo2_data)
    
    # Retrieve all repositories for the user
    user_repos = user_repos_dao.get_user_repositories(sample_user.id)
    
    # Verify all repositories were retrieved
    assert len(user_repos) == 2
    repo_names = [repo.repo_name for repo in user_repos]
    assert "testuser/repo1" in repo_names
    assert "testuser/repo2" in repo_names


def test_get_user_repositories_empty(user_repos_dao: UserReposDAO, sample_user: User):
    """Test retrieving repositories for a user with no repositories."""
    user_repos = user_repos_dao.get_user_repositories(sample_user.id)
    assert len(user_repos) == 0


def test_get_repositories_by_status_all_users(user_repos_dao: UserReposDAO, sample_repo_data: dict, sample_user: User):
    """Test retrieving repositories by status for all users."""
    # Add repositories with different statuses
    repo1 = user_repos_dao.add_repository(**sample_repo_data)
    user_repos_dao.update_repository_status(repo1.id, RepoStatus.CLONED, "/path/to/repo")
    
    repo2_data = sample_repo_data.copy()
    repo2_data["repo_clone_url"] = "https://github.com/testuser/repo2.git"
    repo2_data["repo_name"] = "testuser/repo2"
    repo2 = user_repos_dao.add_repository(**repo2_data)
    user_repos_dao.update_repository_status(repo2.id, RepoStatus.FAILED, error_message="Clone failed")
    
    # Get repositories with CLONED status
    cloned_repos = user_repos_dao.get_repositories_by_status(RepoStatus.CLONED)
    assert len(cloned_repos) == 1
    assert cloned_repos[0].status == RepoStatus.CLONED
    
    # Get repositories with FAILED status
    failed_repos = user_repos_dao.get_repositories_by_status(RepoStatus.FAILED)
    assert len(failed_repos) == 1
    assert failed_repos[0].status == RepoStatus.FAILED
    
    # Get repositories with PENDING status
    pending_repos = user_repos_dao.get_repositories_by_status(RepoStatus.PENDING)
    assert len(pending_repos) == 0


def test_get_repositories_by_status_specific_user(user_repos_dao: UserReposDAO, sample_repo_data: dict, sample_user: User):
    """Test retrieving repositories by status for a specific user."""
    # Create another user
    user2 = User(
        id=str(uuid4()),
        oauth_provider=OAuthProvider.GITHUB,
        oauth_username="user2",
        oauth_email="user2@example.com"
    )
    user_repos_dao.db.add(user2)
    user_repos_dao.db.commit()
    
    # Add repositories for both users
    repo1 = user_repos_dao.add_repository(**sample_repo_data)
    user_repos_dao.update_repository_status(repo1.id, RepoStatus.CLONED, "/path/to/repo")
    
    repo2_data = sample_repo_data.copy()
    repo2_data["user_id"] = user2.id
    repo2_data["repo_clone_url"] = "https://github.com/user2/repo.git"
    repo2_data["repo_name"] = "user2/repo"
    repo2 = user_repos_dao.add_repository(**repo2_data)
    user_repos_dao.update_repository_status(repo2.id, RepoStatus.CLONED, "/path/to/user2/repo")
    
    # Get CLONED repositories for the first user only
    user1_cloned = user_repos_dao.get_repositories_by_status(RepoStatus.CLONED, sample_user.id)
    assert len(user1_cloned) == 1
    assert user1_cloned[0].user_id == sample_user.id
    
    # Get all CLONED repositories
    all_cloned = user_repos_dao.get_repositories_by_status(RepoStatus.CLONED)
    assert len(all_cloned) == 2


def test_update_repository_status_to_cloning(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test updating repository status to CLONING."""
    # Create a repository
    repo = user_repos_dao.add_repository(**sample_repo_data)
    original_updated_at = repo.updated_at
    
    # Update status to CLONING
    updated_repo = user_repos_dao.update_repository_status(repo.id, RepoStatus.CLONING)
    
    # Verify the update
    assert updated_repo is not None
    assert updated_repo.status == RepoStatus.CLONING
    assert updated_repo.last_clone_attempt is not None
    assert updated_repo.clone_error_message is None
    assert updated_repo.updated_at > original_updated_at


def test_update_repository_status_to_cloned(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test updating repository status to CLONED."""
    # Create a repository
    repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Update status to CLONED with local path
    local_path = "/path/to/cloned/repo"
    updated_repo = user_repos_dao.update_repository_status(repo.id, RepoStatus.CLONED, local_path=local_path)
    
    # Verify the update
    assert updated_repo is not None
    assert updated_repo.status == RepoStatus.CLONED
    assert updated_repo.local_path == local_path
    assert updated_repo.clone_error_message is None


def test_update_repository_status_to_failed(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test updating repository status to FAILED."""
    # Create a repository
    repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Update status to FAILED with error message
    error_message = "Clone failed due to network error"
    updated_repo = user_repos_dao.update_repository_status(repo.id, RepoStatus.FAILED, error_message=error_message)
    
    # Verify the update
    assert updated_repo is not None
    assert updated_repo.status == RepoStatus.FAILED
    assert updated_repo.clone_error_message == error_message


def test_update_repository_status_not_found(user_repos_dao: UserReposDAO):
    """Test updating repository status for non-existent repository."""
    non_existent_id = str(uuid4())
    updated_repo = user_repos_dao.update_repository_status(non_existent_id, RepoStatus.CLONED, "/path/to/repo")
    
    assert updated_repo is None


def test_delete_repository_success(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test successfully deleting a repository."""
    # Create a repository
    repo = user_repos_dao.add_repository(**sample_repo_data)
    repo_id = repo.id
    
    # Delete the repository
    delete_result = user_repos_dao.delete_repository(repo_id)
    
    # Verify deletion was successful
    assert delete_result is True
    
    # Verify repository is no longer retrievable
    retrieved_repo = user_repos_dao.get_repository_by_id(repo_id)
    assert retrieved_repo is None


def test_delete_repository_not_found(user_repos_dao: UserReposDAO):
    """Test deleting a repository that doesn't exist."""
    non_existent_id = str(uuid4())
    delete_result = user_repos_dao.delete_repository(non_existent_id)
    
    assert delete_result is False


def test_get_pending_clones(user_repos_dao: UserReposDAO, sample_repo_data: dict, sample_user: User):
    """Test getting repositories with PENDING status."""
    # Add multiple repositories
    repo1 = user_repos_dao.add_repository(**sample_repo_data)  # PENDING by default
    
    repo2_data = sample_repo_data.copy()
    repo2_data["repo_clone_url"] = "https://github.com/testuser/repo2.git"
    repo2_data["repo_name"] = "testuser/repo2"
    repo2 = user_repos_dao.add_repository(**repo2_data)
    user_repos_dao.update_repository_status(repo2.id, RepoStatus.CLONED, "/path/to/repo2")
    
    repo3_data = sample_repo_data.copy()
    repo3_data["repo_clone_url"] = "https://github.com/testuser/repo3.git"
    repo3_data["repo_name"] = "testuser/repo3"
    repo3 = user_repos_dao.add_repository(**repo3_data)  # PENDING by default
    
    # Get all pending clones
    pending_clones = user_repos_dao.get_pending_clones()
    assert len(pending_clones) == 2
    assert all(repo.status == RepoStatus.PENDING for repo in pending_clones)
    
    # Get pending clones with limit
    limited_pending = user_repos_dao.get_pending_clones(limit=1)
    assert len(limited_pending) == 1


def test_count_repositories_by_status(user_repos_dao: UserReposDAO, sample_repo_data: dict, sample_user: User):
    """Test counting repositories by status for a user."""
    # Add repositories with different statuses
    repo1 = user_repos_dao.add_repository(**sample_repo_data)  # PENDING
    
    repo2_data = sample_repo_data.copy()
    repo2_data["repo_clone_url"] = "https://github.com/testuser/repo2.git"
    repo2_data["repo_name"] = "testuser/repo2"
    repo2 = user_repos_dao.add_repository(**repo2_data)
    user_repos_dao.update_repository_status(repo2.id, RepoStatus.CLONED, "/path/to/repo2")
    
    repo3_data = sample_repo_data.copy()
    repo3_data["repo_clone_url"] = "https://github.com/testuser/repo3.git"
    repo3_data["repo_name"] = "testuser/repo3"
    repo3 = user_repos_dao.add_repository(**repo3_data)
    user_repos_dao.update_repository_status(repo3.id, RepoStatus.FAILED, error_message="Failed")
    
    # Count repositories by status
    status_count = user_repos_dao.count_repositories_by_status(sample_user.id)
    
    # Verify counts
    assert status_count.status_counts[RepoStatus.PENDING] == 1
    assert status_count.status_counts[RepoStatus.CLONED] == 1
    assert status_count.status_counts[RepoStatus.FAILED] == 1
    assert status_count.status_counts[RepoStatus.CLONING] == 0
    assert status_count.status_counts[RepoStatus.OUTDATED] == 0


def test_count_repositories_by_status_empty(user_repos_dao: UserReposDAO, sample_user: User):
    """Test counting repositories by status for a user with no repositories."""
    status_count = user_repos_dao.count_repositories_by_status(sample_user.id)
    
    # Verify all counts are zero
    for status in RepoStatus:
        assert status_count.status_counts[status] == 0


def test_update_repository_path_success(user_repos_dao: UserReposDAO, sample_repo_data: dict):
    """Test successfully updating repository local path."""
    # Create a repository
    repo = user_repos_dao.add_repository(**sample_repo_data)
    original_updated_at = repo.updated_at
    
    # Update the local path
    new_path = "/new/path/to/repo"
    update_result = user_repos_dao.update_repository_path(repo.id, new_path)
    
    # Verify the update
    assert update_result is True
    
    # Verify the path was updated (repository should exist since update was successful)
    retrieved_repo = user_repos_dao.get_repository_by_id(repo.id)
    assert retrieved_repo is not None
    assert retrieved_repo.local_path == new_path
    assert retrieved_repo.updated_at > original_updated_at


def test_update_repository_path_not_found(user_repos_dao: UserReposDAO):
    """Test updating repository path for non-existent repository."""
    non_existent_id = str(uuid4())
    update_result = user_repos_dao.update_repository_path(non_existent_id, "/some/path")
    
    assert update_result is False


def test_add_repository_exception_handling(user_repos_dao: UserReposDAO, sample_repo_data: dict, mocker):
    """Test exception handling when adding a repository fails."""
    # Mock the database session to raise an exception during add
    mocker.patch.object(user_repos_dao.db, 'add', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_repos_dao.add_repository(**sample_repo_data)
    
    assert "Database error" in str(exc_info.value)


def test_update_repository_status_exception_handling(user_repos_dao: UserReposDAO, sample_repo_data: dict, mocker):
    """Test exception handling when updating repository status fails."""
    # Create a repository first
    repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Mock the database session to raise an exception during commit
    mocker.patch.object(user_repos_dao.db, 'commit', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_repos_dao.update_repository_status(repo.id, RepoStatus.CLONED, "/path/to/repo")
    
    assert "Database error" in str(exc_info.value)


def test_delete_repository_exception_handling(user_repos_dao: UserReposDAO, sample_repo_data: dict, mocker):
    """Test exception handling when deleting a repository fails."""
    # Create a repository first
    repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Mock the database session to raise an exception during delete
    mocker.patch.object(user_repos_dao.db, 'delete', side_effect=Exception("Database error"))
    
    # This should return False due to exception handling in the method
    delete_result = user_repos_dao.delete_repository(repo.id)
    assert delete_result is False


def test_update_repository_path_exception_handling(user_repos_dao: UserReposDAO, sample_repo_data: dict, mocker):
    """Test exception handling when updating repository path fails."""
    # Create a repository first
    repo = user_repos_dao.add_repository(**sample_repo_data)
    
    # Mock the database session to raise an exception during commit
    mocker.patch.object(user_repos_dao.db, 'commit', side_effect=Exception("Database error"))
    
    # This should return False due to exception handling in the method
    update_result = user_repos_dao.update_repository_path(repo.id, "/new/path")
    assert update_result is False