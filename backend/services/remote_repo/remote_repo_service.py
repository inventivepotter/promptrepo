"""
Remote Repository Service

This module provides the main service for managing remote repositories,
including fetching repository lists and branch information.
"""

import uuid
import logging
from pathlib import Path
from typing import Optional

from sqlmodel import Session
from settings import settings
from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.oauth.models import OAuthError
from database.daos.user.user_dao import UserDAO
from database.daos.user.user_repos_dao import UserReposDAO
from database.models.user_repos import RepoStatus
from services.auth.session_service import SessionService
from services.remote_repo.models import RepoInfo, RepositoryList, RepositoryBranchesResponse, BranchInfo
from services.remote_repo.remote_repo_interface import IRemoteRepo
from services.remote_repo.providers import (
    GitHubRepoLocator,
    GitLabRepoLocator,
    BitbucketRepoLocator,
)
from services.git.git_service import GitService

logger = logging.getLogger(__name__)


class RemoteRepoService:
    """
    Service class for locating and cloning repositories using different strategies.
    Uses constructor injection for config and auth services following SOLID principles.
    """
    def __init__(self, db: Session, session_service: SessionService):
        self.db = db
        self.user_dao = UserDAO(db)
        self.user_repos_dao = UserReposDAO(db)
        self.session_service = session_service
    
    async def get_repositories(
        self,
        user_id: str
    ) -> RepositoryList:
        """
        Get repositories for a given user based on the configured locator strategy.
        
        Args:
            user_id: The ID of the user to fetch repositories for.

        Returns:
            RepositoryList: A list of repository information.
        """
        try:
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found for ID: {user_id}")

            latest_session = self.session_service.get_active_session(user_id)
            if not latest_session:
                raise ValueError(f"No active session found for user ID: {user_id}")

            oauth_provider = user.oauth_provider
            oauth_token = latest_session.oauth_token
            oauth_username = user.oauth_username

        except ValueError as e:
            logger.error(f"Failed to retrieve user or session data: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
            raise

        if not oauth_provider or not oauth_token:
            raise ValueError(f"OAuth provider and token not configured for user {user_id}")
        
        locator: IRemoteRepo
        if oauth_provider.lower() == "github":
            locator = GitHubRepoLocator(oauth_token)
        elif oauth_provider.lower() == "gitlab":
            locator = GitLabRepoLocator(oauth_token)
        elif oauth_provider.lower() == "bitbucket":
            username = oauth_username
            if not username:
                raise ValueError(f"OAuth username not configured for user {user_id} with Bitbucket")
            locator = BitbucketRepoLocator(oauth_token, username)
        else:
            raise OAuthError(f"Unsupported provider: {oauth_provider}", oauth_provider)
        
        async with locator:
            return await locator.get_repositories()
    
    async def get_repository_branches(
        self,
        user_id: str,
        owner: str,
        repo: str
    ) -> RepositoryBranchesResponse:
        """
        Get branches for a specific repository.
        
        Args:
            user_id: The ID of the user to fetch branches for
            owner: Repository owner/organization
            repo: Repository name
        
        Returns:
            RepositoryBranchesResponse: Branch information for the repository
        """
        try:
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found for ID: {user_id}")

            latest_session = self.session_service.get_active_session(user_id)
            if not latest_session:
                raise ValueError(f"No active session found for user ID: {user_id}")

            oauth_provider = user.oauth_provider
            oauth_token = latest_session.oauth_token
            oauth_username = user.oauth_username

        except ValueError as e:
            logger.error(f"Failed to retrieve user or session data: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
            raise

        if not oauth_provider or not oauth_token:
            raise ValueError(f"OAuth provider and token not configured for user {user_id}")
        
        locator: IRemoteRepo
        if oauth_provider.lower() == "github":
            locator = GitHubRepoLocator(oauth_token)
        elif oauth_provider.lower() == "gitlab":
            locator = GitLabRepoLocator(oauth_token)
        elif oauth_provider.lower() == "bitbucket":
            username = oauth_username
            if not username:
                raise ValueError(f"OAuth username not configured for user {user_id} with Bitbucket")
            locator = BitbucketRepoLocator(oauth_token, username)
        else:
            raise OAuthError(f"Unsupported provider: {oauth_provider}", oauth_provider)
        
        async with locator:
            return await locator.get_repository_branches(owner, repo)
    
    def clone_user_repository(
        self,
        user_id: str,
        repo_id: str,
        oauth_token: Optional[str] = None
    ) -> bool:
        """
        Clone a repository for a user and update its status.
        
        Args:
            user_id: ID of the user
            repo_id: ID of the repository record in database
            oauth_token: Optional OAuth token for authentication
            
        Returns:
            bool: True if cloning was successful, False otherwise
        """
        try:
            # Get repository record
            repo = self.user_repos_dao.get_repository_by_id(repo_id)
            if not repo or repo.user_id != user_id:
                logger.error(f"Repository {repo_id} not found for user {user_id}")
                return False
            base_path = Path(settings.multi_user_repo_path) / user_id
            
            # Check if already cloned
            if repo.status == RepoStatus.CLONED and repo.local_path:
                local_path = Path(repo.local_path)
                if local_path.exists() and (local_path / ".git").exists():
                    logger.info(f"Repository {repo.repo_name} already cloned at {repo.local_path}")
                    return True
            
            # Mark as cloning
            self.user_repos_dao.update_repository_status(repo_id, RepoStatus.CLONING)
            self.db.commit()
            
            # Prepare clone path
            clone_path = base_path / repo.repo_name
            
            # Clone the repository
            git_service = GitService(clone_path)
            clone_result = git_service.clone_repository(
                clone_url=repo.repo_clone_url,
                branch=repo.branch,
                oauth_token=oauth_token
            )
            
            if clone_result.success:
                # Mark as cloned with local path
                self.user_repos_dao.update_repository_status(
                    repo_id,
                    RepoStatus.CLONED,
                    local_path=str(clone_path)
                )
                self.db.commit()
                logger.info(f"Successfully cloned {repo.repo_name} to {clone_path}")
                return True
            else:
                # Mark as failed with error message
                self.user_repos_dao.update_repository_status(
                    repo_id,
                    RepoStatus.FAILED,
                    error_message=clone_result.message
                )
                self.db.commit()
                logger.error(f"Failed to clone {repo.repo_name}: {clone_result.message}")
                return False
                
        except Exception as e:
            logger.error(f"Error cloning repository {repo_id}: {e}", exc_info=True)
            try:
                # Try to mark as failed
                self.user_repos_dao.update_repository_status(
                    repo_id,
                    RepoStatus.FAILED,
                    error_message=str(e)
                )
                self.db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update repository status: {db_error}")
                self.db.rollback()
            return False
