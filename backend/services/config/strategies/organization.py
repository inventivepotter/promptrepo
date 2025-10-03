"""
Configuration strategy for organization hosting type.
Requirements:
- Hosting type from ENV
- OAuth config from ENV (GitHub Client ID/Secret)
- LLM config from ENV (organization-wide) and users (user-specific)
- Repo config from users (stored in session/database)
"""

import json
import os
import logging
from typing import List
from pathlib import Path

from sqlmodel import Session
from services.config.models import HostingConfig, HostingType, LLMConfig, LLMConfigScope, OAuthConfig, RepoConfig
from database.daos.user.user_repos_dao import UserReposDAO
from database.daos.user import UserLLMDAO
from services.config.config_interface import IConfig
from services.file_operations import FileOperationsService
from settings import settings

logger = logging.getLogger(__name__)


class OrganizationConfig(IConfig):
    """
    Configuration strategy for organization hosting type.
    - Hosting type: From ENV
    - OAuth: From ENV (GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
    - LLM configs: From ENV (organization-wide) and user context (user-specific)
    - Repo configs: From user context (database/session)
    """
    
    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        """Set OAuth configurations in environment variables."""
        # For organization hosting, OAuth is required and stored in ENV
        if not oauth_configs:
            raise ValueError("OAuth configuration is required for organization hosting type.")
        
        # Convert OAuthConfig objects to dictionaries for JSON serialization
        oauth_configs_dict = [
            {
                "provider": config.provider,
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "redirect_url": config.redirect_url
            }
            for config in oauth_configs
        ]
        os.environ["OAUTH_CONFIGS"] = json.dumps(oauth_configs_dict)
        return oauth_configs
    
    def set_llm_configs(self, db: Session, user_id: str, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        """
        Set LLM configuration for a user using UserLLMService.
        For organization hosting, user-specific LLM configs are stored in database.
        ENV configs remain in ENV and are not modified by this method.
        """
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
        """
        Set repository configuration for a user and initiate cloning.
        For organization hosting, repo configs are managed per-user in database.
        This method stores configurations and initiates cloning via RepoLocatorService.
        
        Args:
            db: Database session
            user_id: User ID
            repo_configs: List of repository configurations
            remote_repo_service: Optional RepoLocatorService instance for cloning
        """
        user_repos_dao = UserReposDAO(db)
        file_ops = FileOperationsService()
        
        if not repo_configs:
            # If an empty list is provided, delete all existing repos for the user
            existing_repos = user_repos_dao.get_user_repositories(user_id)
            for repo in existing_repos:
                # Delete from database
                user_repos_dao.delete_repository(repo.id)
                # Delete from file system
                if repo.local_path:
                    file_ops.delete_directory(repo.local_path)
            return []

        # Get existing repos to track which ones to keep
        existing_repos = user_repos_dao.get_user_repositories(user_id)
        existing_repos_map = {repo.repo_clone_url: repo for repo in existing_repos}
        processed_repo_urls = set()

        saved_repos = []
        for config in repo_configs:
            try:
                # Check if repo already exists to avoid duplicates
                existing_repo = existing_repos_map.get(config.repo_url)
                if existing_repo:
                    # If it exists, we can optionally update it or just acknowledge it.
                    # For now, we'll consider it as successfully "set" and add to the return list.
                    saved_repos.append(config)
                    processed_repo_urls.add(config.repo_url)
                    logger.info(f"Repository {config.repo_name} already exists for user {user_id}")
                    continue
                
                # Ensure repo_name is provided, otherwise derive from repo_url as a fallback
                repo_name_to_use = config.repo_name
                if not repo_name_to_use and config.repo_url:
                    # Basic extraction: owner/repo-name from a URL like https://github.com/owner/repo-name
                    parts = config.repo_url.rstrip('/').split('/')
                    if len(parts) > 1:
                        repo_name_to_use = f"{parts[-2]}/{parts[-1]}"
                
                if not repo_name_to_use:
                    logger.warning(f"repo_name is missing and cannot be derived from repo_url: {config.repo_url}. Skipping.")
                    continue

                # Add repository to database with PENDING status
                new_repo = user_repos_dao.add_repository(
                    user_id=user_id,
                    repo_clone_url=config.repo_url,
                    repo_name=repo_name_to_use,
                    branch=config.base_branch or "main"
                )
                processed_repo_urls.add(config.repo_url)
                
                # Commit the transaction so the repository is visible for cloning
                db.commit()
                
                # Initiate cloning if remote_repo_service is provided
                if remote_repo_service:
                    oauth_token = getattr(config, 'access_token', None)
                    clone_success = remote_repo_service.clone_user_repository(
                        user_id=user_id,
                        repo_id=new_repo.id,
                        oauth_token=oauth_token
                    )
                    if clone_success:
                        logger.info(f"Successfully cloned {repo_name_to_use} for user {user_id}")
                    else:
                        logger.warning(f"Failed to clone {repo_name_to_use} for user {user_id}")
                else:
                    logger.info(f"Repository {repo_name_to_use} added with PENDING status (no clone service provided)")
                
                saved_repos.append(config)
            except Exception as e:
                # Log error and continue with other configs
                logger.error(f"Error saving repository config for {config.repo_url or config.repo_name}: {e}", exc_info=True)
        
        # Delete any existing repos that were not in the new list
        for repo in existing_repos:
            if repo.repo_clone_url not in processed_repo_urls:
                # Delete from database
                user_repos_dao.delete_repository(repo.id)
                # Delete from file system
                if repo.local_path:
                    file_ops.delete_directory(repo.local_path)
                logger.info(f"Deleted repository {repo.repo_name} (ID: {repo.id}) for user {user_id}")
        
        return saved_repos if saved_repos else None
    
    def get_hosting_config(self) -> HostingConfig:
        """Get hosting configuration."""
        hosting_config = HostingConfig()
        hosting_type_str = os.environ.get("HOSTING_TYPE", "organization")
        try:
            hosting_config.type = HostingType(hosting_type_str)
        except ValueError:
            hosting_config.type = HostingType.ORGANIZATION
        return hosting_config
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        """Get OAuth configurations from environment variables."""
        oauth_configs_json = os.environ.get("OAUTH_CONFIGS")
        
        if oauth_configs_json:
            try:
                oauth_configs_dict = json.loads(oauth_configs_json)
                oauth_configs = [
                    OAuthConfig(
                        provider=config["provider"],
                        client_id=config["client_id"],
                        client_secret=config["client_secret"],
                        redirect_url=config.get("redirect_url", "")
                    )
                    for config in oauth_configs_dict
                ]
                return oauth_configs
            except (json.JSONDecodeError, KeyError):
                pass
        
        return None
    
    def get_llm_configs(self, db: Session, user_id: str | None) -> List[LLMConfig] | None:
        """
        Get LLM configurations from both ENV and user database.
        ENV configs have 'organization' scope, user configs have 'user' scope.
        User configs override ENV configs for the same provider/model combination.
        """
        llm_configs = []
        
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
                        scope=LLMConfigScope.ORGANIZATION  # ENV configs have organization scope
                    )
                    for config in llm_configs_data
                ]
        except json.JSONDecodeError:
            pass
        
        # Then, get user-specific LLM configs from database if user_id is provided
        user_configs = []
        if user_id:
            user_llm_dao = UserLLMDAO(db)
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
        """
        Get repository configuration for a user.
        For organization hosting, repo configs are retrieved from user context.
        This method uses UserReposService to fetch configurations from the database.
        """
        user_repos_dao = UserReposDAO(db)
        user_repos = user_repos_dao.get_user_repositories(user_id)
        if not user_repos:
            return None

        repo_configs = []
        for user_repo in user_repos:
            # Map UserRepos object to RepoConfig object
            config = RepoConfig(
                id=user_repo.id,
                repo_name=user_repo.repo_name,
                repo_url=user_repo.repo_clone_url,
                base_branch=user_repo.branch or "main",
                current_branch=user_repo.branch
            )
            repo_configs.append(config)
        
        return repo_configs if repo_configs else None