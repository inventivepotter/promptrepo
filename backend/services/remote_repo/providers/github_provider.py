"""
GitHub Repository Provider

This module implements the IRemoteRepo interface for GitHub repositories.
"""

import httpx
import logging

from services.remote_repo.remote_repo_interface import IRemoteRepo
from services.remote_repo.models import RepoInfo, RepositoryList, BranchInfo, RepositoryBranchesResponse
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
        """Get branches from GitHub repository."""
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
            
            # Get all branches
            branches_response = await self.http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/branches",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
            )
            
            if branches_response.status_code != 200:
                logger.error(f"Failed to get branches: {branches_response.status_code}")
                # Return just the default branch if we can't get branches
                return RepositoryBranchesResponse(
                    branches=[BranchInfo(name=default_branch, is_default=True)],
                    default_branch=default_branch
                )
            
            branches_data = branches_response.json()
            branches = [
                BranchInfo(
                    name=branch["name"],
                    is_default=(branch["name"] == default_branch)
                )
                for branch in branches_data
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