"""
Service for managing user repositories in the database.
Handles CRUD operations for the user_repos table.
"""
from sqlmodel import Session, select
from database.models import UserRepos, RepoStatus
from database.daos.user.models import RepositoryStatusCount
from datetime import datetime, UTC
from typing import Optional, List
import logging
import os

logger = logging.getLogger(__name__)


class UserReposDAO:
    """Service for managing user repositories."""

    def __init__(self, db: Session):
        """
        Initialize UserReposDAO with database session.

        Args:
            db: Database session
        """
        self.db = db

    def add_repository(
        self,
        user_id: str,
        repo_clone_url: str,
        repo_name: str,
        branch: str = "main"
    ) -> UserRepos:
        """
        Add a new repository for a user.

        Args:
            user_id: ID of the user
            repo_clone_url: Git clone URL
            repo_name: Repository name (e.g., 'owner/repo-name')
            branch: Target branch (defaults to 'main')

        Returns:
            Created UserRepos object

        Raises:
            Exception: If repository already exists or creation fails
        """
        try:
            # Check if repository already exists for this user
            existing_repo = self.get_repository_by_url(user_id, repo_clone_url)
            if existing_repo:
                raise ValueError(f"Repository {repo_name} already exists for user {user_id}")

            # Create new repository record
            user_repo = UserRepos(
                user_id=user_id,
                repo_clone_url=repo_clone_url,
                repo_name=repo_name,
                branch=branch,
                status=RepoStatus.PENDING
            )

            # Save to database
            self.db.add(user_repo)
            self.db.commit()
            self.db.refresh(user_repo)

            logger.info(f"Added repository {repo_name} for user {user_id}")
            return user_repo

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add repository {repo_name} for user {user_id}: {e}")
            raise

    def get_repository_by_id(self, repo_id: str) -> Optional[UserRepos]:
        """
        Get repository by its ID.

        Args:
            repo_id: Repository ID

        Returns:
            UserRepos object if found, None otherwise
        """
        try:
            statement = select(UserRepos).where(UserRepos.id == repo_id)
            return self.db.exec(statement).first()
        except Exception as e:
            logger.error(f"Failed to get repository {repo_id}: {e}")
            return None

    def get_repository_by_url(
        self,
        user_id: str,
        repo_clone_url: str
    ) -> Optional[UserRepos]:
        """
        Get repository by user ID and clone URL.

        Args:
            user_id: User ID
            repo_clone_url: Repository clone URL

        Returns:
            UserRepos object if found, None otherwise
        """
        try:
            statement = select(UserRepos).where(
                UserRepos.user_id == user_id,
                UserRepos.repo_clone_url == repo_clone_url
            )
            return self.db.exec(statement).first()
        except Exception as e:
            logger.error(f"Failed to get repository by URL for user {user_id}: {e}")
            return None

    def get_user_repositories(self, user_id: str) -> List[UserRepos]:
        """
        Get all repositories for a user.

        Args:
            user_id: User ID

        Returns:
            List of UserRepos objects
        """
        try:
            statement = select(UserRepos).where(UserRepos.user_id == user_id)
            return list(self.db.exec(statement).all())
        except Exception as e:
            logger.error(f"Failed to get repositories for user {user_id}: {e}")
            return []

    def get_repositories_by_status(
        self,
        status: RepoStatus,
        user_id: Optional[str] = None
    ) -> List[UserRepos]:
        """
        Get repositories by status, optionally filtered by user.

        Args:
            status: Repository status to filter by
            user_id: Optional user ID to filter by

        Returns:
            List of UserRepos objects
        """
        try:
            statement = select(UserRepos).where(UserRepos.status == status)
            if user_id:
                statement = statement.where(UserRepos.user_id == user_id)
            return list(self.db.exec(statement).all())
        except Exception as e:
            logger.error(f"Failed to get repositories by status {status}: {e}")
            return []

    def update_repository_status(
        self,
        repo_id: str,
        status: RepoStatus,
        local_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[UserRepos]:
        """
        Update repository status and related fields.

        Args:
            repo_id: Repository ID
            status: New status
            local_path: Optional local path (for successful clones)
            error_message: Optional error message (for failed clones)

        Returns:
            Updated UserRepos object or None if not found
        """
        try:
            user_repo = self.get_repository_by_id(repo_id)
            if not user_repo:
                logger.warning(f"Repository {repo_id} not found for status update")
                return None

            # Update status
            user_repo.status = status
            user_repo.updated_at = datetime.now(UTC)

            # Update specific fields based on status
            if status == RepoStatus.CLONING:
                user_repo.last_clone_attempt = datetime.now(UTC)
                user_repo.clone_error_message = None
            elif status == RepoStatus.CLONED:
                user_repo.local_path = local_path
                user_repo.clone_error_message = None
            elif status == RepoStatus.FAILED:
                user_repo.clone_error_message = error_message

            # Save changes
            self.db.add(user_repo)
            self.db.commit()
            self.db.refresh(user_repo)

            logger.info(f"Updated repository {repo_id} status to {status}")
            return user_repo

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update repository {repo_id} status: {e}")
            raise

    def delete_repository(self, repo_id: str) -> bool:
        """
        Delete a repository record.

        Args:
            repo_id: Repository ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            user_repo = self.get_repository_by_id(repo_id)
            if not user_repo:
                logger.warning(f"Repository {repo_id} not found for deletion")
                return False

            # Optional: Clean up local files if they exist
            if user_repo.local_path and os.path.exists(user_repo.local_path):
                logger.info(f"Local repository files still exist at {user_repo.local_path}")
                # You might want to add file cleanup logic here

            self.db.delete(user_repo)
            self.db.commit()

            logger.info(f"Deleted repository {repo_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete repository {repo_id}: {e}")
            return False

    def get_pending_clones(self, limit: Optional[int] = None) -> List[UserRepos]:
        """
        Get repositories that are pending clone.
        Useful for background job processing.

        Args:
            limit: Optional limit on number of results

        Returns:
            List of UserRepos objects with PENDING status
        """
        try:
            statement = select(UserRepos).where(UserRepos.status == RepoStatus.PENDING)
            if limit:
                statement = statement.limit(limit)
            return list(self.db.exec(statement).all())
        except Exception as e:
            logger.error(f"Failed to get pending clone repositories: {e}")
            return []

    def count_repositories_by_status(self, user_id: str) -> RepositoryStatusCount:
        """
        Get count of repositories by status for a user.

        Args:
            user_id: User ID

        Returns:
            RepositoryStatusCount object with status counts
        """
        try:
            result = {}
            for status in RepoStatus:
                statement = select(UserRepos).where(
                    UserRepos.user_id == user_id,
                    UserRepos.status == status
                )
                count = len(list(self.db.exec(statement).all()))
                result[status] = count
            return RepositoryStatusCount(status_counts=result)
        except Exception as e:
            logger.error(f"Failed to count repositories by status for user {user_id}: {e}")
            return RepositoryStatusCount(status_counts={})

    def update_repository_path(self, repo_id: str, local_path: str) -> bool:
        """
        Update the local path of a repository.

        Args:
            repo_id: Repository ID
            local_path: New local path

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            user_repo = self.get_repository_by_id(repo_id)
            if not user_repo:
                return False

            user_repo.local_path = local_path
            user_repo.updated_at = datetime.now(UTC)

            self.db.add(user_repo)
            self.db.commit()
            self.db.refresh(user_repo)

            logger.info(f"Updated repository {repo_id} local path to {local_path}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update repository {repo_id} local path: {e}")
            return False