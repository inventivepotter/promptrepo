from abc import ABC, abstractmethod
from pathlib import Path
import httpx
import logging
import uuid
from typing import List

from sqlmodel import Session
from settings import settings
from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.oauth.models import OAuthError
from schemas.oauth_provider_enum import OAuthProvider
from database.daos.user.user_dao import UserDAO
from services.auth.session_service import SessionService
from services.repo.models import RepoInfo, RepositoryList
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IRepoLocator(ABC):
    @abstractmethod
    async def get_repositories(self) -> RepositoryList:
        """Get list of available repositories"""
        pass


class LocalRepoLocator(IRepoLocator):
    def __init__(self):
        self.base_path = Path(settings.local_repo_path)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

    async def get_repositories(self) -> RepositoryList:
        repos_list = []
        for item in self.base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repos_list.append(RepoInfo(id=str(uuid.uuid4()), name=item.name, full_name=item.name, clone_url=str(item.resolve()), owner="local"))
        return RepositoryList(repositories=repos_list)


class GitHubRepoLocator(IRepoLocator):
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


class GitLabRepoLocator(IRepoLocator):
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
                    language=repo_data.get("tag_list"), # GitLab might not have a direct 'language' field
                    size=repo_data.get("statistics", {}).get("repository_size", 0) // 1024, # size in KB
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


class BitbucketRepoLocator(IRepoLocator):
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


class BranchInfo(BaseModel):
    """Information about a repository branch"""
    name: str = Field(..., description="Branch name")
    is_default: bool = Field(default=False, description="Whether this is the default branch")


class RepositoryBranchesResponse(BaseModel):
    """Response containing repository branches"""
    branches: List[BranchInfo] = Field(..., description="List of repository branches")
    default_branch: str = Field(..., description="The default branch name")


