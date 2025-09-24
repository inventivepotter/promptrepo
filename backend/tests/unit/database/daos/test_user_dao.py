"""
Unit tests for the UserDAO.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session
from datetime import datetime, UTC

from database.daos.user.user_dao import UserDAO
from database.models.user import User


@pytest.fixture
def sample_user_data():
    """Fixture to provide sample user data."""
    return {
        "id": str(uuid4()),
        "oauth_provider": "github",
        "username": "testuser",
        "name": "Test User",
        "email": "test@example.com",
        "avatar_url": "https://github.com/testuser.png",
        "oauth_user_id": 12345,
        "html_url": "https://github.com/testuser"
    }


@pytest.fixture
def user_dao(db_session: Session) -> UserDAO:
    """Fixture to create a UserDAO instance."""
    return UserDAO(db_session)


def test_save_user_create_new(user_dao: UserDAO, sample_user_data: dict):
    """Test creating a new user."""
    user = User(**sample_user_data)
    
    # Save the user
    saved_user = user_dao.save_user(user)
    
    # Verify the user was created
    assert saved_user.id == sample_user_data["id"]
    assert saved_user.oauth_username == sample_user_data["username"]
    assert saved_user.oauth_provider == sample_user_data["oauth_provider"]
    assert saved_user.oauth_name == sample_user_data["name"]
    assert saved_user.oauth_email == sample_user_data["email"]
    assert saved_user.oauth_avatar_url == sample_user_data["avatar_url"]
    assert saved_user.oauth_user_id == sample_user_data["oauth_user_id"]
    assert saved_user.html_url == sample_user_data["html_url"]
    assert isinstance(saved_user.created_at, datetime)
    assert isinstance(saved_user.modified_at, datetime)


def test_save_user_update_existing(user_dao: UserDAO, sample_user_data: dict):
    """Test updating an existing user."""
    # First create a user
    user = User(**sample_user_data)
    saved_user = user_dao.save_user(user)
    
    # Now update the user
    updated_data = User(
        id=saved_user.id,
        oauth_provider="github",
        oauth_username="testuser",  # Same username
        oauth_name="Updated Name",
        oauth_email="updated@example.com"
    )
    
    updated_user = user_dao.save_user(updated_data)
    
    # Verify the user was updated
    assert updated_user.id == saved_user.id
    assert updated_user.oauth_username == "testuser"  # Should remain the same
    assert updated_user.oauth_name == "Updated Name"
    assert updated_user.oauth_email == "updated@example.com"
    assert updated_user.oauth_provider == "github"  # Should remain the same
    assert updated_user.modified_at > saved_user.modified_at


def test_save_user_with_nonexistent_field(user_dao: UserDAO, sample_user_data: dict, caplog):
    """Test saving user with a non-existent field (should be ignored)."""
    user = User(**sample_user_data)
    
    # Add a non-existent field to the model dump
    update_data = user.model_dump(exclude_unset=True)
    update_data["nonexistent_field"] = "some_value"
    
    # This should not raise an error but should log a warning
    saved_user = user_dao.save_user(user)
    
    # Verify the user was saved without the non-existent field
    assert saved_user.id == sample_user_data["id"]
    assert not hasattr(saved_user, "nonexistent_field")
    
    # Check that a warning was logged
    assert "Attempted to update non-existent field" in caplog.text


def test_get_user_by_id_found(user_dao: UserDAO, sample_user_data: dict):
    """Test retrieving a user by ID when found."""
    # Create a user first
    user = User(**sample_user_data)
    saved_user = user_dao.save_user(user)
    
    # Retrieve the user by ID
    retrieved_user = user_dao.get_user_by_id(saved_user.id)
    
    # Verify the user was retrieved correctly
    assert retrieved_user is not None
    assert retrieved_user.id == saved_user.id
    assert retrieved_user.oauth_username == saved_user.oauth_username


def test_get_user_by_id_not_found(user_dao: UserDAO):
    """Test retrieving a user by ID when not found."""
    non_existent_id = str(uuid4())
    retrieved_user = user_dao.get_user_by_id(non_existent_id)
    
    assert retrieved_user is None


def test_get_user_by_username_found(user_dao: UserDAO, sample_user_data: dict):
    """Test retrieving a user by username when found."""
    # Create a user first
    user = User(**sample_user_data)
    saved_user = user_dao.save_user(user)
    
    # Retrieve the user by username
    retrieved_user = user_dao.get_user_by_username(saved_user.oauth_username)
    
    # Verify the user was retrieved correctly
    assert retrieved_user is not None
    assert retrieved_user.oauth_username == saved_user.oauth_username
    assert retrieved_user.id == saved_user.id


def test_get_user_by_username_not_found(user_dao: UserDAO):
    """Test retrieving a user by username when not found."""
    non_existent_username = "nonexistentuser"
    retrieved_user = user_dao.get_user_by_username(non_existent_username)
    
    assert retrieved_user is None


def test_get_users_with_pagination(user_dao: UserDAO, sample_user_data: dict):
    """Test retrieving users with pagination."""
    # Create multiple users
    users = []
    for i in range(5):
        user_data = sample_user_data.copy()
        user_data["id"] = str(uuid4())
        user_data["username"] = f"user{i}"
        user = User(**user_data)
        users.append(user_dao.save_user(user))
    
    # Test getting all users
    all_users = user_dao.get_users()
    assert len(all_users) == 5
    
    # Test pagination with skip
    skipped_users = user_dao.get_users(skip=2)
    assert len(skipped_users) == 3
    
    # Test pagination with limit
    limited_users = user_dao.get_users(limit=3)
    assert len(limited_users) == 3
    
    # Test pagination with both skip and limit
    paginated_users = user_dao.get_users(skip=1, limit=2)
    assert len(paginated_users) == 2


def test_get_users_empty_database(user_dao: UserDAO):
    """Test retrieving users when database is empty."""
    users = user_dao.get_users()
    assert len(users) == 0


def test_delete_user_success(user_dao: UserDAO, sample_user_data: dict):
    """Test successfully deleting a user."""
    # Create a user first
    user = User(**sample_user_data)
    saved_user = user_dao.save_user(user)
    
    # Delete the user
    delete_result = user_dao.delete_user(saved_user.id)
    
    # Verify deletion was successful
    assert delete_result is True
    
    # Verify user is no longer retrievable
    retrieved_user = user_dao.get_user_by_id(saved_user.id)
    assert retrieved_user is None


def test_delete_user_not_found(user_dao: UserDAO):
    """Test deleting a user that doesn't exist."""
    non_existent_id = str(uuid4())
    delete_result = user_dao.delete_user(non_existent_id)
    
    assert delete_result is False


