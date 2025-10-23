"""
Remote Repository Service

This module provides the main service for managing remote repositories,
including fetching repository lists and branch information.
"""

import logging
from pathlib import Path
from typing import Optional

from sqlmodel import Session
from database.models.user_sessions import UserSessions
from settings import settings
from services.oauth.models import OAuthError
from database.daos.user.user_dao import UserDAO
from database.daos.user.user_repos_dao import UserReposDAO
from database.models.user_repos import RepoStatus
from services.remote_repo.models import RepositoryList, RepositoryBranchesResponse, PullRequestResult
from services.remote_repo.remote_repo_interface import IRemoteRepo
from services.remote_repo.providers import (
    GitHubRepoLocator,
    GitLabRepoLocator,
    BitbucketRepoLocator,
)
from services.local_repo.git_service import GitService

logger = logging.getLogger(__name__)


class RemoteRepoService:
    """
    Service class for locating and cloning repositories using different strategies.
    Uses constructor injection for config and auth services following SOLID principles.
    """
    def __init__(self, db: Session):
        self.db = db
        self.user_dao = UserDAO(db)
        self.user_repos_dao = UserReposDAO(db)
    
    async def get_repositories(
        self,
        user_session: UserSessions
    ) -> RepositoryList:
        """
        Get repositories for a given user based on the configured locator strategy.
        
        Args:
            user_id: The ID of the user to fetch repositories for.

        Returns:
            RepositoryList: A list of repository information.
        """
        try:
            user = self.user_dao.get_user_by_id(user_session.user_id)
            if not user:
                raise ValueError(f"User not found for ID: {user_session.user_id}")

            oauth_provider = user.oauth_provider
            oauth_token = user_session.oauth_token
            oauth_username = user.oauth_username

        except ValueError as e:
            logger.error(f"Failed to retrieve user or session data: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
            raise

        if not oauth_provider or not oauth_token:
            raise ValueError(f"OAuth provider and token not configured for user {user_session.user_id}")
        
        locator: IRemoteRepo
        if oauth_provider.lower() == "github":
            locator = GitHubRepoLocator(oauth_token)
        elif oauth_provider.lower() == "gitlab":
            locator = GitLabRepoLocator(oauth_token)
        elif oauth_provider.lower() == "bitbucket":
            username = oauth_username
            if not username:
                raise ValueError(f"OAuth username not configured for user {user_session.user_id} with Bitbucket")
            locator = BitbucketRepoLocator(oauth_token, username)
        else:
            raise OAuthError(f"Unsupported provider: {oauth_provider}", oauth_provider)
        
        async with locator:
            return await locator.get_repositories()
    
    async def get_repository_branches(
        self,
        user_session: UserSessions,
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
            user = self.user_dao.get_user_by_id(user_session.user_id)
            if not user:
                raise ValueError(f"User not found for ID: {user_session.user_id}")

            oauth_provider = user.oauth_provider
            oauth_token = user_session.oauth_token
            oauth_username = user.oauth_username

        except ValueError as e:
            logger.error(f"Failed to retrieve user or session data: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
            raise

        if not oauth_provider or not oauth_token:
            raise ValueError(f"OAuth provider and token not configured for user {user_session.user_id}")
        
        locator: IRemoteRepo
        if oauth_provider.lower() == "github":
            locator = GitHubRepoLocator(oauth_token)
        elif oauth_provider.lower() == "gitlab":
            locator = GitLabRepoLocator(oauth_token)
        elif oauth_provider.lower() == "bitbucket":
            username = oauth_username
            if not username:
                raise ValueError(f"OAuth username not configured for user {user_session.user_id} with Bitbucket")
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
    
    async def create_pull_request_if_not_exists(
        self,
        user_session: UserSessions,
        owner: str,
        repo: str,
        head_branch: str,
        title: str,
        body: str = "",
        base_branch: str = "main",
        draft: bool = False
    ) -> PullRequestResult:
        """
        Create a pull request only if it doesn't already exist.
        
        Args:
            user_session: User session containing OAuth credentials
            owner: Repository owner/organization
            repo: Repository name
            head_branch: Source branch for the PR
            title: Pull request title
            body: Pull request description
            base_branch: Target branch (default: main)
            draft: Create as draft PR (default: False)
            
        Returns:
            PullRequestResult: Result of the operation
        """
        try:
            user = self.user_dao.get_user_by_id(user_session.user_id)
            if not user:
                raise ValueError(f"User not found for ID: {user_session.user_id}")

            oauth_provider = user.oauth_provider
            oauth_token = user_session.oauth_token
            oauth_username = user.oauth_username

        except ValueError as e:
            logger.error(f"Failed to retrieve user or session data: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
            raise

        if not oauth_provider or not oauth_token:
            raise ValueError(f"OAuth provider and token not configured for user {user_session.user_id}")
        
        locator: IRemoteRepo
        if oauth_provider.lower() == "github":
            locator = GitHubRepoLocator(oauth_token)
        elif oauth_provider.lower() == "gitlab":
            locator = GitLabRepoLocator(oauth_token)
        elif oauth_provider.lower() == "bitbucket":
            username = oauth_username
            if not username:
                raise ValueError(f"OAuth username not configured for user {user_session.user_id} with Bitbucket")
            locator = BitbucketRepoLocator(oauth_token, username)
        else:
            raise OAuthError(f"Unsupported provider: {oauth_provider}", oauth_provider)
        
        async with locator:
            # Check if PR already exists
            existing_pr = await locator.check_existing_pull_request(
                owner=owner,
                repo=repo,
                head_branch=head_branch,
                base_branch=base_branch
            )
            
            if existing_pr.success:
                logger.info(f"PR already exists: {existing_pr.pr_url}")
                return existing_pr
            
            # Create new PR
            logger.info(f"Creating new PR from {head_branch} to {base_branch}")
            return await locator.create_pull_request(
                owner=owner,
                repo=repo,
                head_branch=head_branch,
                title=title,
                body=body,
                base_branch=base_branch,
                draft=draft
            )
