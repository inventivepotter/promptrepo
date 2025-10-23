"""
GitLab Repository Provider

This module implements the IRemoteRepo interface for GitLab repositories.
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
        """Get branches from GitLab repository with pagination support."""
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
            
            # Get all branches with pagination support
            all_branches = []
            page = 1
            per_page = 100  # GitLab's maximum per_page value
            
            while True:
                branches_response = await self.http_client.get(
                    f"https://gitlab.com/api/v4/projects/{project_path}/repository/branches",
                    headers={
                        "Authorization": f"Bearer {self.access_token}"
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
            logger.error(f"HTTP error during GitLab branch retrieval: {e}")
            raise OAuthError("Failed to communicate with GitLab", "gitlab")
        except Exception as e:
            if isinstance(e, (OAuthError, ValueError)):
                raise
            logger.error(f"Unexpected error during GitLab branch retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "gitlab")
    
    async def check_existing_pull_request(
        self,
        owner: str,
        repo: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> PullRequestResult:
        """
        Check if a merge request already exists for the given branch.

        Args:
            owner: Repository owner
            repo: Repository name
            head_branch: Source branch for the MR
            base_branch: Target branch (default: main)

        Returns:
            PullRequestResult: Result with existing MR info if found
        """
        try:
            logger.info(f"Checking for existing MR from {head_branch} to {base_branch}")

            project_path = f"{owner}/{repo}".replace("/", "%2F")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            # Check for existing MRs with the same source and target branches
            params = {
                "source_branch": head_branch,
                "target_branch": base_branch,
                "state": "opened"
            }

            response = await self.http_client.get(
                f"https://gitlab.com/api/v4/projects/{project_path}/merge_requests",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                mrs = response.json()
                if mrs:
                    # MR already exists
                    mr_info = mrs[0]  # Get the first matching MR
                    logger.info(f"Found existing MR #{mr_info['iid']}: {mr_info['web_url']}")
                    return PullRequestResult(
                        success=True,
                        pr_number=mr_info["iid"],
                        pr_url=mr_info["web_url"],
                        pr_id=mr_info["id"],
                        data=mr_info
                    )
                else:
                    logger.info(f"No existing MR found for {head_branch} -> {base_branch}")
                    return PullRequestResult(
                        success=False,
                        error="No existing MR found"
                    )
            else:
                error_msg = f"Failed to check for existing MRs: {response.status_code} {response.text}"
                logger.error(error_msg)
                return PullRequestResult(
                    success=False,
                    error=error_msg
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during MR check: {e}")
            return PullRequestResult(
                success=False,
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during MR check: {e}")
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
        Create a merge request via GitLab API.

        Args:
            owner: Repository owner
            repo: Repository name
            head_branch: Source branch for the MR
            title: Merge request title
            body: Merge request description
            base_branch: Target branch (default: main)
            draft: Create as draft MR (default: False)

        Returns:
            PullRequestResult: Result of the operation
        """
        try:
            logger.info(f"Creating merge request: {title}")

            project_path = f"{owner}/{repo}".replace("/", "%2F")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            # Prepend "Draft: " to title if draft
            mr_title = f"Draft: {title}" if draft else title

            mr_data = {
                "source_branch": head_branch,
                "target_branch": base_branch,
                "title": mr_title,
                "description": body,
                "remove_source_branch": False
            }

            response = await self.http_client.post(
                f"https://gitlab.com/api/v4/projects/{project_path}/merge_requests",
                headers=headers,
                json=mr_data
            )

            if response.status_code == 201:
                mr_info = response.json()
                logger.info(f"Successfully created MR #{mr_info['iid']}: {mr_info['web_url']}")
                return PullRequestResult(
                    success=True,
                    pr_number=mr_info["iid"],
                    pr_url=mr_info["web_url"],
                    pr_id=mr_info["id"],
                    data=mr_info
                )
            else:
                error_msg = f"MR creation failed: {response.status_code} {response.text}"
                logger.error(error_msg)
                return PullRequestResult(
                    success=False,
                    error=error_msg
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during MR creation: {e}")
            return PullRequestResult(
                success=False,
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during MR creation: {e}")
            return PullRequestResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )