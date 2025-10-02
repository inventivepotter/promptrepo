"""
Interface for Prompt Service following Interface Segregation Principle (ISP).

This interface defines the contract that all prompt service implementations
must follow, supporting both individual and organization hosting types.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from .models import (
    PromptMeta,
    PromptData,
    PromptDataUpdate
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
        repo_name: str,
        file_path: str,
        prompt_data: PromptData
    ) -> PromptMeta:
        """
        Create a new prompt in the specified repository.
        
        Args:
            user_id: ID of the user creating the prompt
            repo_name: Repository name where prompt will be stored
            file_path: File path within the repository
            prompt_data: Data for creating the prompt
            
        Returns:
            Created PromptMeta object
            
        Raises:
            ValueError: If repository doesn't exist or user lacks permission
        """
        pass
    
    @abstractmethod
    async def get_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
    ) -> Optional[PromptMeta]:
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
        repo_name: str,
        file_path: str,
        prompt_data: PromptDataUpdate
    ) -> Optional[PromptMeta]:
        """
        Update an existing prompt.
        
        Args:
            user_id: ID of the user updating the prompt
            prompt_id: ID of the prompt to update
            prompt_data: Updated data for the prompt
            
        Returns:
            Updated PromptMeta object if successful, None if not found
            
        Raises:
            ValueError: If user lacks permission to update
        """
        pass
    
    @abstractmethod
    async def delete_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
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
    async def discover_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[PromptMeta]:
        """
        Discover prompt files in a repository by scanning for YAML/YML files.
        
        Args:
            user_id: ID of the user performing discovery
            repo_name: Name of the repository to scan
            
        Returns:
            List of PromptMeta objects found in the repository
            
        Raises:
            NotFoundException: If repository doesn't exist or user lacks access
        """
        pass
    