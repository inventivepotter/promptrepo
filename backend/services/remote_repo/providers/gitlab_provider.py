"""
GitLab Repository Provider

This module implements the IRemoteRepo interface for GitLab repositories.
"""

import httpx
import logging

from services.remote_repo.remote_repo_interface import IRemoteRepo
from services.remote_repo.models import RepoInfo, RepositoryList, BranchInfo, RepositoryBranchesResponse
from services.oauth.models import OAuthError

logger = logging.getLogger(__name__)


class GitLabRepoLocator(IRemoteRepo):
    """
    GitLab repository locator.
    
    This implementation handles repositories hosted on GitLab.
    """
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    async def get_repositories(self) -> RepositoryList:
        """Get user repositories from GitLab API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = await self.http_client.get(
                "https://gitlab.com/api/v4/projects?membership=true",
                headers=headers
            )
            
            if response.status_code == 401:
                raise OAuthError("Invalid or expired GitLab access token", "gitlab")
            elif response.status_code != 200:
                logger.error(f"GitLab user repositories failed: {response.status_code} {response.text}")
                raise OAuthError("Failed to retrieve user repositories from GitLab", "gitlab")
            
            repos_data = response.json()
            
            repos_list = []
            for repo_data in repos_data:
                owner, _ = repo_data["path_with_namespace"].split("/", 1)
                repos_list.append(RepoInfo(
                    id=str(repo_data["id"]),
                    name=repo_data["name"],
                    full_name=repo_data["path_with_namespace"],
                    clone_url=repo_data["http_url_to_repo"],
                    owner=owner,
                    private=not repo_data.get("public", True),
                    default_branch=repo_data.get("default_branch", "main"),
                    language=repo_data.get("tag_list"),
                    size=repo_data.get("statistics", {}).get("repository_size", 0) // 1024,
                    updated_at=repo_data.get("last_activity_at")
                ))
            
            return RepositoryList(repositories=repos_list)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during GitLab repository retrieval: {e}")
            raise OAuthError("Failed to communicate with GitLab", "gitlab")
        except Exception as e:
            if isinstance(e, OAuthError):
                raise
            logger.error(f"Unexpected error during GitLab repository retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "gitlab")
    
    async def get_repository_branches(self, owner: str, repo: str) -> RepositoryBranchesResponse:
        """Get branches from GitLab repository."""
        try:
            # GitLab uses URL-encoded project paths
            project_path = f"{owner}/{repo}".replace("/", "%2F")
            
            # First get default branch
            repo_response = await self.http_client.get(
                f"https://gitlab.com/api/v4/projects/{project_path}",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            if repo_response.status_code == 401:
                raise OAuthError("Invalid or expired GitLab access token", "gitlab")
            elif repo_response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found")
            elif repo_response.status_code != 200:
                raise OAuthError("Failed to retrieve repository info from GitLab", "gitlab")
            
            repo_data = repo_response.json()
            default_branch = repo_data.get("default_branch", "main")
            
            # Get all branches
            branches_response = await self.http_client.get(
                f"https://gitlab.com/api/v4/projects/{project_path}/repository/branches",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
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
            logger.error(f"HTTP error during GitLab branch retrieval: {e}")
            raise OAuthError("Failed to communicate with GitLab", "gitlab")
        except Exception as e:
            if isinstance(e, (OAuthError, ValueError)):
                raise
            logger.error(f"Unexpected error during GitLab branch retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "gitlab")