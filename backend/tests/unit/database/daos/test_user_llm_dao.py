"""
Unit tests for the UserLLMDAO.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session
from datetime import datetime, UTC

from database.daos.user.user_llm_dao import UserLLMDAO
from database.models.user_llm_configs import UserLLMConfigs
from database.models.user import User


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Fixture to create a sample user for testing."""
    user = User(id=str(uuid4()), oauth_username="testuser", oauth_email="test@example.com", oauth_provider="github")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_llm_config_data(sample_user: User) -> dict:
    """Fixture to provide sample LLM configuration data."""
    return {
        "user_id": sample_user.id,
        "provider": "openai",
        "model_name": "gpt-4",
        "api_key": "test_api_key",
        "base_url": "https://api.openai.com/v1",
    }


@pytest.fixture
def user_llm_dao(db_session: Session) -> UserLLMDAO:
    """Fixture to create a UserLLMDAO instance."""
    return UserLLMDAO(db_session)


def test_add_llm_config(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict):
    """Test adding a new LLM configuration."""
    config = user_llm_dao.add_llm_config(**sample_llm_config_data)

    assert config.id is not None
    assert config.user_id == sample_llm_config_data["user_id"]
    assert config.provider == sample_llm_config_data["provider"]
    assert config.model_name == sample_llm_config_data["model_name"]
    assert config.api_key == sample_llm_config_data["api_key"]
    assert config.base_url == sample_llm_config_data["base_url"]
    assert isinstance(config.created_at, datetime)
    assert isinstance(config.updated_at, datetime)


def test_get_llm_config_by_id(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict):
    """Test retrieving an LLM configuration by its ID."""
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    retrieved_config = user_llm_dao.get_llm_config_by_id(created_config.id)

    assert retrieved_config is not None
    assert retrieved_config.id == created_config.id
    assert retrieved_config.user_id == created_config.user_id

    # Test with non-existent ID
    non_existent_config = user_llm_dao.get_llm_config_by_id(str(uuid4()))
    assert non_existent_config is None


def test_get_llm_configs_for_user(user_llm_dao: UserLLMDAO, sample_user: User, sample_llm_config_data: dict):
    """Test retrieving all LLM configurations for a user."""
    # Add two configs for the same user
    user_llm_dao.add_llm_config(**sample_llm_config_data)
    sample_llm_config_data["model_name"] = "gpt-3.5-turbo"
    user_llm_dao.add_llm_config(**sample_llm_config_data)

    configs = user_llm_dao.get_llm_configs_for_user(sample_user.id)
    assert len(configs) == 2
    assert all(c.user_id == sample_user.id for c in configs)

    # Test for user with no configs
    new_user = User(id=str(uuid4()), oauth_username="newuser", oauth_email="newuser@example.com", oauth_provider="github")
    user_llm_dao.db.add(new_user)
    user_llm_dao.db.commit()
    empty_configs = user_llm_dao.get_llm_configs_for_user(new_user.id)
    assert len(empty_configs) == 0


def test_get_llm_config_by_provider_and_model(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict):
    """Test retrieving an LLM configuration by user, provider, and model."""
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    retrieved_config = user_llm_dao.get_llm_config_by_provider_and_model(
        sample_llm_config_data["user_id"],
        sample_llm_config_data["provider"],
        sample_llm_config_data["model_name"]
    )

    assert retrieved_config is not None
    assert retrieved_config.id == created_config.id

    # Test with non-existent combination
    non_existent_config = user_llm_dao.get_llm_config_by_provider_and_model(
        sample_llm_config_data["user_id"],
        "nonexistent_provider",
        "nonexistent_model"
    )
    assert non_existent_config is None


def test_update_llm_config(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict):
    """Test updating an LLM configuration."""
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    original_updated_at = created_config.updated_at

    update_data = {
        "config_id": created_config.id,
        "provider": "anthropic",
        "model_name": "claude-3-opus",
    }
    updated_config = user_llm_dao.update_llm_config(**update_data)

    assert updated_config is not None
    assert updated_config.id == created_config.id
    assert updated_config.provider == update_data["provider"]
    assert updated_config.model_name == update_data["model_name"]
    # Ensure other fields are unchanged
    assert updated_config.api_key == created_config.api_key
    # Ensure updated_at timestamp changed
    assert updated_config.updated_at > original_updated_at

    # Test updating non-existent config
    non_existent_update = user_llm_dao.update_llm_config(config_id=str(uuid4()), provider="new_provider")
    assert non_existent_update is None


