"""
Git Service Implementation

This module provides Git operations for repository management,
including branch management, file operations, commits, and pull requests.
"""

from git import Repo
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging

from services.local_repo.models import GitOperationResult, RepoStatus, CommitInfo

logger = logging.getLogger(__name__)


class GitService:
    """
    Service class for Git operations.
    """

    def __init__(self, repo_path: Union[str, Path]):
        """
        Initialize the Git service with a repository path.
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path) if isinstance(repo_path, str) else repo_path

    def checkout_new_branch(
            self,
            branch_name: str,
            base_branch: str = "main",
            oauth_token: Optional[str] = None
    ) -> GitOperationResult:
        """
        Create and checkout a new branch.

        Args:
            branch_name: Name of the new branch to create
            base_branch: Base branch to branch from (default: main)
            oauth_token: GitHub OAuth token for pulling latest (optional)

        Returns:
            GitOperationResult: Result of the operation
        """
        try:
            logger.info(f"Creating new branch: {branch_name} from {base_branch}")

            # Initialize repository
            repo = Repo(self.repo_path)

            # Ensure we're on base branch and up to date
            if repo.active_branch.name != base_branch:
                repo.git.checkout(base_branch)

            # Pull latest changes if token provided
            if oauth_token:
                try:
                    origin = repo.remote('origin')
                    original_url = origin.url

                    if oauth_token not in original_url:
                        authenticated_url = self._add_token_to_url(original_url, oauth_token)
                        origin.set_url(authenticated_url)

                    origin.pull()

                    # Reset URL for security
                    if oauth_token in origin.url:
                        origin.set_url(original_url)

                except Exception as e:
                    logger.warning(f"Could not pull latest changes: {e}")

            # Create and checkout new branch
            if branch_name in repo.heads:
                logger.warning(f"Branch {branch_name} already exists. Checking it out.")
                repo.git.checkout(branch_name)
                return GitOperationResult(
                    success=True,
                    message=f"Successfully checked out existing branch: {branch_name}"
                )
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()

            logger.info(f"Successfully created and checked out branch: {branch_name}")
            return GitOperationResult(
                success=True,
                message=f"Successfully created and checked out branch: {branch_name}"
            )

        except Exception as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to create branch {branch_name}: {e}"
            )

    def add_files(self, files_to_add: Union[List[str], Dict[str, str]]) -> GitOperationResult:
        """
        Add files to the repository staging area.

        Args:
            files_to_add: Either:
                - List of existing file paths to stage
                - Dict of {file_path: content} to create and stage

        Returns:
            GitOperationResult: Result of the operation
        """
        added_files = []

        try:
            repo = Repo(self.repo_path)
            repo_path_obj = self.repo_path

            if isinstance(files_to_add, dict):
                logger.info(f"Creating and adding {len(files_to_add)} new files")
                # Dict format: {file_path: content}
                for file_path, content in files_to_add.items():
                    try:
                        full_path = repo_path_obj / file_path

                        # Create directory if it doesn't exist
                        full_path.parent.mkdir(parents=True, exist_ok=True)

                        # Write content to file
                        if isinstance(content, str):
                            full_path.write_text(content, encoding='utf-8')
                        else:
                            full_path.write_bytes(content)

                        # Add to git
                        repo.index.add([file_path])
                        added_files.append(file_path)

                    except Exception as e:
                        logger.error(f"Failed to create/stage file {file_path}: {e}")

            elif isinstance(files_to_add, list):
                logger.info(f"Staging {len(files_to_add)} existing files")
                # List format: [file_paths] - files must already exist
                for file_path in files_to_add:
                    try:
                        full_path = repo_path_obj / file_path
                        if full_path.exists():
                            repo.index.add([file_path])
                            added_files.append(file_path)
                        else:
                            logger.warning(f"File not found, skipping: {file_path}")

                    except Exception as e:
                        logger.error(f"Failed to stage file {file_path}: {e}")

            logger.info(f"Successfully added {len(added_files)} files")
            return GitOperationResult(
                success=True,
                message=f"Successfully added {len(added_files)} files",
                data={"added_files": added_files}
            )

        except Exception as e:
            logger.error(f"Failed to add files: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to add files: {e}",
                data={"added_files": added_files}
            )

    def commit_changes(
            self,
            commit_message: str,
            author_name: Optional[str] = None,
            author_email: Optional[str] = None
    ) -> GitOperationResult:
        """
        Commit the staged changes.

        Args:
            commit_message: Commit message
            author_name: Git author name (optional)
            author_email: Git author email (optional)

        Returns:
            GitOperationResult: Result of the operation
        """
        try:
            logger.info(f"Committing changes: {commit_message[:50]}...")

            repo = Repo(self.repo_path)

            # Configure git user if provided or not set
            self._configure_git_user(repo, author_name, author_email)

            # Check if there are changes to commit
            if not repo.is_dirty() and not repo.untracked_files:
                logger.warning("No changes to commit")
                return GitOperationResult(
                    success=False,
                    message="No changes to commit"
                )

            # Commit changes
            commit = repo.index.commit(commit_message)
            commit_hash = commit.hexsha

            logger.info(f"Successfully committed: {commit_hash[:8]}")
            return GitOperationResult(
                success=True,
                message=f"Successfully committed: {commit_hash[:8]}",
                data={"commit_hash": commit_hash}
            )

        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to commit changes: {e}"
            )

    def push_branch(self, oauth_token: str, branch_name: Optional[str], repo_url: str) -> GitOperationResult:
        """
        Push branch to remote repository.

        Args:
            oauth_token: GitHub OAuth token for authentication
            branch_name: Name of branch to push (default: current branch)
            repo_url: Repository URL from config

        Returns:
            GitOperationResult: Result of the operation
        """
        try:
            repo = Repo(self.repo_path)

            if branch_name is None:
                branch_name = repo.active_branch.name

            logger.info(f"Pushing branch to remote: {branch_name}")

            # Clean the URL (remove any existing auth and normalize)
            clean_url = repo_url
            if '@github.com' in clean_url:
                # Extract the part after @github.com
                clean_url = 'https://github.com/' + clean_url.split('@github.com/')[-1]
            
            # Remove trailing slashes and .git if present, then add .git
            clean_url = clean_url.rstrip('/')
            if not clean_url.endswith('.git'):
                clean_url = clean_url + '.git'
            
            authenticated_url = self._add_token_to_url(clean_url, oauth_token)

            # Push branch directly to the authenticated URL
            # This bypasses the remote config and pushes directly to the URL
            repo.git.push(authenticated_url, f"{branch_name}:{branch_name}")

            logger.info(f"Successfully pushed branch: {branch_name}")
            return GitOperationResult(
                success=True,
                message=f"Successfully pushed branch: {branch_name}"
            )

        except Exception as e:
            logger.error(f"Failed to push branch {branch_name}: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to push branch {branch_name}: {e}"
            )

    def get_repo_status(self) -> RepoStatus:
        """
        Get detailed repository status.

        Returns:
            RepoStatus: Repository status information
        """
        try:
            repo = Repo(self.repo_path)
            # Check if remote origin exists before trying to compare with it
            commits_ahead = 0
            try:
                if 'origin' in repo.remotes:
                    commits_ahead = len(list(repo.iter_commits('origin/main..HEAD')))
            except Exception:
                # If comparison with remote fails, just assume we're up to date
                commits_ahead = 0
                
            return RepoStatus(
                current_branch=repo.active_branch.name,
                is_dirty=repo.is_dirty(),
                untracked_files=repo.untracked_files or [],
                modified_files=[item.a_path for item in repo.index.diff(None) if item.a_path is not None],
                staged_files=[item.a_path for item in repo.index.diff("HEAD") if item.a_path is not None],
                commits_ahead=commits_ahead,
                last_commit={
                    "hash": repo.head.commit.hexsha[:8],
                    "message": repo.head.commit.message.strip(),
                    "author": str(repo.head.commit.author),
                    "date": repo.head.commit.committed_datetime.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to get repo status: {e}")
            return RepoStatus(
                current_branch="",
                is_dirty=False,
                untracked_files=[],
                modified_files=[],
                staged_files=[],
                commits_ahead=0,
                last_commit={},
                error=str(e)
            )

    def switch_branch(self, branch_name: str) -> GitOperationResult:
        """
        Switch to an existing branch.

        Args:
            branch_name: Name of branch to switch to

        Returns:
            GitOperationResult: Result of the operation
        """
        try:
            repo = Repo(self.repo_path)
            repo.git.checkout(branch_name)
            logger.info(f"Switched to branch: {branch_name}")
            return GitOperationResult(
                success=True,
                message=f"Switched to branch: {branch_name}"
            )
        except Exception as e:
            logger.error(f"Failed to switch to branch {branch_name}: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to switch to branch {branch_name}: {e}"
            )

    def pull_latest(self, oauth_token: Optional[str] = None, branch_name: Optional[str] = None, force: bool = False) -> GitOperationResult:
        """
        Pull latest changes from remote.

        Args:
            oauth_token: GitHub OAuth token for authentication (optional)
            branch_name: Branch to pull (default: current branch)
            force: Whether to force pull and discard local changes (default: False)

        Returns:
            GitOperationResult: Result of the operation
        """
        try:
            repo = Repo(self.repo_path)
            if branch_name:
                repo.git.checkout(branch_name)

            current_branch = repo.active_branch.name
            origin = repo.remote('origin')

            # Use OAuth token if provided
            if oauth_token:
                original_url = origin.url
                if oauth_token not in original_url:
                    authenticated_url = self._add_token_to_url(original_url, oauth_token)
                    origin.set_url(authenticated_url)

            # Force pull if requested (discards local changes)
            if force:
                # Stash local changes first
                repo.git.stash('-u', '-m', 'Stashing local changes before getting latest')

            origin.pull()

            # Reset URL for security
            original_url = origin.url  # Ensure original_url is defined
            if oauth_token and oauth_token in origin.url:
                origin.set_url(original_url)

            action = "Force pulled" if force else "Pulled"
            return GitOperationResult(
                success=True,
                message=f"{action} latest changes for branch: {current_branch}"
            )

        except Exception as e:
            logger.error(f"Failed to pull latest changes: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to pull latest changes: {e}"
            )

    def clone_repository(
            self,
            clone_url: str,
            branch: Optional[str] = None,
            oauth_token: Optional[str] = None
    ) -> GitOperationResult:
        """
        Clone a repository from a remote URL.

        Args:
            clone_url: Git clone URL
            branch: Optional branch to checkout (default: main/master)
            oauth_token: Optional OAuth token for authentication

        Returns:
            GitOperationResult: Result of the operation
        """
        try:
            logger.info(f"Cloning repository from {clone_url}")

            # Add OAuth token to URL if provided
            authenticated_url = clone_url
            if oauth_token:
                authenticated_url = self._add_token_to_url(clone_url, oauth_token)

            # Ensure parent directory exists
            self.repo_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone the repository
            repo = Repo.clone_from(authenticated_url, self.repo_path)

            # Checkout specific branch if provided
            if branch and branch != repo.active_branch.name:
                try:
                    repo.git.checkout(branch)
                    logger.info(f"Checked out branch: {branch}")
                except Exception as e:
                    logger.warning(f"Could not checkout branch {branch}: {e}")

            logger.info(f"Successfully cloned repository to {self.repo_path}")
            return GitOperationResult(
                success=True,
                message=f"Successfully cloned repository to {self.repo_path}",
                data={"repo_path": str(self.repo_path)}
            )

        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            return GitOperationResult(
                success=False,
                message=f"Failed to clone repository: {e}"
            )

    # Private helper methods

    def _add_token_to_url(self, url: str, oauth_token: str) -> str:
        """Add OAuth token to GitHub URL."""
        if url.startswith('https://github.com/'):
            # Remove .git suffix temporarily
            clean_url = url
            if clean_url.endswith('.git'):
                clean_url = clean_url[:-4]
            
            # Extract repo path (owner/repo)
            repo_path = clean_url.replace('https://github.com/', '').rstrip('/')
            
            # GitHub requires x-access-token: prefix for OAuth tokens in HTTPS URLs
            return f'https://x-access-token:{oauth_token}@github.com/{repo_path}.git'
        return url

    def _configure_git_user(self, repo: Repo, author_name: Optional[str] = None, author_email: Optional[str] = None):
        """Configure git user for commits."""
        try:
            with repo.config_writer() as git_config:
                if author_name:
                    git_config.set_value("user", "name", author_name)
                elif not self._get_git_config(repo, "user.name"):
                    git_config.set_value("user", "name", "GitHub Automation")

                if author_email:
                    git_config.set_value("user", "email", author_email)
                elif not self._get_git_config(repo, "user.email"):
                    git_config.set_value("user", "email", "automation@github.local")

        except Exception as e:
            logger.warning(f"Could not configure git user: {e}")

    def _get_git_config(self, repo: Repo, key: str) -> Optional[str]:
        """Get git config value."""
        try:
            section, option = key.split('.')
            value = repo.config_reader().get_value(section, option)
            return str(value) if value is not None else None
        except:
            return None

    def get_current_branch(self) -> Optional[str]:
        """
        Get the name of the current branch.
        
        Returns:
            Optional[str]: Current branch name or None if unable to determine
        """
        try:
            repo = Repo(self.repo_path)
            return repo.active_branch.name
        except Exception as e:
            logger.error(f"Failed to get current branch: {e}")
            return None

    def get_file_commit_history(self, file_path: str, limit: int = 5) -> List[CommitInfo]:
        """
        Get commit history for a specific file.
        
        Args:
            file_path: Path to the file relative to repository root
            limit: Maximum number of commits to retrieve (default: 5)
            
        Returns:
            List[CommitInfo]: List of commit information for the file
        """
        try:
            repo = Repo(self.repo_path)
            commits = list(repo.iter_commits(paths=file_path, max_count=limit))
            
            commit_info_list = []
            for commit in commits:
                # Handle message - ensure it's a string
                message = commit.message
                if isinstance(message, bytes):
                    message = message.decode('utf-8', errors='replace')
                elif not isinstance(message, str):
                    message = str(message)
                
                commit_info = CommitInfo(
                    commit_id=commit.hexsha,
                    message=message.strip(),
                    author=str(commit.author),
                    timestamp=commit.committed_datetime
                )
                commit_info_list.append(commit_info)
            
            logger.info(f"Retrieved {len(commit_info_list)} commits for file: {file_path}")
            return commit_info_list
            
        except Exception as e:
            logger.warning(f"Failed to get commit history for {file_path}: {e}")
            return []