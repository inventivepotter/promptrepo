"""
Abstract base class for configuration strategies.
Implements the Strategy Pattern for hosting type configurations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Session
from services.config.models import AppConfig
from services.config.models import HostingConfig, OAuthConfig, LLMConfig, RepoConfig

if TYPE_CHECKING:
    from services.remote_repo.remote_repo_service import RemoteRepoService


class IConfig(ABC):
    """
    Abstract base class for all configuration strategies.
    Defines the interface that all hosting type configurations must implement.
    """
    
    @abstractmethod
    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        """
        Set OAuth configurations in environment variables.

        Args:
            oauth_configs: List of OAuth configurations

        Returns:
            List[OAuthConfig]: Updated OAuth configurations
        """
        pass

    @abstractmethod
    def set_llm_configs(self, db: Session, user_id: str, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        """
        Set LLM configuration in environment variables.
        
        Args:
            llm_configs: LLM configuration as a list of LLMConfig objects

        Returns:
            List[LLMConfig]: Updated LLM configuration
        """
        pass

    @abstractmethod
    def set_repo_configs(self, db: Session, user_id: str, repo_configs: List[RepoConfig], remote_repo_service: Optional['RemoteRepoService'] = None) -> List[RepoConfig] | None:
        """
        Set repository configuration for a user.

        Args:
            db: Database session
            user_id: The ID of the user to set the configuration for.
            repo_configs: Repository configuration as a list of RepoConfig objects
            remote_repo_service: Optional RepoLocatorService for cloning

        Returns:
            List[RepoConfig]: Updated repository configuration
        """
        pass
    
    @abstractmethod
    def get_hosting_config(self) -> HostingConfig:
        """
        Get hosting type.
        
        Returns:
            HostingConfig: The hosting type
        """
        pass
    
    @abstractmethod
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        """
        Get OAuth configurations.
        
        Returns:
            List[OAuthConfig]: List of OAuth configurations
        """
        pass
    
    @abstractmethod
    def get_llm_configs(self, db: Session, user_id: str | None) -> List[LLMConfig] | None:
        """
        Get LLM configuration.
        
        Returns:
            List[LLMConfig]: LLM configuration
        """
        pass

    @abstractmethod
    def get_repo_configs(self, db: Session, user_id: str) -> List[RepoConfig] | None:
        """
        Get repository configuration for a user.

        Args:
            db: Database session
            user_id: The ID of the user to get the configuration for.

        Returns:
            List[RepoConfig]: Repository configuration
        """
        pass
