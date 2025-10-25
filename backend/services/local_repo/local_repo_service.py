"""
Local Repository Service

This service handles git workflow operations for local repositories,
including automatic branch creation, commits, and pushes when saving prompts.
Also handles repository cloning and ensuring repositories are available.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
import uuid

from services.local_repo.models import PRInfo

from sqlmodel import Session
from database.daos.user.user_repos_dao import UserReposDAO
from database.models.user_repos import RepoStatus
from middlewares.rest.exceptions import AppException, NotFoundException
from services.config.config_service import ConfigService
from services.config.models import RepoConfig
from services.local_repo.git_service import GitService
from schemas.hosting_type_enum import HostingType
from settings import settings

if TYPE_CHECKING:
    from services.remote_repo.remote_repo_service import RemoteRepoService

logger = logging.getLogger(__name__)


class LocalRepoService:
    """
    Service for handling local repository operations.
    
    This service manages git workflows such as:
    - Automatic branch creation when on base branch
    - File staging and commits
    - Pushing changes to remote
    - Ensuring repositories are cloned before operations
    """
    
    def __init__(
        self,
        config_service: ConfigService,
        db: Optional[Session] = None,
        remote_repo_service: Optional["RemoteRepoService"] = None
    ):
        """
        Initialize LocalRepoService with dependencies.
        
        Args:
            config_service: Configuration service for getting repo configs
            db: Optional database session for cloning operations
            remote_repo_service: Optional remote repo service for cloning and PR operations
        """
        self.config_service = config_service
        self.db = db
        self.remote_repo_service = remote_repo_service
        if db:
            self.user_repos_dao = UserReposDAO(db)
        else:
            self.user_repos_dao = None
    
    def _get_repo_base_path(self, user_id: str) -> Path:
        """
        Get the base repository path based on hosting type.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Path object for the repository base directory
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
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
        if not self.user_repos_dao or not self.remote_repo_service:
            raise ValueError("Database session and remote_repo_service required for cloning operations")
        
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
        if not self.remote_repo_service:
            raise ValueError("remote_repo_service required for cloning operations")
        
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
    
    async def handle_git_workflow_after_save(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Optional[PRInfo]:
        """
        Handle git workflow after saving a prompt file.
        
        If current branch is same as base branch:
        1. Create a new branch (with prompt name in branch name)
        2. Stage the file
        3. Commit changes
        4. Push to remote
        5. Create PR if possible
        
        If current branch is different from base branch:
        1. Stage the file
        2. Commit changes
        3. Push to remote
        4. Create PR if possible
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: File path relative to repository root
            oauth_token: Optional OAuth token for authentication
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Optional[PRInfo]: PR info if PR was created, None otherwise
        """
        try:
            # Get base branch and repo URL from repo config
            base_branch = self.config_service.get_base_branch_for_repo(user_id, repo_name)
            repo_url = self.config_service.get_repo_url_for_repo(user_id, repo_name)
            
            # Get repository path
            repo_base_path = self._get_repo_base_path(user_id)
            repo_path = repo_base_path / repo_name
            
            # Initialize git service
            git_service = GitService(repo_path)
            
            # Get current branch
            current_branch = git_service.get_current_branch()
            if not current_branch:
                logger.warning(f"Could not determine current branch for {repo_name}")
                return None
            
            # Extract prompt name from file path (remove extension and path)
            prompt_name = Path(file_path).stem.replace('_', '-').replace(' ', '-')
            
            # Check if current branch is same as base branch
            if current_branch == base_branch:
                logger.info(f"Current branch '{current_branch}' is same as base branch, creating new branch and committing changes")
                
                # Generate new branch name with prompt name
                timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
                short_uuid = str(uuid.uuid4())[:8]
                new_branch_name = f"update-{prompt_name}-{timestamp}-{short_uuid}"
                
                # Create and checkout new branch
                branch_result = git_service.checkout_new_branch(
                    branch_name=new_branch_name,
                    base_branch=base_branch,
                    oauth_token=oauth_token
                )
                
                if not branch_result.success:
                    logger.error(f"Failed to create branch {new_branch_name}: {branch_result.message}")
                    return None
                
                # Update current_branch to the new branch for commit/push
                current_branch = new_branch_name
            else:
                # Already on a feature branch, just commit and push
                logger.info(f"Current branch '{current_branch}' is different from base branch '{base_branch}', committing and pushing to existing branch")
            
            # Stage the file
            add_result = git_service.add_files([file_path])
            if not add_result.success:
                logger.error(f"Failed to stage file {file_path}: {add_result.message}")
                return None
            
            # Commit changes with user information
            commit_message = f"Update prompt: {file_path}"
            commit_result = git_service.commit_changes(
                commit_message=commit_message,
                author_name=author_name,
                author_email=author_email
            )
            if not commit_result.success:
                logger.error(f"Failed to commit changes: {commit_result.message}")
                return None
            
            # Validate required parameters for push
            if not oauth_token:
                raise AppException(
                    message="OAuth token is required for pushing changes to remote repository",
                    context={"repo_name": repo_name, "branch": current_branch}
                )
            
            if not repo_url:
                raise NotFoundException(
                    resource="Repository URL",
                    identifier=repo_name,
                    context={"message": "Repository URL not found in configuration"}
                )
            
            # Push to remote
            push_result = git_service.push_branch(oauth_token, current_branch, repo_url)
            if not push_result.success:
                logger.error(f"Failed to push branch {current_branch}: {push_result.message}")
                raise AppException(
                    message=f"Failed to push changes to remote: {push_result.message}",
                    context={"repo_name": repo_name, "branch": current_branch}
                )
            
            logger.info(f"Successfully pushed changes to branch {current_branch}")
            
            # Create PR if we're on a new branch and have remote repo service
            if self.remote_repo_service and user_session and current_branch != base_branch:
                try:
                    # Extract owner and repo from repo_name (format: owner/repo)
                    repo_parts = repo_name.split('/')
                    if len(repo_parts) == 2:
                        owner, repo = repo_parts
                        
                        # Generate PR title and body
                        pr_title = f"Update {file_path}"
                        pr_body = f"Automated update to prompt file: {file_path}"
                        
                        # Create PR if it doesn't exist
                        pr_result = await self.remote_repo_service.create_pull_request_if_not_exists(
                            user_session=user_session,
                            owner=owner,
                            repo=repo,
                            head_branch=current_branch,
                            title=pr_title,
                            body=pr_body,
                            base_branch=base_branch,
                            draft=False
                        )
                        
                        if pr_result.success and pr_result.pr_number and pr_result.pr_url and pr_result.pr_id:
                            logger.info(f"PR created/found: {pr_result.pr_url}")
                            # Return PR info
                            return PRInfo(
                                pr_number=pr_result.pr_number,
                                pr_url=pr_result.pr_url,
                                pr_id=pr_result.pr_id
                            )
                        else:
                            logger.warning(f"Failed to create PR: {pr_result.error}")
                    else:
                        logger.warning(f"Invalid repo_name format: {repo_name}, expected 'owner/repo'")
                except Exception as pr_error:
                    logger.error(f"Error creating PR: {pr_error}", exc_info=True)
            
            # No PR created (on base branch or PR creation failed)
            return None
                
        except Exception as e:
            logger.error(f"Error in git workflow after save: {e}", exc_info=True)
            return None
    
    async def get_latest_base_branch_content(
        self,
        user_id: str,
        repo_name: str,
        oauth_token: Optional[str] = None
    ) -> dict:
        """
        Get the latest content from the base branch of a repository.
        
        This method will:
        1. Switch to the base branch
        2. Pull the latest changes from remote
        3. Return success status
        
        Any local changes will be stashed before pulling.
        
        Args:
            user_id: ID of the user
            repo_name: Name of the repository
            oauth_token: OAuth token for authentication
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Get base branch from config
            base_branch = self.config_service.get_base_branch_for_repo(user_id, repo_name)
            
            # Get repository path
            repo_base_path = self._get_repo_base_path(user_id)
            repo_path = repo_base_path / repo_name
            
            if not (repo_path.exists() and (repo_path / ".git").exists()):
                logger.warning(f"Repository {repo_name} not found at {repo_path}")
                return {"success": False, "message": f"Repository {repo_name} not found or not a git repository"}
            
            # Initialize git service
            git_service = GitService(repo_path)
            
            # Get current branch
            current_branch = git_service.get_current_branch()
            if not current_branch:
                logger.warning(f"Could not determine current branch for {repo_name}")
                return {"success": False, "message": "Could not determine current branch"}
            
            # Switch to base branch if not already on it
            if current_branch != base_branch:
                switch_result = git_service.switch_branch(base_branch)
                if not switch_result.success:
                    logger.error(f"Failed to switch to base branch {base_branch}: {switch_result.message}")
                    return {"success": False, "message": f"Failed to switch to base branch: {switch_result.message}"}
            
            # Pull latest changes from base branch (force to discard local changes)
            pull_result = git_service.pull_latest(oauth_token=oauth_token, branch_name=base_branch, force=True)
            if not pull_result.success:
                logger.error(f"Failed to pull latest changes: {pull_result.message}")
                return {"success": False, "message": f"Failed to pull latest changes: {pull_result.message}"}
            
            return {"success": True, "message": f"Successfully fetched latest content from {repo_name}"}
            
        except Exception as e:
            logger.error(f"Error getting latest base branch content for {repo_name}: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}