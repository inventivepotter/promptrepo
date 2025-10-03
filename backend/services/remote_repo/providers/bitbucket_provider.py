"""
Bitbucket Repository Provider

This module implements the IRemoteRepo interface for Bitbucket repositories.
"""

import httpx
import logging

from services.remote_repo.remote_repo_interface import IRemoteRepo
from services.remote_repo.models import RepoInfo, RepositoryList, BranchInfo, RepositoryBranchesResponse
from services.oauth.models import OAuthError

logger = logging.getLogger(__name__)


class BitbucketRepoLocator(IRemoteRepo):
    """
    Bitbucket repository locator.
    
    This implementation handles repositories hosted on Bitbucket.
    """
    
    def __init__(self, access_token: str, username: str):
        self.access_token = access_token
        self.username = username
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    async def get_repositories(self) -> RepositoryList:
        """Get user repositories from Bitbucket API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = await self.http_client.get(
                f"https://api.bitbucket.org/2.0/repositories/{self.username}",
                headers=headers
            )
            
            if response.status_code == 401:
                raise OAuthError("Invalid or expired Bitbucket access token", "bitbucket")
            elif response.status_code != 200:
                logger.error(f"Bitbucket user repositories failed: {response.status_code} {response.text}")
                raise OAuthError("Failed to retrieve user repositories from Bitbucket", "bitbucket")
            
            repos_data = response.json()
            
            repos_list = []
            for repo_data in repos_data.get("values", []):
                clone_links = repo_data.get("links", {}).get("clone", [])
                clone_url = None
                for link in clone_links:
                    if link.get("name") == "https":
                        clone_url = link.get("href")
                        break
                if clone_url:
                    repos_list.append(RepoInfo(
                        id=str(repo_data["uuid"]),
                        name=repo_data["name"],
                        full_name=repo_data["full_name"],
                        clone_url=clone_url,
                        owner=repo_data["owner"]["username"],
                        private=not repo_data.get("is_public", True),
                        default_branch=repo_data.get("mainbranch", {}).get("name", "main"),
                        language=repo_data.get("language"),
                        size=repo_data.get("size", 0),
                        updated_at=repo_data.get("updated_on")
                    ))
            
            return RepositoryList(repositories=repos_list)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during Bitbucket repository retrieval: {e}")
            raise OAuthError("Failed to communicate with Bitbucket", "bitbucket")
        except Exception as e:
            if isinstance(e, OAuthError):
                raise
            logger.error(f"Unexpected error during Bitbucket repository retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "bitbucket")
    
    async def get_repository_branches(self, owner: str, repo: str) -> RepositoryBranchesResponse:
        """Get branches from Bitbucket repository with pagination support."""
        try:
            # First get default branch
            repo_response = await self.http_client.get(
                f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            if repo_response.status_code == 401:
                raise OAuthError("Invalid or expired Bitbucket access token", "bitbucket")
            elif repo_response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found")
            elif repo_response.status_code != 200:
                raise OAuthError("Failed to retrieve repository info from Bitbucket", "bitbucket")
            
            repo_data = repo_response.json()
            default_branch = repo_data.get("mainbranch", {}).get("name", "main")
            
            # Get all branches with pagination support
            all_branches = []
            page = 1
            pagelen = 100  # Bitbucket's maximum pagelen value
            
            while True:
                branches_response = await self.http_client.get(
                    f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}/refs/branches",
                    headers={
                        "Authorization": f"Bearer {self.access_token}"
                    },
                    params={
                        "pagelen": pagelen,
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
                values = branches_data.get("values", [])
                
                if not values:
                    break
                
                all_branches.extend(values)
                
                # Check if there's a next page using Bitbucket's pagination
                if not branches_data.get("next"):
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
            logger.error(f"HTTP error during Bitbucket branch retrieval: {e}")
            raise OAuthError("Failed to communicate with Bitbucket", "bitbucket")
        except Exception as e:
            if isinstance(e, (OAuthError, ValueError)):
                raise
            logger.error(f"Unexpected error during Bitbucket branch retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "bitbucket")