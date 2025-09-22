import pytest
from datetime import datetime, UTC
from uuid import uuid4
from sqlmodel import SQLModel, Session

from database.models.user_llm_configs import UserLLMConfigs
from database.models.user import User


def test_create_user_llm_config(db_session: Session):
    """
    Test creating a new UserLLMConfigs instance.
    """
    user_id = str(uuid4())
    user = User(id=user_id, username="testuser")
    db_session.add(user)
    db_session.commit()

    config_id = str(uuid4())
    config = UserLLMConfigs(
        id=config_id,
        user_id=user_id,
        provider="openai",
        model_name="gpt-4",
        api_key="sk-test",
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)

    assert config.id == config_id
    assert config.user_id == user_id
    assert config.provider == "openai"
    assert config.model_name == "gpt-4"
    assert config.api_key == "sk-test"
    assert isinstance(config.created_at, datetime)
    assert isinstance(config.updated_at, datetime)


def test_user_llm_config_repr(db_session: Session):
    """
    Test the __repr__ method of UserLLMConfigs.
    """
    user_id = str(uuid4())
    user = User(id=user_id, username="testuser")
    db_session.add(user)
    db_session.commit()

    config_id = str(uuid4())
    config = UserLLMConfigs(
        id=config_id,
        user_id=user_id,
        provider="anthropic",
        model_name="claude-3-opus",
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)

    expected_repr = f"<UserLLMConfigs(id={config_id}, user_id={user_id}, provider=anthropic, model_name=claude-3-opus)>"
    assert repr(config) == expected_repr


def test_user_llm_config_relationship(db_session: Session):
    """
    Test the relationship between User and UserLLMConfigs.
    """
    user_id = str(uuid4())
    user = User(id=user_id, username="testuser")
    db_session.add(user)
    db_session.commit()

    config1 = UserLLMConfigs(
        user_id=user_id,
        provider="openai",
        model_name="gpt-4",
    )
    config2 = UserLLMConfigs(
        user_id=user_id,
        provider="google",
        model_name="gemini-pro",
    )
    db_session.add(config1)
    db_session.add(config2)
    db_session.commit()

    # Refresh user to load relationships
    db_session.refresh(user)
    assert len(user.llm_configs) == 2
    assert user.llm_configs[0].provider == "openai"
    assert user.llm_configs[1].provider == "google"

    # Test back-population
    assert config1.user == user
    assert config2.user == user


def test_user_llm_config_defaults(db_session: Session):
    """
    Test default values for UserLLMConfigs fields.
    """
    user_id = str(uuid4())
    user = User(id=user_id, username="testuser")
    db_session.add(user)
    db_session.commit()

    config = UserLLMConfigs(
        user_id=user_id,
        provider="openai",
        model_name="gpt-3.5-turbo",
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)

    assert config.api_key is None
    assert config.base_url is None