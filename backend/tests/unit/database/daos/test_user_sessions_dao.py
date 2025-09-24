"""
Unit tests for the UserSessionDAO.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session
from datetime import datetime, timedelta, UTC

from database.daos.user.user_sessions_dao import UserSessionDAO
from database.models.user_sessions import UserSessions
from database.models.user import User


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Fixture to create a sample user for testing."""
    user = User(
        id=str(uuid4()),
        oauth_provider="github",
        oauth_username="testuser",
        oauth_email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_session_dao(db_session: Session) -> UserSessionDAO:
    """Fixture to create a UserSessionDAO instance."""
    return UserSessionDAO(db_session)


@pytest.fixture
def sample_session_data(sample_user: User) -> dict:
    """Fixture to provide sample session data."""
    return {
        "user_id": sample_user.id,
        "oauth_token": "gho_testtoken123456789",
        "session_data": '{"device": "desktop", "ip": "192.168.1.1"}'
    }


def test_create_session_success(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test successfully creating a new session."""
    session = user_session_dao.create_session(**sample_session_data)
    
    # Verify the session was created
    assert session.id is not None
    assert session.user_id == sample_session_data["user_id"]
    assert session.oauth_token == sample_session_data["oauth_token"]
    assert session.session_id is not None
    assert len(session.session_id) == 32  # UUID without dashes
    assert session.data == sample_session_data["session_data"]
    assert isinstance(session.created_at, datetime)
    assert isinstance(session.accessed_at, datetime)


def test_create_session_without_data(user_session_dao: UserSessionDAO, sample_user: User):
    """Test creating a session without optional session data."""
    session = user_session_dao.create_session(
        user_id=sample_user.id,
        oauth_token="gho_testtoken123456789"
    )
    
    # Verify the session was created
    assert session.id is not None
    assert session.user_id == sample_user.id
    assert session.oauth_token == "gho_testtoken123456789"
    assert session.session_id is not None
    assert session.data is None


def test_generate_session_key(user_session_dao: UserSessionDAO):
    """Test session key generation."""
    key1 = user_session_dao.generate_session_key()
    key2 = user_session_dao.generate_session_key()
    
    # Verify keys are 32 characters long (UUID without dashes)
    assert len(key1) == 32
    assert len(key2) == 32
    
    # Verify keys are unique
    assert key1 != key2
    
    # Verify keys contain only hexadecimal characters
    assert all(c in '0123456789abcdef' for c in key1)


def test_get_session_by_id_found(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test retrieving a session by session_id when found."""
    # Create a session first
    created_session = user_session_dao.create_session(**sample_session_data)
    
    # Retrieve the session by ID
    retrieved_session = user_session_dao.get_session_by_id(created_session.session_id)
    
    # Verify the session was retrieved correctly
    assert retrieved_session is not None
    assert retrieved_session.session_id == created_session.session_id
    assert retrieved_session.user_id == created_session.user_id
    assert retrieved_session.oauth_token == created_session.oauth_token


def test_get_session_by_id_not_found(user_session_dao: UserSessionDAO):
    """Test retrieving a session by session_id when not found."""
    non_existent_id = "nonexistentsessionid123456789"
    retrieved_session = user_session_dao.get_session_by_id(non_existent_id)
    
    assert retrieved_session is None


def test_get_sessions_by_user_id(user_session_dao: UserSessionDAO, sample_session_data: dict, sample_user: User):
    """Test retrieving all sessions for a user."""
    # Create multiple sessions for the user
    session1 = user_session_dao.create_session(**sample_session_data)
    
    session2_data = sample_session_data.copy()
    session2_data["oauth_token"] = "gho_testtoken987654321"
    session2 = user_session_dao.create_session(**session2_data)
    
    # Retrieve all sessions for the user
    user_sessions = user_session_dao.get_sessions_by_user_id(sample_user.id)
    
    # Verify all sessions were retrieved
    assert len(user_sessions) == 2
    session_ids = [session.session_id for session in user_sessions]
    assert session1.session_id in session_ids
    assert session2.session_id in session_ids


def test_get_sessions_by_user_id_empty(user_session_dao: UserSessionDAO, sample_user: User):
    """Test retrieving sessions for a user with no sessions."""
    user_sessions = user_session_dao.get_sessions_by_user_id(sample_user.id)
    assert len(user_sessions) == 0


def test_update_session_success(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test successfully updating a session."""
    # Create a session first
    created_session = user_session_dao.create_session(**sample_session_data)
    original_accessed_at = created_session.accessed_at
    
    # Update the session
    update_result = user_session_dao.update_session(
        session_id=created_session.session_id,
        oauth_token="gho_newtoken123456789",
        session_data='{"device": "mobile", "ip": "192.168.1.2"}'
    )
    
    # Verify the update was successful
    assert update_result is True
    
    # Verify the session was updated
    retrieved_session = user_session_dao.get_session_by_id(created_session.session_id)
    assert retrieved_session is not None
    assert retrieved_session.oauth_token == "gho_newtoken123456789"
    assert retrieved_session.data == '{"device": "mobile", "ip": "192.168.1.2"}'
    assert retrieved_session.accessed_at > original_accessed_at


def test_update_session_partial(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test updating only some fields of a session."""
    # Create a session first
    created_session = user_session_dao.create_session(**sample_session_data)
    original_token = created_session.oauth_token
    original_data = created_session.data
    
    # Update only the oauth token
    update_result = user_session_dao.update_session(
        session_id=created_session.session_id,
        oauth_token="gho_newtoken123456789"
    )
    
    # Verify the update was successful
    assert update_result is True
    
    # Verify only the token was updated
    retrieved_session = user_session_dao.get_session_by_id(created_session.session_id)
    assert retrieved_session is not None
    assert retrieved_session.oauth_token == "gho_newtoken123456789"
    assert retrieved_session.data == original_data  # Should be unchanged


def test_update_session_not_found(user_session_dao: UserSessionDAO):
    """Test updating a session that doesn't exist."""
    non_existent_id = "nonexistentsessionid123456789"
    update_result = user_session_dao.update_session(
        session_id=non_existent_id,
        oauth_token="gho_newtoken123456789"
    )
    
    assert update_result is False


def test_delete_session_success(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test successfully deleting a session."""
    # Create a session first
    created_session = user_session_dao.create_session(**sample_session_data)
    session_id = created_session.session_id
    
    # Delete the session
    delete_result = user_session_dao.delete_session(session_id)
    
    # Verify deletion was successful
    assert delete_result is True
    
    # Verify session is no longer retrievable
    retrieved_session = user_session_dao.get_session_by_id(session_id)
    assert retrieved_session is None


def test_delete_session_not_found(user_session_dao: UserSessionDAO):
    """Test deleting a session that doesn't exist."""
    non_existent_id = "nonexistentsessionid123456789"
    delete_result = user_session_dao.delete_session(non_existent_id)
    
    assert delete_result is False


def test_delete_user_sessions_success(user_session_dao: UserSessionDAO, sample_session_data: dict, sample_user: User):
    """Test successfully deleting all sessions for a user."""
    # Create multiple sessions for the user
    session1 = user_session_dao.create_session(**sample_session_data)
    session2 = user_session_dao.create_session(
        user_id=sample_user.id,
        oauth_token="gho_testtoken987654321"
    )
    
    # Delete all sessions for the user
    deleted_count = user_session_dao.delete_user_sessions(sample_user.id)
    
    # Verify the correct number of sessions were deleted
    assert deleted_count == 2
    
    # Verify all sessions are gone
    user_sessions = user_session_dao.get_sessions_by_user_id(sample_user.id)
    assert len(user_sessions) == 0


def test_delete_user_sessions_no_sessions(user_session_dao: UserSessionDAO, sample_user: User):
    """Test deleting sessions for a user with no sessions."""
    deleted_count = user_session_dao.delete_user_sessions(sample_user.id)
    assert deleted_count == 0


def test_get_active_session(user_session_dao: UserSessionDAO, sample_session_data: dict, sample_user: User):
    """Test getting the most recently accessed session for a user."""
    # Create multiple sessions with different access times
    session1 = user_session_dao.create_session(**sample_session_data)
    
    # Wait a tiny bit to ensure different timestamps
    import time
    time.sleep(0.01)
    
    session2_data = sample_session_data.copy()
    session2_data["oauth_token"] = "gho_testtoken987654321"
    session2 = user_session_dao.create_session(**session2_data)
    
    # Access session2 to make it the most recently accessed
    user_session_dao.update_session(session2.session_id, oauth_token="gho_testtoken987654321")
    
    # Get the active session
    active_session = user_session_dao.get_active_session(sample_user.id)
    
    # Verify it's the most recently accessed session
    assert active_session is not None
    assert active_session.session_id == session2.session_id


def test_get_active_session_no_sessions(user_session_dao: UserSessionDAO, sample_user: User):
    """Test getting active session for a user with no sessions."""
    active_session = user_session_dao.get_active_session(sample_user.id)
    assert active_session is None


def test_delete_expired_sessions(user_session_dao: UserSessionDAO, sample_session_data: dict, sample_user: User):
    """Test deleting expired sessions."""
    # Create a session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Manually set the accessed_at to be older than the TTL
    old_time = datetime.now(UTC) - timedelta(hours=25)
    session.accessed_at = old_time
    user_session_dao.db.add(session)
    user_session_dao.db.commit()
    
    # Create another recent session
    recent_session_data = sample_session_data.copy()
    recent_session_data["oauth_token"] = "gho_recenttoken123456789"
    recent_session = user_session_dao.create_session(**recent_session_data)
    
    # Delete sessions older than 24 hours
    ttl = timedelta(hours=24)
    deleted_count = user_session_dao.delete_expired(ttl)
    
    # Verify only the expired session was deleted
    assert deleted_count == 1
    
    # Verify the expired session is gone
    expired_session = user_session_dao.get_session_by_id(session.session_id)
    assert expired_session is None
    
    # Verify the recent session still exists
    existing_session = user_session_dao.get_session_by_id(recent_session.session_id)
    assert existing_session is not None


def test_delete_expired_no_expired_sessions(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test deleting expired sessions when none are expired."""
    # Create a recent session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Delete sessions older than 24 hours
    ttl = timedelta(hours=24)
    deleted_count = user_session_dao.delete_expired(ttl)
    
    # Verify no sessions were deleted
    assert deleted_count == 0
    
    # Verify the session still exists
    existing_session = user_session_dao.get_session_by_id(session.session_id)
    assert existing_session is not None


def test_is_expired_true(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test checking if a session is expired when it is."""
    # Create a session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Manually set the accessed_at to be older than the TTL
    old_time = datetime.now(UTC) - timedelta(seconds=3600)  # 1 hour ago
    session.accessed_at = old_time
    user_session_dao.db.add(session)
    user_session_dao.db.commit()
    
    # Check if expired with TTL of 30 minutes
    is_expired = user_session_dao.is_expired(session, 1800)  # 30 minutes in seconds
    
    assert is_expired is True


def test_is_expired_false(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test checking if a session is expired when it's not."""
    # Create a session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Check if expired with TTL of 1 hour
    is_expired = user_session_dao.is_expired(session, 3600)  # 1 hour in seconds
    
    assert is_expired is False


def test_is_expired_with_naive_datetime(user_session_dao: UserSessionDAO, sample_session_data: dict):
    """Test checking expiration with a naive datetime (no timezone)."""
    # Create a session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Manually set the accessed_at to a naive datetime (older than TTL)
    old_time = datetime.now(UTC) - timedelta(seconds=3600)  # 1 hour ago
    session.accessed_at = old_time.replace(tzinfo=None)  # Make it naive
    user_session_dao.db.add(session)
    user_session_dao.db.commit()
    
    # Check if expired with TTL of 30 minutes
    is_expired = user_session_dao.is_expired(session, 1800)  # 30 minutes in seconds
    
    assert is_expired is True


def test_create_session_exception_handling(user_session_dao: UserSessionDAO, sample_session_data: dict, mocker):
    """Test exception handling when creating a session fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_session_dao.db, 'add', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_session_dao.create_session(**sample_session_data)
    
    assert "Database error" in str(exc_info.value)


def test_update_session_exception_handling(user_session_dao: UserSessionDAO, sample_session_data: dict, mocker):
    """Test exception handling when updating a session fails."""
    # Create a session first
    session = user_session_dao.create_session(**sample_session_data)
    
    # Mock the database session to raise an exception during commit
    mocker.patch.object(user_session_dao.db, 'commit', side_effect=Exception("Database error"))
    
    # This should return False due to exception handling in the method
    update_result = user_session_dao.update_session(session.session_id, oauth_token="new_token")
    assert update_result is False


def test_delete_session_exception_handling(user_session_dao: UserSessionDAO, sample_session_data: dict, mocker):
    """Test exception handling when deleting a session fails."""
    # Create a session first
    session = user_session_dao.create_session(**sample_session_data)
    
    # Mock the database session to raise an exception during delete
    mocker.patch.object(user_session_dao.db, 'delete', side_effect=Exception("Database error"))
    
    # This should return False due to exception handling in the method
    delete_result = user_session_dao.delete_session(session.session_id)
    assert delete_result is False


def test_delete_user_sessions_exception_handling(user_session_dao: UserSessionDAO, sample_session_data: dict, mocker):
    """Test exception handling when deleting user sessions fails."""
    # Create a session first
    session = user_session_dao.create_session(**sample_session_data)
    
    # Mock the database session to raise an exception during delete
    mocker.patch.object(user_session_dao.db, 'delete', side_effect=Exception("Database error"))
    
    # This should return 0 due to exception handling in the method
    deleted_count = user_session_dao.delete_user_sessions(session.user_id)
    assert deleted_count == 0


def test_delete_expired_exception_handling(user_session_dao: UserSessionDAO, sample_session_data: dict, mocker):
    """Test exception handling when deleting expired sessions fails."""
    # Create a session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Manually set the accessed_at to be old
    old_time = datetime.now(UTC) - timedelta(hours=25)
    session.accessed_at = old_time
    user_session_dao.db.add(session)
    user_session_dao.db.commit()
    
    # Mock the database session to raise an exception during delete
    mocker.patch.object(user_session_dao.db, 'delete', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_session_dao.delete_expired(timedelta(hours=24))
    
    assert "Database error" in str(exc_info.value)


def test_is_expired_exception_handling(user_session_dao: UserSessionDAO, sample_session_data: dict, mocker):
    """Test exception handling when checking session expiration fails."""
    # Create a session
    session = user_session_dao.create_session(**sample_session_data)
    
    # Mock datetime.now to raise an exception
    mocker.patch('database.daos.user.user_sessions_dao.datetime', side_effect=Exception("Time error"))
    
    # This should return True (expired) as a safe default
    is_expired = user_session_dao.is_expired(session, 3600)
    assert is_expired is True