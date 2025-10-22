"""
Repository Cloning Service

This service ensures that all configured repositories are cloned before
attempting to discover prompts from them. It prevents infinite loops by
checking and cloning missing repositories.

This service orchestrates existing services (RemoteRepoService, UserReposDAO)
without duplicating their functionality, following SOLID principles.
"""

import logging
from pathlib import Path
from typing import List, Optional

from sqlmodel import Session
from database.daos.user.user_repos_dao import UserReposDAO
from database.models.user_repos import RepoStatus
from services.config.models import RepoConfig
from services.remote_repo.remote_repo_service import RemoteRepoService
from settings import settings
from schemas.hosting_type_enum import HostingType

logger = logging.getLogger(__name__)


class RepoCloningService:
    """
    Service to ensure repositories are cloned before discovery.
    
    This service orchestrates RemoteRepoService and UserReposDAO to ensure
    all configured repositories are available on the file system.
    """
    
    def __init__(
        self,
        db: Session,
        remote_repo_service: RemoteRepoService,
        hosting_type: HostingType
    ):
        """
        Initialize RepoCloningService with dependencies.
        
        Args:
            db: Database session
            remote_repo_service: Service for cloning repositories
            hosting_type: Type of hosting (individual/organization)
        """
        self.db = db
        self.remote_repo_service = remote_repo_service
        self.hosting_type = hosting_type
        self.user_repos_dao = UserReposDAO(db)
    
    def _get_repo_base_path(self, user_id: str) -> Path:
        """
        Get the base repository path based on hosting type.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Path object for the repository base directory
        """
        if self.hosting_type == HostingType.INDIVIDUAL:
            return Path(settings.local_repo_path)
        else:
            return Path(settings.multi_user_repo_path) / user_id
    
    def _check_repo_exists_on_filesystem(self, user_id: str, repo_name: str) -> bool:
        """
        Check if a repository exists on the file system with .git folder.
        
        Args:
            user_id: ID of the user
            repo_name: Name of the repository
            
        Returns:
            bool: True if repository exists, False otherwise
        """
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        # Check if directory exists and has .git folder
        return repo_path.exists() and (repo_path / ".git").exists()
    
    def ensure_repos_cloned(
        self,
        user_id: str,
        repo_configs: List[RepoConfig],
        oauth_token: Optional[str] = None
    ) -> List[str]:
        """
        Ensure all configured repositories are cloned.
        
        This method:
        1. Checks each repository on the file system
        2. Checks database status if not on filesystem
        3. Clones missing or failed repositories
        4. Returns list of available repositories
        
        Args:
            user_id: ID of the user
            repo_configs: List of repository configurations
            oauth_token: Optional OAuth token for authentication
            
        Returns:
            List[str]: List of repository names that are available
        """
        available_repos = []
        
        for repo_config in repo_configs:
            repo_name = repo_config.repo_name
            
            # First check: Is it already on the filesystem?
            if self._check_repo_exists_on_filesystem(user_id, repo_name):
                logger.info(f"Repository {repo_name} already exists for user {user_id}")
                available_repos.append(repo_name)
                continue
            
            # Second check: Get database status
            user_repos = self.user_repos_dao.get_user_repositories(user_id)
            existing_repo = next(
                (r for r in user_repos if r.repo_name == repo_name),
                None
            )
            
            if existing_repo:
                # Handle based on status
                if existing_repo.status == RepoStatus.CLONING:
                    logger.info(f"Repository {repo_name} is currently being cloned")
                    continue
                    
                elif existing_repo.status == RepoStatus.FAILED:
                    logger.warning(f"Repository {repo_name} failed previously, retrying...")
                    if self._clone_repository(user_id, existing_repo.id, oauth_token):
                        available_repos.append(repo_name)
                        
                elif existing_repo.status == RepoStatus.PENDING:
                    logger.info(f"Repository {repo_name} is pending, cloning now...")
                    if self._clone_repository(user_id, existing_repo.id, oauth_token):
                        available_repos.append(repo_name)
                        
                elif existing_repo.status == RepoStatus.CLONED:
                    # Status says cloned but file doesn't exist, reclone
                    logger.warning(f"Repository {repo_name} marked as cloned but files missing, recloning...")
                    if self._clone_repository(user_id, existing_repo.id, oauth_token):
                        available_repos.append(repo_name)
            else:
                # Repository not in DB, need to add and clone
                logger.info(f"Adding new repository {repo_name} for user {user_id}")
                try:
                    new_repo = self.user_repos_dao.add_repository(
                        user_id=user_id,
                        repo_clone_url=repo_config.repo_url,
                        repo_name=repo_name,
                        branch=repo_config.base_branch or "main"
                    )
                    
                    if self._clone_repository(user_id, new_repo.id, oauth_token):
                        available_repos.append(repo_name)
                except Exception as e:
                    logger.error(f"Failed to add repository {repo_name}: {e}")
        
        logger.info(f"Ensured {len(available_repos)} out of {len(repo_configs)} repos are available for user {user_id}")
        return available_repos
    
    def _clone_repository(
        self,
        user_id: str,
        repo_id: str,
        oauth_token: Optional[str] = None
    ) -> bool:
        """
        Clone a repository using the RemoteRepoService.
        
        Uses the existing RemoteRepoService.clone_user_repository method.
        
        Args:
            user_id: ID of the user
            repo_id: ID of the repository record
            oauth_token: Optional OAuth token for authentication
            
        Returns:
            bool: True if cloning was successful, False otherwise
        """
        try:
            # Use existing RemoteRepoService method
            success = self.remote_repo_service.clone_user_repository(
                user_id=user_id,
                repo_id=repo_id,
                oauth_token=oauth_token
            )
            
            if success:
                logger.info(f"Successfully cloned repository {repo_id}")
            else:
                logger.error(f"Failed to clone repository {repo_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error cloning repository {repo_id}: {e}", exc_info=True)
            return False