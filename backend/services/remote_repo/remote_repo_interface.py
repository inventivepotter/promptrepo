"""
Remote Repository Interface

This module defines the abstract base class for remote repository providers,
ensuring all provider implementations follow a consistent interface.
"""

from abc import ABC, abstractmethod
from services.remote_repo.models import RepositoryList, RepositoryBranchesResponse, PullRequestInfo, PullRequestResult


class IRemoteRepo(ABC):
    """
    Abstract base class for remote repository providers.
    
    This interface defines the contract that all remote repo provider
    implementations must follow.
    """
    
    @abstractmethod
    async def get_repositories(self) -> RepositoryList:
        """Get list of available repositories"""
        pass
    
    @abstractmethod
    async def get_repository_branches(self, owner: str, repo: str) -> RepositoryBranchesResponse:
        """Get branches for a specific repository"""
        pass
    
    @abstractmethod
    async def check_existing_pull_request(
        self,
        owner: str,
        repo: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> PullRequestResult:
        """Check if a pull request already exists for the given branch"""
        pass
    
    @abstractmethod
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
        """Create a pull request"""
        pass