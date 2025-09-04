import git
import httpx
import asyncio
from git import Repo, GitCommandError
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


def checkout_new_branch(
        repo_path: str,
        branch_name: str,
        base_branch: str = "main",
        oauth_token: str = None
) -> bool:
    """
    Create and checkout a new branch.

    Args:
        repo_path: Local path to the git repository
        branch_name: Name of the new branch to create
        base_branch: Base branch to branch from (default: main)
        oauth_token: GitHub OAuth token for pulling latest (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"🔄 Creating new branch: {branch_name} from {base_branch}")

        # Initialize repository
        repo = Repo(repo_path)

        # Ensure we're on base branch and up to date
        if repo.active_branch.name != base_branch:
            repo.git.checkout(base_branch)

        # Pull latest changes if token provided
        if oauth_token:
            try:
                origin = repo.remote('origin')
                original_url = origin.url

                if oauth_token not in original_url:
                    authenticated_url = _add_token_to_url(original_url, oauth_token)
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
            return True
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

        logger.info(f"✅ Successfully created and checked out branch: {branch_name}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create branch {branch_name}: {e}")
        return False


def add_files(repo_path: str, files_to_add: Union[List[str], Dict[str, str]]) -> List[str]:
    """
    Add files to the repository staging area.

    Args:
        repo_path: Local path to the git repository
        files_to_add: Either:
            - List of existing file paths to stage
            - Dict of {file_path: content} to create and stage

    Returns:
        List[str]: List of successfully added file paths
    """
    added_files = []

    try:
        repo = Repo(repo_path)
        repo_path_obj = Path(repo_path)

        if isinstance(files_to_add, dict):
            logger.info(f"📝 Creating and adding {len(files_to_add)} new files")
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
            logger.info(f"📁 Staging {len(files_to_add)} existing files")
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

        logger.info(f"✅ Successfully added {len(added_files)} files")
        return added_files

    except Exception as e:
        logger.error(f"❌ Failed to add files: {e}")
        return added_files


def commit_changes(
        repo_path: str,
        commit_message: str,
        author_name: str = None,
        author_email: str = None
) -> str:
    """
    Commit the staged changes.

    Args:
        repo_path: Local path to the git repository
        commit_message: Commit message
        author_name: Git author name (optional)
        author_email: Git author email (optional)

    Returns:
        str: Commit hash if successful, empty string otherwise
    """
    try:
        logger.info(f"💾 Committing changes: {commit_message[:50]}...")

        repo = Repo(repo_path)

        # Configure git user if provided or not set
        _configure_git_user(repo, author_name, author_email)

        # Check if there are changes to commit
        if not repo.is_dirty() and not repo.untracked_files:
            logger.warning("⚠️  No changes to commit")
            return ""

        # Commit changes
        commit = repo.index.commit(commit_message)
        commit_hash = commit.hexsha

        logger.info(f"✅ Successfully committed: {commit_hash[:8]}")
        return commit_hash

    except Exception as e:
        logger.error(f"❌ Failed to commit changes: {e}")
        return ""


def push_branch(repo_path: str, oauth_token: str, branch_name: str = None) -> bool:
    """
    Push branch to remote repository.

    Args:
        repo_path: Local path to the git repository
        oauth_token: GitHub OAuth token for authentication
        branch_name: Name of branch to push (default: current branch)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        repo = Repo(repo_path)

        if branch_name is None:
            branch_name = repo.active_branch.name

        logger.info(f"🚀 Pushing branch to remote: {branch_name}")

        # Get remote origin
        origin = repo.remote('origin')

        # Configure remote URL with token for authentication
        original_url = origin.url
        if oauth_token not in original_url:
            authenticated_url = _add_token_to_url(original_url, oauth_token)
            origin.set_url(authenticated_url)

        # Push branch
        origin.push(refspec=f"{branch_name}:{branch_name}")

        # Reset URL for security
        if oauth_token in origin.url:
            origin.set_url(original_url)

        logger.info(f"✅ Successfully pushed branch: {branch_name}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to push branch {branch_name}: {e}")
        return False