def test_save_user_exception_handling(user_dao: UserDAO, sample_user_data: dict, mocker):
    """Test exception handling when saving a user fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_dao.db, 'exec', side_effect=Exception("Database error"))
    
    user = User(**sample_user_data)
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_dao.save_user(user)
    
    assert "Database error" in str(exc_info.value)


def test_get_user_by_id_exception_handling(user_dao: UserDAO, mocker):
    """Test exception handling when getting user by ID fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_dao.db, 'get', side_effect=Exception("Database error"))
    
    user_id = str(uuid4())
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_dao.get_user_by_id(user_id)
    
    assert "Database error" in str(exc_info.value)


def test_get_user_by_username_exception_handling(user_dao: UserDAO, mocker):
    """Test exception handling when getting user by username fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_dao.db, 'exec', side_effect=Exception("Database error"))
    
    username = "testuser"
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_dao.get_user_by_username(username)
    
    assert "Database error" in str(exc_info.value)


def test_get_users_exception_handling(user_dao: UserDAO, mocker):
    """Test exception handling when getting users fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_dao.db, 'exec', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_dao.get_users()
    
    assert "Database error" in str(exc_info.value)


def test_delete_user_exception_handling(user_dao: UserDAO, sample_user_data: dict, mocker):
    """Test exception handling when deleting a user fails."""
    # Create a user first
    user = User(**sample_user_data)
    saved_user = user_dao.save_user(user)
    
    # Mock the database session to raise an exception during delete
    mocker.patch.object(user_dao.db, 'delete', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_dao.delete_user(saved_user.id)
    
    assert "Database error" in str(exc_info.value)