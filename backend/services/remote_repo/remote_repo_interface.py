"""
Remote Repository Interface

This module defines the abstract base class for remote repository providers,
ensuring all provider implementations follow a consistent interface.
"""

from abc import ABC, abstractmethod
from services.remote_repo.models import RepositoryList, RepositoryBranchesResponse


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