async def create_pull_request(
        github_repo: str,
        oauth_token: str,
        head_branch: str,
        title: str,
        body: str = "",
        base_branch: str = "main",
        draft: bool = False
) -> Dict[str, any]:
    """
    Create a pull request via GitHub API.

    Args:
        github_repo: GitHub repository in format "owner/repo"
        oauth_token: GitHub OAuth token with repo permissions
        head_branch: Source branch for the PR
        title: Pull request title
        body: Pull request description
        base_branch: Target branch (default: main)
        draft: Create as draft PR (default: False)

    Returns:
        Dict with PR data including URL, or error info
    """
    try:
        logger.info(f"🔀 Creating pull request: {title}")

        headers = {
            "Authorization": f"Bearer {oauth_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubWorkflowAutomation/1.0"
        }

        pr_data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
            "draft": draft,
            "maintainer_can_modify": True
        }

        api_url = f"https://api.github.com/repos/{github_repo}/pulls"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=pr_data
            )

            if response.status_code == 201:
                pr_info = response.json()
                logger.info(f"✅ Successfully created PR #{pr_info['number']}: {pr_info['html_url']}")
                return {
                    "success": True,
                    "pr_number": pr_info["number"],
                    "pr_url": pr_info["html_url"],
                    "pr_id": pr_info["id"],
                    "data": pr_info
                }
            else:
                error_msg = f"PR creation failed: {response.status_code} {response.text}"
                logger.error(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Failed to create pull request: {e}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


# Utility functions

def get_repo_status(repo_path: str) -> Dict[str, any]:
    """
    Get detailed repository status.

    Args:
        repo_path: Local path to the git repository

    Returns:
        Dict with repository status information
    """
    try:
        repo = Repo(repo_path)
        return {
            "current_branch": repo.active_branch.name,
            "is_dirty": repo.is_dirty(),
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff("HEAD")],
            "commits_ahead": len(list(repo.iter_commits('origin/main..HEAD'))),
            "last_commit": {
                "hash": repo.head.commit.hexsha[:8],
                "message": repo.head.commit.message.strip(),
                "author": str(repo.head.commit.author),
                "date": repo.head.commit.committed_datetime.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get repo status: {e}")
        return {"error": str(e)}


def switch_branch(repo_path: str, branch_name: str) -> bool:
    """
    Switch to an existing branch.

    Args:
        repo_path: Local path to the git repository
        branch_name: Name of branch to switch to

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        repo = Repo(repo_path)
        repo.git.checkout(branch_name)
        logger.info(f"✅ Switched to branch: {branch_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to switch to branch {branch_name}: {e}")
        return False

def pull_latest(repo_path: str, oauth_token: str = None, branch_name: str = None) -> bool:
    """
    Pull latest changes from remote.

    Args:
        repo_path: Local path to the git repository
        oauth_token: GitHub OAuth token for authentication (optional)
        branch_name: Branch to pull (default: current branch)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        repo = Repo(repo_path)

        if branch_name:
            repo.git.checkout(branch_name)

        origin = repo.remote('origin')

        # Use OAuth token if provided
        if oauth_token:
            original_url = origin.url
            if oauth_token not in original_url:
                authenticated_url = _add_token_to_url(original_url, oauth_token)
                origin.set_url(authenticated_url)

        origin.pull()

        # Reset URL for security
        if oauth_token and oauth_token in origin.url:
            origin.set_url(original_url)

        current_branch = repo.active_branch.name
        logger.info(f"✅ Pulled latest changes for branch: {current_branch}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to pull latest changes: {e}")
        return False


# Private helper functions

def _add_token_to_url(url: str, oauth_token: str) -> str:
    """Add OAuth token to GitHub URL."""
    if url.startswith('https://github.com/'):
        return url.replace('https://github.com/', f'https://{oauth_token}@github.com/')
    return url


def _configure_git_user(repo: Repo, author_name: str = None, author_email: str = None):
    """Configure git user for commits."""
    try:
        with repo.config_writer() as git_config:
            if author_name:
                git_config.set_value("user", "name", author_name)
            elif not _get_git_config(repo, "user.name"):
                git_config.set_value("user", "name", "GitHub Automation")

            if author_email:
                git_config.set_value("user", "email", author_email)
            elif not _get_git_config(repo, "user.email"):
                git_config.set_value("user", "email", "automation@github.local")

    except Exception as e:
        logger.warning(f"Could not configure git user: {e}")


def _get_git_config(repo: Repo, key: str) -> str:
    """Get git config value."""
    try:
        section, option = key.split('.')
        return repo.config_reader().get_value(section, option)
    except:
        return ""