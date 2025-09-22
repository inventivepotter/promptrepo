"""
Service for managing user LLM configurations in the database.
Handles CRUD operations for the user_llm_configs table.
"""
from sqlmodel import Session, select
from database.models.user_llm_configs import UserLLMConfigs
from datetime import datetime, UTC
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class UserLLMDAO:
    """Service for managing user LLM configurations."""

    def __init__(self, db: Session):
        """
        Initialize UserLLMDAO with database session.

        Args:
            db: Database session
        """
        self.db = db

    def add_llm_config(
        self,
        user_id: str,
        provider: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> UserLLMConfigs:
        """
        Add a new LLM configuration for a user.

        Args:
            user_id: ID of the user
            provider: LLM provider (e.g., 'openai', 'anthropic')
            model_name: Specific model name (e.g., 'gpt-4', 'claude-3-opus')
            api_key: API key for the provider
            base_url: Custom base URL for the LLM API

        Returns:
            Created UserLLMConfigs object

        Raises:
            Exception: If configuration creation fails
        """
        try:
            # Create new LLM config record
            user_llm_config = UserLLMConfigs(
                user_id=user_id,
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                base_url=base_url,
            )

            # Save to database
            self.db.add(user_llm_config)
            self.db.commit()
            self.db.refresh(user_llm_config)

            logger.info(f"Added LLM config for provider {provider}, model {model_name} for user {user_id}")
            return user_llm_config

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add LLM config for user {user_id}: {e}")
            raise

    def get_llm_config_by_id(self, config_id: str) -> Optional[UserLLMConfigs]:
        """
        Get LLM configuration by its ID.

        Args:
            config_id: LLM configuration ID

        Returns:
            UserLLMConfigs object if found, None otherwise
        """
        try:
            statement = select(UserLLMConfigs).where(UserLLMConfigs.id == config_id)
            return self.db.exec(statement).first()
        except Exception as e:
            logger.error(f"Failed to get LLM config {config_id}: {e}")
            return None

    def get_llm_configs_for_user(self, user_id: str) -> List[UserLLMConfigs]:
        """
        Get all LLM configurations for a user.

        Args:
            user_id: User ID

        Returns:
            List of UserLLMConfigs objects
        """
        try:
            statement = select(UserLLMConfigs).where(UserLLMConfigs.user_id == user_id)
            return list(self.db.exec(statement).all())
        except Exception as e:
            logger.error(f"Failed to get LLM configs for user {user_id}: {e}")
            return []

    def get_llm_config_by_provider_and_model(
        self,
        user_id: str,
        provider: str,
        model_name: str
    ) -> Optional[UserLLMConfigs]:
        """
        Get LLM configuration by user ID, provider, and model name.

        Args:
            user_id: User ID
            provider: LLM provider
            model_name: Model name

        Returns:
            UserLLMConfigs object if found, None otherwise
        """
        try:
            statement = select(UserLLMConfigs).where(
                UserLLMConfigs.user_id == user_id,
                UserLLMConfigs.provider == provider,
                UserLLMConfigs.model_name == model_name
            )
            return self.db.exec(statement).first()
        except Exception as e:
            logger.error(f"Failed to get LLM config for user {user_id}, provider {provider}, model {model_name}: {e}")
            return None

    def update_llm_config(
        self,
        config_id: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Optional[UserLLMConfigs]:
        """
        Update an LLM configuration.

        Args:
            config_id: LLM configuration ID
            provider: LLM provider
            model_name: Model name
            api_key: API key
            base_url: Base URL

        Returns:
            Updated UserLLMConfigs object or None if not found
        """
        try:
            user_llm_config = self.get_llm_config_by_id(config_id)
            if not user_llm_config:
                logger.warning(f"LLM config {config_id} not found for update")
                return None

            # Update fields if provided
            if provider is not None:
                user_llm_config.provider = provider
            if model_name is not None:
                user_llm_config.model_name = model_name
            if api_key is not None:
                user_llm_config.api_key = api_key
            if base_url is not None:
                user_llm_config.base_url = base_url

            user_llm_config.updated_at = datetime.now(UTC)

            # Save changes
            self.db.add(user_llm_config)
            self.db.commit()
            self.db.refresh(user_llm_config)

            logger.info(f"Updated LLM config {config_id}")
            return user_llm_config

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update LLM config {config_id}: {e}")
            raise

    def delete_llm_config(self, config_id: str) -> bool:
        """
        Delete an LLM configuration record.

        Args:
            config_id: LLM configuration ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            user_llm_config = self.get_llm_config_by_id(config_id)
            if not user_llm_config:
                logger.warning(f"LLM config {config_id} not found for deletion")
                return False

            self.db.delete(user_llm_config)
            self.db.commit()

            logger.info(f"Deleted LLM config {config_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete LLM config {config_id}: {e}")
            return False