def test_delete_llm_config(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict):
    """Test deleting an LLM configuration."""
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    config_id = created_config.id

    # Successful deletion
    delete_success = user_llm_dao.delete_llm_config(config_id)
    assert delete_success is True

    # Verify it's deleted
    deleted_config = user_llm_dao.get_llm_config_by_id(config_id)
    assert deleted_config is None

    # Attempt to delete again
    delete_fail = user_llm_dao.delete_llm_config(config_id)
    assert delete_fail is False

    # Test deleting non-existent config
    delete_non_existent = user_llm_dao.delete_llm_config(str(uuid4()))
    assert delete_non_existent is False


def test_add_llm_config_with_optional_fields(user_llm_dao: UserLLMDAO, sample_user: User):
    """Test adding LLM config with only required fields."""
    config = user_llm_dao.add_llm_config(
        user_id=sample_user.id,
        provider="anthropic",
        model_name="claude-3-sonnet"
    )
    
    assert config.id is not None
    assert config.user_id == sample_user.id
    assert config.provider == "anthropic"
    assert config.model_name == "claude-3-sonnet"
    assert config.api_key is None
    assert config.base_url is None


def test_update_llm_config_all_fields(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict):
    """Test updating all fields in an LLM configuration."""
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    
    # Update all fields
    updated_config = user_llm_dao.update_llm_config(
        config_id=created_config.id,
        provider="new_provider",
        model_name="new_model",
        api_key="new_api_key",
        base_url="https://new-api.example.com"
    )
    
    assert updated_config is not None
    assert updated_config.id == created_config.id
    assert updated_config.provider == "new_provider"
    assert updated_config.model_name == "new_model"
    assert updated_config.api_key == "new_api_key"
    assert updated_config.base_url == "https://new-api.example.com"


def test_add_llm_config_exception_handling(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict, mocker):
    """Test exception handling when adding LLM config fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_llm_dao.db, 'commit', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_llm_dao.add_llm_config(**sample_llm_config_data)
    
    assert "Database error" in str(exc_info.value)


def test_get_llm_config_by_id_exception_handling(user_llm_dao: UserLLMDAO, mocker):
    """Test exception handling when getting LLM config by ID fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_llm_dao.db, 'exec', side_effect=Exception("Database error"))
    
    config_id = str(uuid4())
    
    # This should return None due to exception handling
    result = user_llm_dao.get_llm_config_by_id(config_id)
    assert result is None


def test_get_llm_configs_for_user_exception_handling(user_llm_dao: UserLLMDAO, sample_user: User, mocker):
    """Test exception handling when getting LLM configs for user fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_llm_dao.db, 'exec', side_effect=Exception("Database error"))
    
    # This should return empty list due to exception handling
    result = user_llm_dao.get_llm_configs_for_user(sample_user.id)
    assert result == []


def test_get_llm_config_by_provider_and_model_exception_handling(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict, mocker):
    """Test exception handling when getting LLM config by provider and model fails."""
    # Mock the database session to raise an exception
    mocker.patch.object(user_llm_dao.db, 'exec', side_effect=Exception("Database error"))
    
    # This should return None due to exception handling
    result = user_llm_dao.get_llm_config_by_provider_and_model(
        sample_llm_config_data["user_id"],
        sample_llm_config_data["provider"],
        sample_llm_config_data["model_name"]
    )
    assert result is None


def test_update_llm_config_exception_handling(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict, mocker):
    """Test exception handling when updating LLM config fails."""
    # First create a config
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    
    # Mock the database session to raise an exception during update
    mocker.patch.object(user_llm_dao.db, 'commit', side_effect=Exception("Database error"))
    
    # This should raise an exception
    with pytest.raises(Exception) as exc_info:
        user_llm_dao.update_llm_config(config_id=created_config.id, provider="new_provider")
    
    assert "Database error" in str(exc_info.value)


def test_delete_llm_config_exception_handling(user_llm_dao: UserLLMDAO, sample_llm_config_data: dict, mocker):
    """Test exception handling when deleting LLM config fails."""
    # First create a config
    created_config = user_llm_dao.add_llm_config(**sample_llm_config_data)
    
    # Mock the database session to raise an exception during delete
    mocker.patch.object(user_llm_dao.db, 'commit', side_effect=Exception("Database error"))
    
    # This should return False due to exception handling
    result = user_llm_dao.delete_llm_config(created_config.id)
    assert result is False