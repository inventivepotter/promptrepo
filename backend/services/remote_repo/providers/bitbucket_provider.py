"""
Bitbucket Repository Provider

This module implements the IRemoteRepo interface for Bitbucket repositories.
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
                "Authorization": f"Bearer {self.access_token}"
            }

            # Check for existing PRs with the same source and destination branches
            params = {
                "state": "OPEN"
            }

            response = await self.http_client.get(
                f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}/pullrequests",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                prs_data = response.json()
                prs = prs_data.get("values", [])
                
                # Filter PRs by source and destination branches
                for pr in prs:
                    source = pr.get("source", {}).get("branch", {}).get("name")
                    destination = pr.get("destination", {}).get("branch", {}).get("name")
                    
                    if source == head_branch and destination == base_branch:
                        # PR already exists
                        logger.info(f"Found existing PR #{pr['id']}: {pr['links']['html']['href']}")
                        return PullRequestResult(
                            success=True,
                            pr_number=pr["id"],
                            pr_url=pr["links"]["html"]["href"],
                            pr_id=pr["id"],
                            data=pr
                        )
                
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
        Create a pull request via Bitbucket API.

        Args:
            owner: Repository owner
            repo: Repository name
            head_branch: Source branch for the PR
            title: Pull request title
            body: Pull request description
            base_branch: Target branch (default: main)
            draft: Create as draft PR (default: False) - Note: Bitbucket doesn't support draft PRs natively

        Returns:
            PullRequestResult: Result of the operation
        """
        try:
            logger.info(f"Creating pull request: {title}")

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            pr_data = {
                "title": title,
                "description": body,
                "source": {
                    "branch": {
                        "name": head_branch
                    }
                },
                "destination": {
                    "branch": {
                        "name": base_branch
                    }
                },
                "close_source_branch": False
            }

            response = await self.http_client.post(
                f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}/pullrequests",
                headers=headers,
                json=pr_data
            )

            if response.status_code == 201:
                pr_info = response.json()
                logger.info(f"Successfully created PR #{pr_info['id']}: {pr_info['links']['html']['href']}")
                return PullRequestResult(
                    success=True,
                    pr_number=pr_info["id"],
                    pr_url=pr_info["links"]["html"]["href"],
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