class RepoLocatorService:
    """
    Service class for locating repositories using different strategies.
    Uses constructor injection for config and auth services following SOLID principles.
    """
    def __init__(self, db: Session, config_service: IConfig, session_service: SessionService):
        self.config_service = config_service
        self.user_dao = UserDAO(db)
        self.session_service = session_service
    
    async def get_repositories(
        self,
        user_id: str
    ) -> RepositoryList:
        """
        Get repositories for a given user based on the configured locator strategy.
        
        Args:
            user_id: The ID of the user to fetch repositories for.

        Returns:
            RepositoryList: A list of repository information.
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            locator = LocalRepoLocator()
            return await locator.get_repositories()
        elif hosting_config.type == HostingType.ORGANIZATION:
            # Fetch necessary data for the user using the auth_service
            # We assume auth_service has a method to get OAuth details.
            # For now, we'll create a placeholder for this logic.
            # In a real scenario, this would call a method on auth_service.
            # user_oauth_details = await self.auth_service.get_user_oauth_details(user_id)
            
            # Placeholder for now - we'll need to implement this method in AuthService
            # For the sake of this diff, we'll raise an error if these are not found.
            # This will be replaced by the actual call to auth_service.
            try:
                user = self.user_dao.get_user_by_id(user_id)
                if not user:
                    raise ValueError(f"User not found for ID: {user_id}")

                latest_session = self.session_service.get_active_session(user_id)
                if not latest_session:
                    raise ValueError(f"No active session found for user ID: {user_id}")

                oauth_provider = user.oauth_provider
                oauth_token = latest_session.oauth_token
                oauth_username = user.oauth_username

            except ValueError as e:
                logger.error(f"Failed to retrieve user or session data: {e}")
                raise
            except Exception as e:
                logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
                raise

            if not oauth_provider or not oauth_token:
                raise ValueError(f"OAuth provider and token not configured for user {user_id}")
            
            locator: IRepoLocator
            if oauth_provider.lower() == "github":
                locator = GitHubRepoLocator(oauth_token)
            elif oauth_provider.lower() == "gitlab":
                locator = GitLabRepoLocator(oauth_token)
            elif oauth_provider.lower() == "bitbucket":
                username = oauth_username
                if not username:
                    raise ValueError(f"OAuth username not configured for user {user_id} with Bitbucket")
                locator = BitbucketRepoLocator(oauth_token, username)
            else:
                raise OAuthError(f"Unsupported provider: {oauth_provider}", oauth_provider)
            
            async with locator:
                return await locator.get_repositories()
        else:
            raise ValueError(f"Unsupported hosting type: {hosting_config.type}")
    
    async def get_repository_branches(
        self,
        user_id: str,
        owner: str,
        repo: str
    ) -> RepositoryBranchesResponse:
        """
        Get branches for a specific repository.
        
        Args:
            user_id: The ID of the user to fetch branches for
            owner: Repository owner/organization
            repo: Repository name
        
        Returns:
            RepositoryBranchesResponse: Branch information for the repository
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            # For local repositories, just return the main branch
            return RepositoryBranchesResponse(
                branches=[BranchInfo(name="main", is_default=True)],
                default_branch="main"
            )
        elif hosting_config.type == HostingType.ORGANIZATION:
            try:
                user = self.user_dao.get_user_by_id(user_id)
                if not user:
                    raise ValueError(f"User not found for ID: {user_id}")

                latest_session = self.session_service.get_active_session(user_id)
                if not latest_session:
                    raise ValueError(f"No active session found for user ID: {user_id}")

                oauth_provider = user.oauth_provider
                oauth_token = latest_session.oauth_token

            except ValueError as e:
                logger.error(f"Failed to retrieve user or session data: {e}")
                raise
            except Exception as e:
                logger.error(f"An unexpected error occurred while fetching OAuth details: {e}")
                raise

            if not oauth_provider or not oauth_token:
                raise ValueError(f"OAuth provider and token not configured for user {user_id}")
            
            if oauth_provider.lower() == "github":
                return await self._get_github_branches(oauth_token, owner, repo)
            elif oauth_provider.lower() == "gitlab":
                return await self._get_gitlab_branches(oauth_token, owner, repo)
            elif oauth_provider.lower() == "bitbucket":
                return await self._get_bitbucket_branches(oauth_token, owner, repo)
            else:
                raise OAuthError(f"Unsupported provider: {oauth_provider}", oauth_provider)
        else:
            raise ValueError(f"Unsupported hosting type: {hosting_config.type}")
    
    async def _get_github_branches(
        self,
        access_token: str,
        owner: str,
        repo: str
    ) -> RepositoryBranchesResponse:
        """Get branches from GitHub repository."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get default branch
                repo_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "X-GitHub-Api-Version": "2022-11-28"
                    }
                )
                
                if repo_response.status_code == 401:
                    raise OAuthError("Invalid or expired GitHub access token", "github")
                elif repo_response.status_code == 404:
                    raise ValueError(f"Repository {owner}/{repo} not found")
                elif repo_response.status_code != 200:
                    raise OAuthError(f"Failed to retrieve repository info from GitHub", "github")
                
                repo_data = repo_response.json()
                default_branch = repo_data.get("default_branch", "main")
                
                # Get all branches
                branches_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/branches",
                    headers={
                        "Authorization": f"Bearer {access_token}",
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
    
    async def _get_gitlab_branches(
        self,
        access_token: str,
        owner: str,
        repo: str
    ) -> RepositoryBranchesResponse:
        """Get branches from GitLab repository."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # GitLab uses URL-encoded project paths
                project_path = f"{owner}/{repo}".replace("/", "%2F")
                
                # First get default branch
                repo_response = await client.get(
                    f"https://gitlab.com/api/v4/projects/{project_path}",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    }
                )
                
                if repo_response.status_code == 401:
                    raise OAuthError("Invalid or expired GitLab access token", "gitlab")
                elif repo_response.status_code == 404:
                    raise ValueError(f"Repository {owner}/{repo} not found")
                elif repo_response.status_code != 200:
                    raise OAuthError(f"Failed to retrieve repository info from GitLab", "gitlab")
                
                repo_data = repo_response.json()
                default_branch = repo_data.get("default_branch", "main")
                
                # Get all branches
                branches_response = await client.get(
                    f"https://gitlab.com/api/v4/projects/{project_path}/repository/branches",
                    headers={
                        "Authorization": f"Bearer {access_token}"
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
    
    async def _get_bitbucket_branches(
        self,
        access_token: str,
        owner: str,
        repo: str
    ) -> RepositoryBranchesResponse:
        """Get branches from Bitbucket repository."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get default branch
                repo_response = await client.get(
                    f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    }
                )
                
                if repo_response.status_code == 401:
                    raise OAuthError("Invalid or expired Bitbucket access token", "bitbucket")
                elif repo_response.status_code == 404:
                    raise ValueError(f"Repository {owner}/{repo} not found")
                elif repo_response.status_code != 200:
                    raise OAuthError(f"Failed to retrieve repository info from Bitbucket", "bitbucket")
                
                repo_data = repo_response.json()
                default_branch = repo_data.get("mainbranch", {}).get("name", "main")
                
                # Get all branches
                branches_response = await client.get(
                    f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}/refs/branches",
                    headers={
                        "Authorization": f"Bearer {access_token}"
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
                    for branch in branches_data.get("values", [])
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
