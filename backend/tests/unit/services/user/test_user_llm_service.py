"""
Unit tests for the UserLLMService.
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
    user = User(id=str(uuid4()), username="testuser", email="test@example.com")
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


def test_add_llm_config(db_session: Session, sample_llm_config_data: dict):
    """Test adding a new LLM configuration."""
    config = UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)

    assert config.id is not None
    assert config.user_id == sample_llm_config_data["user_id"]
    assert config.provider == sample_llm_config_data["provider"]
    assert config.model_name == sample_llm_config_data["model_name"]
    assert config.api_key == sample_llm_config_data["api_key"]
    assert config.base_url == sample_llm_config_data["base_url"]
    assert isinstance(config.created_at, datetime)
    assert isinstance(config.updated_at, datetime)


def test_get_llm_config_by_id(db_session: Session, sample_llm_config_data: dict):
    """Test retrieving an LLM configuration by its ID."""
    created_config = UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)
    retrieved_config = UserLLMDAO.get_llm_config_by_id(db_session, created_config.id)

    assert retrieved_config is not None
    assert retrieved_config.id == created_config.id
    assert retrieved_config.user_id == created_config.user_id

    # Test with non-existent ID
    non_existent_config = UserLLMDAO.get_llm_config_by_id(db_session, str(uuid4()))
    assert non_existent_config is None


def test_get_llm_configs_for_user(db_session: Session, sample_user: User, sample_llm_config_data: dict):
    """Test retrieving all LLM configurations for a user."""
    # Add two configs for the same user
    UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)
    sample_llm_config_data["model_name"] = "gpt-3.5-turbo"
    UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)

    configs = UserLLMDAO.get_llm_configs_for_user(db_session, sample_user.id)
    assert len(configs) == 2
    assert all(c.user_id == sample_user.id for c in configs)

    # Test for user with no configs
    new_user = User(id=str(uuid4()), username="newuser", email="newuser@example.com")
    db_session.add(new_user)
    db_session.commit()
    empty_configs = UserLLMDAO.get_llm_configs_for_user(db_session, new_user.id)
    assert len(empty_configs) == 0


def test_get_llm_config_by_provider_and_model(db_session: Session, sample_llm_config_data: dict):
    """Test retrieving an LLM configuration by user, provider, and model."""
    created_config = UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)
    retrieved_config = UserLLMDAO.get_llm_config_by_provider_and_model(
        db_session,
        sample_llm_config_data["user_id"],
        sample_llm_config_data["provider"],
        sample_llm_config_data["model_name"]
    )

    assert retrieved_config is not None
    assert retrieved_config.id == created_config.id

    # Test with non-existent combination
    non_existent_config = UserLLMDAO.get_llm_config_by_provider_and_model(
        db_session,
        sample_llm_config_data["user_id"],
        "nonexistent_provider",
        "nonexistent_model"
    )
    assert non_existent_config is None


def test_update_llm_config(db_session: Session, sample_llm_config_data: dict):
    """Test updating an LLM configuration."""
    created_config = UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)
    original_updated_at = created_config.updated_at

    update_data = {
        "config_id": created_config.id,
        "provider": "anthropic",
        "model_name": "claude-3-opus",
    }
    updated_config = UserLLMDAO.update_llm_config(db_session, **update_data)

    assert updated_config is not None
    assert updated_config.id == created_config.id
    assert updated_config.provider == update_data["provider"]
    assert updated_config.model_name == update_data["model_name"]
    # Ensure other fields are unchanged
    assert updated_config.api_key == created_config.api_key
    # Ensure updated_at timestamp changed
    assert updated_config.updated_at > original_updated_at

    # Test updating non-existent config
    non_existent_update = UserLLMDAO.update_llm_config(db_session, config_id=str(uuid4()), provider="new_provider")
    assert non_existent_update is None


def test_delete_llm_config(db_session: Session, sample_llm_config_data: dict):
    """Test deleting an LLM configuration."""
    created_config = UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)
    config_id = created_config.id

    # Successful deletion
    delete_success = UserLLMDAO.delete_llm_config(db_session, config_id)
    assert delete_success is True

    # Verify it's deleted
    deleted_config = UserLLMDAO.get_llm_config_by_id(db_session, config_id)
    assert deleted_config is None

    # Attempt to delete again
    delete_fail = UserLLMDAO.delete_llm_config(db_session, config_id)
    assert delete_fail is False

    # Test deleting non-existent config
    delete_non_existent = UserLLMDAO.delete_llm_config(db_session, str(uuid4()))
    assert delete_non_existent is False


def test_get_default_llm_config_for_user(db_session: Session, sample_user: User, sample_llm_config_data: dict):
    """Test getting the default LLM configuration for a user."""
    # No configs for user
    default_config_none = UserLLMDAO.get_default_llm_config_for_user(db_session, sample_user.id)
    assert default_config_none is None

    # Add one config
    first_config = UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)

    # Should return the first one
    default_config_one = UserLLMDAO.get_default_llm_config_for_user(db_session, sample_user.id)
    assert default_config_one is not None
    assert default_config_one.id == first_config.id

    # Add another config
    sample_llm_config_data["model_name"] = "gpt-3.5-turbo"
    UserLLMDAO.add_llm_config(db_session, **sample_llm_config_data)

    # Should still return the first one added (as per current implementation)
    default_config_multiple = UserLLMDAO.get_default_llm_config_for_user(db_session, sample_user.id)
    assert default_config_multiple is not None
    assert default_config_multiple.id == first_config.id

    # Test for user with no configs
    new_user = User(id=str(uuid4()), username="anotheruser", email="another@example.com")
    db_session.add(new_user)
    db_session.commit()
    default_config_no_user = UserLLMDAO.get_default_llm_config_for_user(db_session, new_user.id)
    assert default_config_no_user is None