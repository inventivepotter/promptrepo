"""
Test suite for UserRepos model
"""
import pytest
from datetime import datetime, UTC
from uuid import uuid4
from sqlmodel import SQLModel, Session

from models.user_repos import UserRepos, RepoStatus
from database.models.user import User


class TestUserReposModel:
    """Test cases for UserRepos model"""
    
    def test_repository_creation(self, db_session: Session):
        """Test creating a repository"""
        # First create a user
        user_id = str(uuid4())
        user = User(id=user_id, username="repo_test_user")
        db_session.add(user)
        db_session.commit()
        
        # Create repository
        repo = UserRepos(
            user_id=user_id,
            repo_clone_url="https://github.com/user/repo.git",
            repo_name="user/repo",
            branch="main"
        )
        
        db_session.add(repo)
        db_session.commit()
        
        assert repo.status == RepoStatus.PENDING
        assert repo.branch == "main"
        assert repo.local_path is None
    
    def test_repository_status_transitions(self):
        """Test repository status transition methods"""
        repo = UserRepos(
            user_id=str(uuid4()),
            repo_clone_url="https://github.com/test/repo.git",
            repo_name="test/repo"
        )
        
        # Initial state
        assert repo.is_clone_pending() is True
        assert repo.is_cloned_successfully() is False
        assert repo.is_clone_failed() is False
        
        # Mark as cloning
        repo.mark_as_cloning()
        assert repo.status == RepoStatus.CLONING
        assert repo.last_clone_attempt is not None
        
        # Mark as cloned
        repo.mark_as_cloned("/path/to/repo")
        assert repo.status == RepoStatus.CLONED
        assert repo.local_path == "/path/to/repo"
        assert repo.is_cloned_successfully() is True
        
        # Mark as failed
        repo.mark_as_failed("Clone failed: timeout")
        assert repo.status == RepoStatus.FAILED
        assert repo.clone_error_message == "Clone failed: timeout"
        assert repo.is_clone_failed() is True
        
        # Mark as outdated
        repo.mark_as_outdated()
        assert repo.status == RepoStatus.OUTDATED
    
    def test_repo_status_enum(self):
        """Test RepoStatus enum values"""
        assert RepoStatus.PENDING.value == "pending"
        assert RepoStatus.CLONING.value == "cloning"
        assert RepoStatus.CLONED.value == "cloned"
        assert RepoStatus.FAILED.value == "failed"
        assert RepoStatus.OUTDATED.value == "outdated"