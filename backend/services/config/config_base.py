"""
Abstract base class for configuration strategies.
Implements the Strategy Pattern for hosting type configurations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from schemas.config import AppConfig
from dotenv import load_dotenv
from schemas.config import HostingConfig, OAuthConfig, LLMConfig, RepoConfig


class ConfigBase(ABC):
    """
    Abstract base class for all configuration strategies.
    Defines the interface that all hosting type configurations must implement.
    """
    
    def __init__(self):
        """
        Initialize strategy with the application configuration.
        
        Args:
            config: The application configuration object
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate if the configuration is complete for this hosting type.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        pass
    
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
    def set_llm_config(self, llm_config_json: Dict[str, str]) -> LLMConfig | None:
        """
        Set LLM configuration in environment variables.
        
        Args:
            llm_config_json: LLM configuration as a JSON dictionary

        Returns:
            LLMConfig: Updated LLM configuration
        """
        pass
    
    @abstractmethod
    def get_hosting_config(self) -> HostingConfig | None:
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
    def get_llm_config(self) -> LLMConfig | None:
        """
        Get LLM configuration.
        
        Returns:
            LLMConfig: LLM configuration
        """
        pass
    
    @abstractmethod
    def is_oauth_required(self) -> bool:
        """
        Check if OAuth configuration is required for this hosting type.
        
        Returns:
            bool: True if OAuth is required, False otherwise
        """
        pass
    
    @abstractmethod
    def is_llm_required(self) -> bool:
        """
        Check if LLM configuration is required for this hosting type.
        
        Returns:
            bool: True if LLM configs are required, False otherwise
        """
        pass
    
    # def reload_settings(self) -> None:
    #     """
    #     Reload all settings from environment variables and .env file.
    #     """
    #     # Reload environment variables from .env file
    #     load_dotenv(override=True)
        
    #     # Reinitialize all sub-settings to pick up new values
    #     self._hosting_config = HostingConfig()
    #     self._auth_config = OAuthConfig()
    #     self._llm_config = LLMConfig()
    #     self._repo_config = RepoConfig()

    @abstractmethod
    def get_config(self) -> AppConfig:
        """
        Get the current configuration object based on the hosting type.

        Returns:
            AppConfig: The current configuration
        """
        pass