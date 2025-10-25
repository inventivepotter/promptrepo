"""
Configuration strategy for individual hosting type.
Requirements: llmConfigs only
"""

import json
import os
from typing import List

from sqlmodel import Session

from services.config.models import HostingConfig, HostingType, LLMConfig, LLMConfigScope, OAuthConfig, RepoConfig
from services.config.config_interface import IConfig
from database.daos.user.user_llm_dao import UserLLMDAO
from database.daos.user.user_dao import UserDAO
from database.models.user import User
from schemas.oauth_provider_enum import OAuthProvider


class IndividualConfig(IConfig):
    """
    Configuration strategy for individual hosting type.
    Requirements: llmConfigs only
    """

    def _ensure_individual_user_exists(self, db: Session, user_id: str) -> None:
        """
        Ensures that the default user for individual hosting exists.
        If not, creates the user.
        """
        user_dao = UserDAO(db)
        user = user_dao.get_user_by_id(user_id)
        if not user:
            new_user = User(
                id=user_id,
                oauth_username=user_id,
                oauth_provider=OAuthProvider.GITHUB,  # Placeholder for individual hosting
            )
            user_dao.save_user(new_user)

    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        # For individual hosting, OAuth will not be configured
        return None

    def set_llm_configs(self, db: Session, user_id: str, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        """
        Set LLM configuration for a user using UserLLMService.
        For individual hosting, user-specific LLM configs are stored in database.
        ENV configs remain in ENV and are not modified by this method.
        """
        self._ensure_individual_user_exists(db, user_id)
        user_llm_dao = UserLLMDAO(db)
        if not llm_configs:
            # If an empty list is provided, delete all existing configs for the user.
            existing_db_llm_configs = user_llm_dao.get_llm_configs_for_user(user_id)
            for config in existing_db_llm_configs:
                user_llm_dao.delete_llm_config(config.id)
            return []

        # Filter out organization-scoped configs (these should remain in ENV)
        user_configs = [config for config in llm_configs if config.scope == LLMConfigScope.USER]
        
        if not user_configs:
            return []

        existing_db_llm_configs = user_llm_dao.get_llm_configs_for_user(user_id)
        existing_configs_map = {(config.provider, config.model_name): config for config in existing_db_llm_configs}
        processed_existing_ids = set()

        for config_data in user_configs:
            key = (config_data.provider, config_data.model)
            if key in existing_configs_map:
                # Update existing config
                existing_config = existing_configs_map[key]
                user_llm_dao.update_llm_config(
                    config_id=existing_config.id,
                    provider=config_data.provider,
                    model_name=config_data.model,
                    api_key=config_data.api_key,
                    base_url=config_data.api_base_url
                )
                processed_existing_ids.add(existing_config.id)
            else:
                # Create new config
                user_llm_dao.add_llm_config(
                    user_id=user_id,
                    provider=config_data.provider,
                    model_name=config_data.model,
                    api_key=config_data.api_key,
                    base_url=config_data.api_base_url
                )
        
        # Delete any existing configs that were not in the new list
        for config in existing_db_llm_configs:
            if config.id not in processed_existing_ids:
                user_llm_dao.delete_llm_config(config.id)
        
        return user_configs
    
    def set_repo_configs(self, db: Session, user_id: str, repo_configs: List[RepoConfig], remote_repo_service=None) -> List[RepoConfig] | None:
        # Individual hosting does not manage repo configs
        return None

    def get_hosting_config(self) -> HostingConfig:
        """Get hosting configuration."""
        hosting_config = HostingConfig()
        hosting_type_str = os.environ.get("HOSTING_TYPE", "individual")
        try:
            hosting_config.type = HostingType(hosting_type_str)
        except ValueError:
            hosting_config.type = HostingType.INDIVIDUAL
        return hosting_config
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        """Get OAuth configurations."""
        # For individual hosting, OAuth might not be configured
        return None

    def get_llm_configs(self, db: Session, user_id: str | None) -> List[LLMConfig] | None:
        """
        Get LLM configurations from both ENV and user database.
        ENV configs have 'organization' scope, user configs have 'user' scope.
        User configs override ENV configs for the same provider/model combination.
        """
        llm_configs = []
        user_llm_dao = UserLLMDAO(db)
        # First, get LLM configs from ENV (organization-wide)
        llm_configs_str = os.environ.get("DEFAULT_LLM_CONFIGS", "[]")
        env_configs = []
        try:
            llm_configs_data = json.loads(llm_configs_str)
            if llm_configs_data:
                env_configs = [
                    LLMConfig(
                        id=config.get("id"),
                        provider=config.get("provider"),
                        model=config.get("model"),
                        api_key=config.get("api_key"),
                        api_base_url=config.get("api_base_url") or "",
                        label=config.get("label") or "",  # Parse label from ENV config
                        scope=LLMConfigScope.USER
                    )
                    for config in llm_configs_data
                ]
        except json.JSONDecodeError:
            pass
        
        # Then, get user-specific LLM configs from database if user_id is provided
        user_configs = []
        if user_id:
            db_llm_configs = user_llm_dao.get_llm_configs_for_user(user_id)
            if db_llm_configs:
                user_configs = [
                    LLMConfig(
                        id=config.id,
                        provider=config.provider,
                        model=config.model_name,
                        api_key=config.api_key or "",
                        api_base_url=config.base_url or "",
                        scope=LLMConfigScope.USER  # User configs have user scope
                    )
                    for config in db_llm_configs
                ]
        
        # Merge configs: user configs override ENV configs for same provider/model
        config_map = {}
        
        # Add ENV configs first
        for config in env_configs:
            key = (config.provider, config.model)
            config_map[key] = config
        
        # Override with user configs if they exist for the same provider/model
        for config in user_configs:
            key = (config.provider, config.model)
            config_map[key] = config
        
        # Convert back to list
        llm_configs = list(config_map.values())
        
        return llm_configs if llm_configs else None

    def get_repo_configs(self, db: Session, user_id: str) -> List[RepoConfig] | None:
        # Individual hosting does not manage repo configs
        return None