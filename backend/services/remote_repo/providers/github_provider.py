"""
GitHub Repository Provider

This module implements the IRemoteRepo interface for GitHub repositories.
"""

import httpx
import logging

from services.remote_repo.remote_repo_interface import IRemoteRepo
from services.remote_repo.models import (
    RepoInfo,
    RepositoryList,
    BranchInfo,
    RepositoryBranchesResponse,
    PullRequestResult,
    PullRequestInfo
)
from services.oauth.models import OAuthError

logger = logging.getLogger(__name__)


class GitHubRepoLocator(IRemoteRepo):
    """
    GitHub repository locator.
    
    This implementation handles repositories hosted on GitHub.
    """
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    async def get_repositories(self) -> RepositoryList:
        """Get user repositories from GitHub API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            response = await self.http_client.get(
                "https://api.github.com/user/repos",
                headers=headers
            )
            
            if response.status_code == 401:
                raise OAuthError("Invalid or expired GitHub access token", "github")
            elif response.status_code != 200:
                logger.error(f"GitHub user repositories failed: {response.status_code} {response.text}")
                raise OAuthError("Failed to retrieve user repositories from GitHub", "github")
            
            repos_data = response.json()
            
            repos_list = []
            for repo_data in repos_data:
                repos_list.append(RepoInfo(
                    id=str(repo_data["id"]),
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    clone_url=repo_data["clone_url"],
                    owner=repo_data["owner"]["login"],
                    private=repo_data.get("private", False),
                    default_branch=repo_data.get("default_branch", "main"),
                    language=repo_data.get("language"),
                    size=repo_data.get("size", 0),
                    updated_at=repo_data.get("updated_at")
                ))
            
            return RepositoryList(repositories=repos_list)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during GitHub repository retrieval: {e}")
            raise OAuthError("Failed to communicate with GitHub", "github")
        except Exception as e:
            if isinstance(e, OAuthError):
                raise
            logger.error(f"Unexpected error during GitHub repository retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "github")
    
    async def get_repository_branches(self, owner: str, repo: str) -> RepositoryBranchesResponse:
        """Get branches from GitHub repository with pagination support."""
        try:
            # First get default branch
            repo_response = await self.http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
            )
            
            if repo_response.status_code == 401:
                raise OAuthError("Invalid or expired GitHub access token", "github")
            elif repo_response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found")
            elif repo_response.status_code != 200:
                raise OAuthError("Failed to retrieve repository info from GitHub", "github")
            
            repo_data = repo_response.json()
            default_branch = repo_data.get("default_branch", "main")
            
            # Get all branches with pagination support
            all_branches = []
            page = 1
            per_page = 100  # GitHub's maximum per_page value
            
            while True:
                branches_response = await self.http_client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/branches",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "X-GitHub-Api-Version": "2022-11-28"
                    },
                    params={
                        "per_page": per_page,
                        "page": page
                    }
                )
                
                if branches_response.status_code != 200:
                    logger.error(f"Failed to get branches: {branches_response.status_code}")
                    # Return just the default branch if we can't get branches
                    if not all_branches:
                        return RepositoryBranchesResponse(
                            branches=[BranchInfo(name=default_branch, is_default=True)],
                            default_branch=default_branch
                        )
                    break
                
                branches_data = branches_response.json()
                if not branches_data:
                    break
                
                all_branches.extend(branches_data)
                
                # Check if there are more pages
                if len(branches_data) < per_page:
                    break
                
                page += 1
            
            branches = [
                BranchInfo(
                    name=branch["name"],
                    is_default=(branch["name"] == default_branch)
                )
                for branch in all_branches
            ]
            
            return RepositoryBranchesResponse(
                branches=branches,
                default_branch=default_branch
            )
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during GitHub branch retrieval: {e}")
            raise OAuthError("Failed to communicate with GitHub", "github")
        except Exception as e:
            if isinstance(e, (OAuthError, ValueError)):
                raise
            logger.error(f"Unexpected error during GitHub branch retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "github")
    
    async def check_existing_pull_request(
        self,
        owner: str,
        repo: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> PullRequestResult:
        """
        Check if a pull request already exists for the given branch.

        Args:
            owner: Repository owner
            repo: Repository name
            head_branch: Source branch for the PR
            base_branch: Target branch (default: main)

        Returns:
            PullRequestResult: Result with existing PR info if found
        """
        try:
            logger.info(f"Checking for existing PR from {head_branch} to {base_branch}")

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            # Check for existing PRs with the same head and base
            params = {
                "head": f"{owner}:{head_branch}",
                "base": base_branch,
                "state": "open"
            }

            response = await self.http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                prs = response.json()
                if prs:
                    # PR already exists
                    pr_info = prs[0]  # Get the first matching PR
                    logger.info(f"Found existing PR #{pr_info['number']}: {pr_info['html_url']}")
                    return PullRequestResult(
                        success=True,
                        pr_number=pr_info["number"],
                        pr_url=pr_info["html_url"],
                        pr_id=pr_info["id"],
                        data=pr_info
                    )
                else:
                    # No existing PR found
                    logger.info(f"No existing PR found for {head_branch} -> {base_branch}")
                    return PullRequestResult(
                        success=False,
                        error="No existing PR found"
                    )
            else:
                error_msg = f"Failed to check for existing PRs: {response.status_code} {response.text}"
                logger.error(error_msg)
                return PullRequestResult(
                    success=False,
                    error=error_msg
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during PR check: {e}")
            return PullRequestResult(
                success=False,
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during PR check: {e}")
            return PullRequestResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        head_branch: str,
        title: str,
        body: str = "",
        base_branch: str = "main",
        draft: bool = False
    ) -> PullRequestResult:
        """
        Create a pull request via GitHub API.

        Args:
            owner: Repository owner
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
            logger.info(f"Creating pull request: {title}")

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            pr_data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch,
                "draft": draft,
                "maintainer_can_modify": True
            }

            response = await self.http_client.post(
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                headers=headers,
                json=pr_data
            )

            if response.status_code == 201:
                pr_info = response.json()
                logger.info(f"Successfully created PR #{pr_info['number']}: {pr_info['html_url']}")
                return PullRequestResult(
                    success=True,
                    pr_number=pr_info["number"],
                    pr_url=pr_info["html_url"],
                    pr_id=pr_info["id"],
                    data=pr_info
                )
            else:
                error_msg = f"PR creation failed: {response.status_code} {response.text}"
                logger.error(error_msg)
                return PullRequestResult(
                    success=False,
                    error=error_msg
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during PR creation: {e}")
            return PullRequestResult(
                success=False,
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during PR creation: {e}")
            return PullRequestResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )