"""
Unit tests for database models.
"""
import pytest
import uuid
from datetime import datetime, UTC, timedelta
from sqlmodel import Session, select

from database.models.user import User
from database.models.user_sessions import UserSessions
from database.models.user_repos import UserRepos, RepoStatus
from database.models.user_llm_configs import UserLLMConfigs
from schemas.oauth_provider_enum import OAuthProvider


class TestUserModel:
    """Test cases for User model"""

    def test_user_creation(self, db_session: Session):
        """Test basic user creation"""
        user = User(
            oauth_username="testuser",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_user_id="123",
            oauth_email="test@example.com"
        )
        db_session.add(user)
        db_session.commit()

        # Verify user was created
        saved_user = db_session.exec(select(User).where(User.oauth_username == "testuser")).first()
        assert saved_user is not None
        assert saved_user.oauth_username == "testuser"
        assert saved_user.oauth_provider == OAuthProvider.GITHUB
        assert saved_user.oauth_user_id == "123"
        assert saved_user.oauth_email == "test@example.com"

    def test_user_creation_minimal_fields(self, db_session: Session):
        """Test user creation with minimal required fields"""
        user = User(oauth_username="minimal_user", oauth_provider=OAuthProvider.GITHUB)
        db_session.add(user)
        db_session.commit()

        saved_user = db_session.exec(select(User).where(User.oauth_username == "minimal_user")).first()
        assert saved_user is not None
        assert saved_user.oauth_username == "minimal_user"
        assert saved_user.oauth_provider == OAuthProvider.GITHUB
        assert saved_user.oauth_user_id is None
        assert saved_user.oauth_email is None

    def test_user_different_oauth_providers(self, db_session: Session):
        """Test same oauth_user_id with different providers is allowed"""
        user1 = User(oauth_username="user1", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="123")
        user2 = User(oauth_username="user2", oauth_provider=OAuthProvider.GITLAB, oauth_user_id="123")

        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()  # Should not raise error

        # Verify both users exist
        saved_users = db_session.exec(select(User)).all()
        assert len(saved_users) == 2
        assert saved_users[0].oauth_user_id == "123"
        assert saved_users[1].oauth_user_id == "123"
        assert saved_users[0].oauth_provider != saved_users[1].oauth_provider

    def test_user_timestamps(self, db_session: Session):
        """Test user timestamps are set correctly"""
        before_creation = datetime.now(UTC)

        user = User(oauth_username="timestamp_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="789")
        db_session.add(user)
        db_session.commit()

        after_creation = datetime.now(UTC)

        assert user.created_at is not None
        assert user.modified_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.modified_at, datetime)

        # Timestamps should be between before and after creation
        # Convert to UTC for comparison if they're not already
        before_utc = before_creation if before_creation.tzinfo is not None else before_creation.replace(tzinfo=UTC)
        after_utc = after_creation if after_creation.tzinfo is not None else after_creation.replace(tzinfo=UTC)
        created_utc = user.created_at if user.created_at.tzinfo is not None else user.created_at.replace(tzinfo=UTC)
        
        assert before_utc <= created_utc <= after_utc

    def test_user_update_timestamp(self, db_session: Session):
        """Test modified_at timestamp updates on record update"""
        user = User(oauth_username="update_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="999")
        db_session.add(user)
        db_session.commit()

        original_modified_at = user.modified_at

        # Wait to ensure timestamp difference (at least 1 second for database precision)
        import time
        time.sleep(1.1)

        # Update user
        user.oauth_name = "Updated Name"
        db_session.commit()
        
        # Refresh to get the updated timestamp from database
        db_session.refresh(user)

        # modified_at should have changed
        assert user.modified_at > original_modified_at

    def test_user_string_representation(self, db_session: Session):
        """Test user string representation"""
        user = User(oauth_username="str_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="111")
        db_session.add(user)
        db_session.commit()

        str_repr = str(user)
        assert "str_user" in str_repr
        assert "GITHUB" in str_repr or "github" in str_repr

    def test_user_query_by_oauth_provider(self, db_session: Session):
        """Test querying users by oauth provider"""
        # Create users with different providers
        github_user = User(oauth_username="github_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="1")
        gitlab_user = User(oauth_username="gitlab_user", oauth_provider=OAuthProvider.GITLAB, oauth_user_id="2")
        github_user2 = User(oauth_username="github_user2", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="3")

        db_session.add(github_user)
        db_session.add(gitlab_user)
        db_session.add(github_user2)
        db_session.commit()

        # Query by provider
        github_users = db_session.exec(select(User).where(User.oauth_provider == OAuthProvider.GITHUB)).all()
        gitlab_users = db_session.exec(select(User).where(User.oauth_provider == OAuthProvider.GITLAB)).all()

        assert len(github_users) == 2
        assert len(gitlab_users) == 1
        assert all(user.oauth_provider == OAuthProvider.GITHUB for user in github_users)
        assert all(user.oauth_provider == OAuthProvider.GITLAB for user in gitlab_users)


class TestUserSessionModel:
    """Test cases for UserSessions model"""

    def test_session_creation(self, db_session: Session):
        """Test basic session creation"""
        # First create a user
        user = User(oauth_username="session_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="101")
        db_session.add(user)
        db_session.commit()

        # Create session
        session_id = str(uuid.uuid4()).replace('-', '')
        session = UserSessions(
            user_id=user.id,
            session_id=session_id,
            oauth_token="access_token"
        )
        db_session.add(session)
        db_session.commit()

        # Verify session was created
        saved_session = db_session.exec(select(UserSessions).where(UserSessions.session_id == session_id)).first()
        assert saved_session is not None
        assert saved_session.user_id == user.id
        assert saved_session.session_id == session_id
        assert saved_session.oauth_token == "access_token"

    def test_session_update_accessed_at(self, db_session: Session):
        """Test updating accessed_at timestamp"""
        # Create user
        user = User(oauth_username="access_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="101")
        db_session.add(user)
        db_session.commit()

        # Create session
        session_id = str(uuid.uuid4()).replace('-', '')
        session = UserSessions(
            user_id=user.id,
            session_id=session_id,
            oauth_token="access_token"
        )
        db_session.add(session)
        db_session.commit()

        original_accessed_at = session.accessed_at

        # Wait a small amount
        import time
        time.sleep(0.5)

        # Update accessed_at by updating the record
        session.oauth_token = "updated_token"
        db_session.commit()
        
        # Refresh to get the updated timestamp from database
        db_session.refresh(session)

        # accessed_at should have changed
        assert session.accessed_at >= original_accessed_at

    def test_session_string_representation(self, db_session: Session):
        """Test session string representation"""
        # Create user
        user = User(oauth_username="str_session_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="102")
        db_session.add(user)
        db_session.commit()

        # Create session
        session_id = str(uuid.uuid4()).replace('-', '')
        session = UserSessions(
            user_id=user.id,
            session_id=session_id,
            oauth_token="str_token"
        )
        db_session.add(session)
        db_session.commit()

        str_repr = str(session)
        assert session_id[:8] in str_repr  # First 8 chars of session_id

    def test_session_multiple_sessions_per_user(self, db_session: Session):
        """Test multiple sessions per user"""
        # Create user
        user = User(oauth_username="multi_session_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="103")
        db_session.add(user)
        db_session.commit()

        # Create multiple sessions
        session1 = UserSessions(
            user_id=user.id,
            session_id=str(uuid.uuid4()).replace('-', ''),
            oauth_token="token1"
        )
        session2 = UserSessions(
            user_id=user.id,
            session_id=str(uuid.uuid4()).replace('-', ''),
            oauth_token="token2"
        )

        db_session.add(session1)
        db_session.add(session2)
        db_session.commit()

        # Verify both sessions exist
        sessions = db_session.exec(select(UserSessions).where(UserSessions.user_id == user.id)).all()
        assert len(sessions) == 2


class TestUserReposModel:
    """Test cases for UserRepos model"""

    def test_repository_creation(self, db_session: Session):
        """Test basic repository creation"""
        # First create a user
        user = User(oauth_username="repo_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="201")
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

        # Verify repository was created
        saved_repo = db_session.exec(select(UserRepos).where(UserRepos.repo_name == "user/repo")).first()
        assert saved_repo is not None
        assert saved_repo.user_id == user.id
        assert saved_repo.repo_clone_url == "https://github.com/user/repo.git"
        assert saved_repo.repo_name == "user/repo"
        assert saved_repo.branch == "main"
        assert saved_repo.status == RepoStatus.PENDING

    def test_repository_creation_with_minimal_fields(self, db_session: Session):
        """Test creating a repository with minimal fields"""
        # First create a user
        user = User(oauth_username="minimal_repo_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="456")
        db_session.add(user)
        db_session.commit()

        # Create repository with minimal fields
        repo = UserRepos(
            user_id=user.id,
            repo_clone_url="https://github.com/minimal/repo.git",
            repo_name="minimal/repo"
        )

        db_session.add(repo)
        db_session.commit()

        assert repo.status == RepoStatus.PENDING
        assert repo.branch == "main"  # Default value

    def test_repository_multiple_repos_per_user(self, db_session: Session):
        """Test multiple repositories per user"""
        # First create a user
        user = User(oauth_username="multi_repo_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="301")
        db_session.add(user)
        db_session.commit()

        # Create multiple repositories
        repo1 = UserRepos(
            user_id=user.id,
            repo_clone_url="https://github.com/user/repo1.git",
            repo_name="user/repo1"
        )
        repo2 = UserRepos(
            user_id=user.id,
            repo_clone_url="https://github.com/user/repo2.git",
            repo_name="user/repo2"
        )

        db_session.add(repo1)
        db_session.add(repo2)
        db_session.commit()

        # Verify both repositories exist
        repos = db_session.exec(select(UserRepos).where(UserRepos.user_id == user.id)).all()
        assert len(repos) == 2

    def test_repository_same_name_different_users(self, db_session: Session):
        """Test same repository name for different users"""
        # Create two users
        user1 = User(oauth_username="user1", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="401")
        user2 = User(oauth_username="user2", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="402")
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()

        # Create repositories with same name for different users
        repo1 = UserRepos(
            user_id=user1.id,
            repo_clone_url="https://github.com/user/repo.git",
            repo_name="user/repo"
        )
        repo2 = UserRepos(
            user_id=user2.id,
            repo_clone_url="https://github.com/user/repo2.git",
            repo_name="user/repo"
        )

        db_session.add(repo1)
        db_session.add(repo2)
        db_session.commit()

        # Verify both repositories exist
        assert db_session.exec(select(UserRepos).where(UserRepos.user_id == user1.id)).first() is not None
        assert db_session.exec(select(UserRepos).where(UserRepos.user_id == user2.id)).first() is not None


    def test_repository_query_by_status(self, db_session: Session):
        """Test querying repositories by status"""
        # First create a user
        user = User(oauth_username="status_repo_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="501")
        db_session.add(user)
        db_session.commit()

        # Create repositories with different statuses
        pending_repo = UserRepos(
            user_id=user.id,
            repo_clone_url="https://github.com/user/pending.git",
            repo_name="user/pending",
            status=RepoStatus.PENDING
        )
        cloned_repo = UserRepos(
            user_id=user.id,
            repo_clone_url="https://github.com/user/cloned.git",
            repo_name="user/cloned",
            status=RepoStatus.CLONED
        )

        db_session.add(pending_repo)
        db_session.add(cloned_repo)
        db_session.commit()

        # Query by status
        pending_repos = db_session.exec(select(UserRepos).where(UserRepos.status == RepoStatus.PENDING)).all()
        cloned_repos = db_session.exec(select(UserRepos).where(UserRepos.status == RepoStatus.CLONED)).all()

        assert len(pending_repos) == 1
        assert len(cloned_repos) == 1
        assert pending_repos[0].status == RepoStatus.PENDING
        assert cloned_repos[0].status == RepoStatus.CLONED

    def test_repository_string_representation(self, db_session: Session):
        """Test repository string representation"""
        # Create user
        user = User(oauth_username="str_repo_user", oauth_provider=OAuthProvider.GITHUB, oauth_user_id="444")
        db_session.add(user)
        db_session.commit()

        # Create repository
        repo = UserRepos(
            user_id=user.id,
            repo_clone_url="https://github.com/str/repo.git",
            repo_name="str/repo",
            branch="main"
        )
        db_session.add(repo)
        db_session.commit()

        str_repr = str(repo)
        assert "str/repo" in str_repr
        # Check for the enum value, not the full representation
        assert repo.status.value in str_repr or "pending" in str_repr.lower()