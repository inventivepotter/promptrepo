from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathlib import Path
from pydantic import BaseModel
import httpx
from settings.base_settings import Settings
from services.config.models import HostingType
from services.config.config_interface import IConfig

class RepoInfo(BaseModel):
    name: str
    full_name: str
    clone_url: str
    owner: str
    private: bool = False
    default_branch: str = "main"
    language: Optional[str] = None
    size: int = 0
    updated_at: Optional[str] = None


class IRepoLocator(ABC):
    @abstractmethod
    async def get_repositories(self) -> Dict[str, str]:
        """Get list of available repositories"""
        pass


class LocalRepoLocator(IRepoLocator):
    def __init__(self):
        self.base_path = Path(Settings.local_repo_path)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

    async def get_repositories(self) -> Dict[str, str]:
        repos = {}
        for item in self.base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repos[item.name] = str(item.resolve())
        return repos


class RepoLocatorService:
    """
    Service class for locating repositories using different strategies.
    Uses constructor injection for config service and OAuth service following SOLID principles.
    """
    def __init__(self, config_service: IConfig, git_provider_service):
        self.config_service = config_service
        self.git_provider_service = git_provider_service
    
    async def get_repositories(
        self,
        oauth_provider: Optional[str] = None,
        username: Optional[str] = None,
        oauth_token: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get repositories using the configured locator strategy.
        
        Args:
            oauth_provider: OAuth provider name ('github', 'gitlab', 'bitbucket')
            username: Username for OAuth providers (required for organization hosting)
            oauth_token: OAuth token for authentication (required for organization hosting)

        Returns:
            Dict[str, str]: Dictionary mapping repository names to their paths/URLs
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            # Use local repository locator
            locator = LocalRepoLocator()
            return await locator.get_repositories()
        elif hosting_config.type == HostingType.ORGANIZATION:
            # Use OAuth service to get repositories from user's provider
            if not oauth_provider or not oauth_token:
                raise ValueError("OAuth provider and token are required for Organization hosting type")
            
            return await self.git_provider_service.get_user_repositories(oauth_provider, oauth_token)
        else:
            raise ValueError(f"Unsupported hosting type: {hosting_config.type}")
