"""
Interface for Prompt Service following Interface Segregation Principle (ISP).

This interface defines the contract that all prompt service implementations
must follow, supporting both individual and organization hosting types.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from .models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    PromptList,
    PromptSearchParams,
    PromptFile
)


class IPromptService(ABC):
    """
    Abstract base class defining the interface for prompt service operations.
    
    This interface supports:
    - CRUD operations for prompts
    - Repository scanning and discovery
    - User-scoped operations in organization mode
    - Both individual and organization hosting types
    """
    
    @abstractmethod
    async def create_prompt(
        self,
        user_id: str,
        prompt_data: PromptCreate
    ) -> Prompt:
        """
        Create a new prompt in the specified repository.
        
        Args:
            user_id: ID of the user creating the prompt
            prompt_data: Data for creating the prompt
            
        Returns:
            Created Prompt object
            
        Raises:
            ValueError: If repository doesn't exist or user lacks permission
        """
        pass
    
    @abstractmethod
    async def get_prompt(
        self,
        user_id: str,
        prompt_id: str
    ) -> Optional[Prompt]:
        """
        Get a single prompt by ID.
        
        Args:
            user_id: ID of the user requesting the prompt
            prompt_id: ID of the prompt to retrieve
            
        Returns:
            Prompt object if found and user has access, None otherwise
        """
        pass
    
    @abstractmethod
    async def update_prompt(
        self,
        user_id: str,
        prompt_id: str,
        prompt_data: PromptUpdate
    ) -> Optional[Prompt]:
        """
        Update an existing prompt.
        
        Args:
            user_id: ID of the user updating the prompt
            prompt_id: ID of the prompt to update
            prompt_data: Updated data for the prompt
            
        Returns:
            Updated Prompt object if successful, None if not found
            
        Raises:
            ValueError: If user lacks permission to update
        """
        pass
    
    @abstractmethod
    async def delete_prompt(
        self,
        user_id: str,
        prompt_id: str
    ) -> bool:
        """
        Delete a prompt.
        
        Args:
            user_id: ID of the user deleting the prompt
            prompt_id: ID of the prompt to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            ValueError: If user lacks permission to delete
        """
        pass
    
    @abstractmethod
    async def list_prompts(
        self,
        user_id: str,
        search_params: Optional[PromptSearchParams] = None
    ) -> PromptList:
        """
        List prompts accessible to the user with optional filtering.
        
        Args:
            user_id: ID of the user requesting prompts
            search_params: Optional search/filter parameters
            
        Returns:
            PromptList containing filtered prompts
        """
        pass
    
    @abstractmethod
    async def list_repository_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[Prompt]:
        """
        List all prompts in a specific repository.
        
        Args:
            user_id: ID of the user requesting prompts
            repo_name: Name of the repository
            
        Returns:
            List of Prompt objects from the repository
            
        Raises:
            ValueError: If repository doesn't exist or user lacks access
        """
        pass
    
    @abstractmethod
    async def discover_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[PromptFile]:
        """
        Discover prompt files in a repository by scanning for YAML/YML files.
        
        Args:
            user_id: ID of the user performing discovery
            repo_name: Name of the repository to scan
            
        Returns:
            List of PromptFile objects found in the repository
            
        Raises:
            ValueError: If repository doesn't exist or user lacks access
        """
        pass
    
    @abstractmethod
    async def clone_repository_for_user(
        self,
        user_id: str,
        repo_name: str,
        clone_url: str,
        branch: Optional[str] = None
    ) -> Path:
        """
        Clone a repository to the appropriate path based on hosting type.
        
        For individual hosting: uses local_repo_path
        For organization hosting: uses multi_user_repo_path with user scoping
        
        Args:
            user_id: ID of the user cloning the repository
            repo_name: Name of the repository
            clone_url: Git clone URL for the repository
            branch: Optional branch to checkout (defaults to main/master)
            
        Returns:
            Path to the cloned repository
            
        Raises:
            ValueError: If cloning fails or user lacks permission
        """
        pass
    
    @abstractmethod
    async def sync_repository_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> int:
        """
        Sync prompts from a repository by discovering and storing them.
        
        This method:
        1. Discovers all prompt files in the repository
        2. Updates or creates prompt records
        3. Removes prompts no longer in the repository
        
        Args:
            user_id: ID of the user syncing prompts
            repo_name: Name of the repository to sync
            
        Returns:
            Number of prompts synchronized
            
        Raises:
            ValueError: If repository doesn't exist or sync fails
        """
        pass