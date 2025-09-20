"""
Abstract base class for configuration strategies.
Implements the Strategy Pattern for hosting type configurations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from schemas.config import AppConfig
from dotenv import load_dotenv
from schemas.config import HostingConfig, OAuthConfig, LLMConfig, RepoConfig


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
    def set_oauth_config(self, github_client_id: str, github_client_secret: str) -> OAuthConfig | None:
        """
        Set OAuth configuration in environment variables.

        Args:
            oauth_config_json: OAuth configuration as a JSON dictionary

        Returns:
            OAuthConfig: Updated OAuth configuration
        """
        pass

    @abstractmethod
    def set_llm_config(self, llm_config: List[LLMConfig]) -> List[LLMConfig] | None:
        """
        Set LLM configuration in environment variables.
        
        Args:
            llm_config: LLM configuration as a list of LLMConfig objects

        Returns:
            LLMConfig: Updated LLM configuration
        """
        pass

    @abstractmethod
    def set_repo_config(self, repo_config: List[RepoConfig]) -> RepoConfig | None:
        """
        Set repository configuration in environment variables.

        Args:
            repo_config: Repository configuration as a list of RepoConfig objects

        Returns:
            RepoConfig: Updated repository configuration
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
    def get_oauth_config(self) -> OAuthConfig | None:
        """
        Get OAuth configuration.
        
        Returns:
            OAuthConfig: OAuth configuration
        """
        pass
    
    @abstractmethod
    def get_llm_config(self) -> List[LLMConfig] | None:
        """
        Get LLM configuration.
        
        Returns:
            List[LLMConfig]: LLM configuration
        """
        pass

    @abstractmethod
    def get_repo_config(self) -> List[RepoConfig] | None:
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
            oauthConfig=self.get_oauth_config(),
            llmConfigs=self.get_llm_config(),
            repoConfig=self.get_repo_config()
        ) 