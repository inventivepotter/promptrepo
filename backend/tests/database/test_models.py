"""
Test suite for database models
Tests User, UserSession, and UserRepository models
"""
import pytest
from datetime import datetime, UTC, timedelta
from models import User, UserSessions, UserRepos, RepoStatus


class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self, db_session):
        """Test creating a user"""
        user = User(
            username="testuser",
            name="Test User",
            email="test@example.com",
            github_id=12345,
            avatar_url="https://avatar.url",
            html_url="https://github.com/testuser"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        saved_user = db_session.query(User).filter_by(username="testuser").first()
        assert saved_user is not None
        assert saved_user.username == "testuser"
        assert saved_user.name == "Test User"
        assert saved_user.email == "test@example.com"
        assert saved_user.github_id == 12345
    
    def test_user_unique_username(self, db_session):
        """Test username uniqueness constraint"""
        user1 = User(username="unique_user")
        user2 = User(username="unique_user")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_timestamps(self, db_session):
        """Test user timestamps are set correctly"""
        user = User(username="timestamp_user")
        
        db_session.add(user)
        db_session.commit()
        
        assert user.created_at is not None
        assert user.modified_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.modified_at, datetime)


class TestUserSessionModel:
    """Test cases for UserSession model"""
    
    def test_session_creation(self, db_session):
        """Test creating a session"""
        # First create a user
        user = User(username="session_test_user")
        db_session.add(user)
        db_session.commit()
        
        # Create session
        session = UserSessions(
            username=user.username,
            session_id=UserSessions.generate_session_key(),
            oauth_token="test_token_123"
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.session_id is not None
        assert len(session.session_id) == 32  # UUID without dashes
        assert session.oauth_token == "test_token_123"
    
    def test_session_key_generation(self):
        """Test session key generation"""
        key1 = UserSessions.generate_session_key()
        key2 = UserSessions.generate_session_key()
        
        assert key1 != key2  # Should be unique
        assert len(key1) == 32
        assert len(key2) == 32
        assert "-" not in key1  # No dashes
        assert "-" not in key2
    
    def test_session_expiration(self):
        """Test session expiration checking"""
        session = UserSessions(
            username="test_user_id", # Changed from user_id to username
            session_id=UserSessions.generate_session_key(), # Added session_id
            oauth_token="token"
        )
        
        # New session should not be expired
        assert session.is_expired(3600) is False
        
        # Manually set old accessed_at
        session.accessed_at = datetime.now(UTC) - timedelta(hours=2)
        
        # Should be expired for 1 hour TTL
        assert session.is_expired(3600) is True
        
        # Should not be expired for 3 hour TTL
        assert session.is_expired(10800) is False


class TestUserReposModel:
    """Test cases for UserRepos model"""
    
    def test_repository_creation(self, db_session):
        """Test creating a repository"""
        # First create a user
        user = User(username="repo_test_user")
        db_session.add(user)
        db_session.commit()
        
        # Create repository
        repo = UserRepos(
            user_id=user.id,
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
            user_id="test_user_id",
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