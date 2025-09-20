"""
Abstract base class for configuration strategies.
Implements the Strategy Pattern for hosting type configurations.
"""

from abc import ABC, abstractmethod
from typing import List
from services.config.models import AppConfig
from services.config.models import HostingConfig, OAuthConfig, LLMConfig, RepoConfig


class IConfig(ABC):
    """
    Abstract base class for all configuration strategies.
    Defines the interface that all hosting type configurations must implement.
    """
    
    @abstractmethod
    def set_hosting_type(self) -> HostingConfig:
        """
        Set hosting type in environment variables.

        Returns:
            HostingConfig: Updated hosting configuration
        """
        pass
    
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
    def set_llm_configs(self, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        """
        Set LLM configuration in environment variables.
        
        Args:
            llm_configs: LLM configuration as a list of LLMConfig objects

        Returns:
            List[LLMConfig]: Updated LLM configuration
        """
        pass

    @abstractmethod
    def set_repo_configs(self, repo_configs: List[RepoConfig]) -> List[RepoConfig] | None:
        """
        Set repository configuration in environment variables.

        Args:
            repo_configs: Repository configuration as a list of RepoConfig objects

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
    def get_llm_configs(self) -> List[LLMConfig] | None:
        """
        Get LLM configuration.
        
        Returns:
            List[LLMConfig]: LLM configuration
        """
        pass

    @abstractmethod
    def get_repo_configs(self) -> List[RepoConfig] | None:
        """
        Get repository configuration.

        Returns:
            List[RepoConfig]: Repository configuration
        """
        pass

    def get_config(self) -> AppConfig:
        """Get the current configuration object based on the hosting type."""
        return AppConfig(
            hostingConfig=self.get_hosting_config(),
            oauthConfigs=self.get_oauth_configs(),
            llmConfigs=self.get_llm_configs(),
            repoConfigs=self.get_repo_configs()
        )